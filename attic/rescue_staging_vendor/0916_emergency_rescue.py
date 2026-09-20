#!/data/data/com.termux/files/usr/bin/env python3
"""EMERGENCY DATA RESCUE v1.0 — Fixed Path"""
import os, zipfile
from datetime import datetime

SOURCE = os.path.expanduser("~/AERO_ROOT")
BACKUP = "/sdcard/Backup_Science"
ts = datetime.now().strftime("%Y%m%d_%H%M")
ZIPNAME = f"AeroCement_Rescue_{ts}.zip"
ZIPPATH = os.path.join(BACKUP, ZIPNAME)

os.makedirs(BACKUP, exist_ok=True)
print("🚨 EMERGENCY RESCUE...")
print(f"📦 Source: {SOURCE}")
print(f"💾 Target: {ZIPPATH}")

try:
    with zipfile.ZipFile(ZIPPATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SOURCE):
            for f in files:
                fp = os.path.join(root, f)
                arc = os.path.relpath(fp, SOURCE)
                zf.write(fp, arc)
    mb = os.path.getsize(ZIPPATH) / (1024*1024)
    print(f"✅ DONE! {mb:.2f} MB saved to {ZIPPATH}")
except Exception as e:
    print(f"❌ ERROR: {e}")
