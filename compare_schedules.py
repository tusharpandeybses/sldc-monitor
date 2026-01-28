import json, psycopg2, os
from datetime import datetime

DB_URL = os.getenv("DATABASE_URL")

NEW = "Schedule_New/Delhi_SLDC_DC.json"
OLD = "Schedule_old/Delhi_SLDC_DC.json"

if not os.path.exists(OLD):
    print("No old schedule yet")
    exit()

with open(NEW) as f: new = json.load(f)
with open(OLD) as f: old = json.load(f)

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS schedule_changes(
id SERIAL PRIMARY KEY,
time_detected TIMESTAMP,
revision INT,
plant TEXT,
block INT,
old_mw FLOAT,
new_mw FLOAT,
delta_mw FLOAT
)
""")

rev = new.get("RevisionNo",0)

for plant in new["EntitlementData"]:
    for blk in range(1,97):
        n = new["EntitlementData"][plant].get(str(blk),0)
        o = old["EntitlementData"].get(plant,{}).get(str(blk),0)
        if n != o:
            cur.execute("""
            INSERT INTO schedule_changes
            VALUES (DEFAULT,%s,%s,%s,%s,%s,%s,%s)
            """,(datetime.utcnow(),rev,plant,blk,o,n,n-o))

conn.commit()
conn.close()
print("✅ Changes stored")
