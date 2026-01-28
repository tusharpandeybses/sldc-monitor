import requests
import os
from datetime import datetime

URL = "https://www.delhisldc.org/Filesshared/api_response_28-01-2026.json"
NEW_FILE = "Schedule_New/Delhi_SLDC_DC.json"

os.makedirs("Schedule_New", exist_ok=True)

print("⬇ Downloading SLDC schedule...")
resp = requests.get(URL, timeout=30)
resp.raise_for_status()

with open(NEW_FILE, "w") as f:
    f.write(resp.text)

print("✅ New schedule saved at", datetime.now())

