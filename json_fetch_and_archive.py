
import requests, json, os, shutil
from datetime import datetime

URL = "https://www.delhisldc.org/Filesshared/api_response_28-01-2026.json"

NEW_DIR = "Schedule_New"
OLD_DIR = "Schedule_old"

os.makedirs(NEW_DIR, exist_ok=True)
os.makedirs(OLD_DIR, exist_ok=True)

if os.path.exists(f"{NEW_DIR}/Delhi_SLDC_DC.json"):
    shutil.move(f"{NEW_DIR}/Delhi_SLDC_DC.json",
                f"{OLD_DIR}/Delhi_SLDC_DC.json")

print("⬇ Downloading SLDC JSON")
data = requests.get(URL).json()

with open(f"{NEW_DIR}/Delhi_SLDC_DC.json","w") as f:
    json.dump(data,f)

rev = data.get("RevisionNo","NA")
print(f"✅ New schedule saved | Revision {rev}")
