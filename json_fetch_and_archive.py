import os
import json
import ssl
import shutil
import urllib.request
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

URL = "https://www.delhisldc.org/Filesshared/api_response_{date}.json"
FILENAME = "Delhi_SLDC_DC.json"

OLD_DIR = "schedule_old"
NEW_DIR = "schedule_new"

os.makedirs(OLD_DIR, exist_ok=True)
os.makedirs(NEW_DIR, exist_ok=True)

def download_json():
    date = datetime.now().strftime("%d-%m-%Y")
    url = URL.format(date=date)
    print(f"⬇ Downloading {url}")
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    data = download_json()

    new_path = os.path.join(NEW_DIR, FILENAME)
    old_path = os.path.join(OLD_DIR, FILENAME)

    if os.path.exists(new_path):
        shutil.copy(new_path, old_path)
        print("🔁 NEW → OLD")

    with open(new_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    rev = data["ResponseBody"].get("FullSchdRevisionNo")
    print(f"✅ NEW schedule saved | Revision {rev}")

if __name__ == "__main__":
    main()

