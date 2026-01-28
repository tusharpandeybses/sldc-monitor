import json
import csv
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# --- load .env safely ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

OLD_JSON = "schedule_old/Delhi_SLDC_DC.json"
NEW_JSON = "schedule_new/Delhi_SLDC_DC.json"
PLANT_MASTER = "plant_master.csv"
MW_LIMIT = 1.0

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

def load_bypl_plants():
    plants = {}
    with open(PLANT_MASTER, encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        next(rd, None)
        for r in rd:
            if len(r) >= 6 and r[0] == "Entitlement_Matrix.csv" and r[4]:
                plants[r[4].strip()] = r[5].strip() or r[4].strip()
    return plants

def extract_entitlement(path, plant_map):
    with open(path) as f:
        body = json.load(f)["ResponseBody"]

    out = {}
    for g in body.get("GroupWiseDataList", []):
        for e in g.get("EntitlementList", []):
            seller = (e.get("SellerUnitAcronym") or e.get("SellerAcronym") or "").strip()
            if seller not in plant_map:
                continue

            ent = e.get("EntitlementData")
            if not isinstance(ent, dict):
                continue

            mw_list = None
            for v in ent.values():
                if isinstance(v, dict):
                    for arr in v.values():
                        if isinstance(arr, list) and len(arr) >= 96:
                            mw_list = arr
                            break
                if mw_list:
                    break

            if not mw_list:
                continue

            plant = plant_map[seller]
            out.setdefault(plant, {})
            for i, mw in enumerate(mw_list, 1):
                try:
                    out[plant][i] = float(mw)
                except:
                    pass
    return out

def main():
    if not os.path.exists(OLD_JSON):
        print("ℹ First run — no OLD schedule")
        return

    plants = load_bypl_plants()
    old = extract_entitlement(OLD_JSON, plants)
    new = extract_entitlement(NEW_JSON, plants)

    with open(OLD_JSON) as f:
        old_rev = json.load(f)["ResponseBody"].get("FullSchdRevisionNo")
    with open(NEW_JSON) as f:
        new_rev = json.load(f)["ResponseBody"].get("FullSchdRevisionNo")

    print(f"\n🔔 BYPL Changes (Rev {old_rev} → {new_rev})\n")

    count = 0
    for plant in new:
        for block in new[plant]:
            if plant in old and block in old[plant]:
                diff = new[plant][block] - old[plant][block]
                if abs(diff) >= MW_LIMIT:
                    count += 1
                    print(
                        f"{plant} | Block {block:02d} | "
                        f"{old[plant][block]:.2f} → {new[plant][block]:.2f} (Δ {diff:+.2f})"
                    )

                    cur.execute("""
                        INSERT INTO schedule_changes
                        (old_revision, new_revision, plant, block, old_mw, new_mw, delta_mw)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        old_rev, new_rev, plant, block,
                        old[plant][block], new[plant][block], diff
                    ))

    conn.commit()
    print(f"\n✅ Stored changes: {count}")

if __name__ == "__main__":
    main()
