#!/data/data/com.termux/files/usr/bin/env python3
"""
EMERGENCY RESCUE PROTOCOL v1.0
Run BEFORE making major structural changes to the AeroCement system.
Creates backup snapshot and rollback points.
"""
import os
import shutil
from datetime import datetime

PROJECT_ROOT = os.path.expanduser("~/AERO_ROOT")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "BACKUP_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

def main():
    print("🚨 EMERGENCY RESCUE PROTOCOL INITIATED")
    print("=" * 50)
    
    if not os.path.exists(PROJECT_ROOT):
        print(f"❌ ERROR: Project root {PROJECT_ROOT} not found.")
        return
    
    # Create backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    items_to_backup = [
        "00-ADMIN",
        "01-SHELTER",
        "02-ENERGY",
        "03-LIFE",
        "04-MOBILITY",
        "05-DATA"
    ]
    
    for item in items_to_backup:
        src = os.path.join(PROJECT_ROOT, item)
        dst = os.path.join(BACKUP_DIR, item)
        if os.path.exists(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"✅ Backed up: {item}")
        else:
            print(f"⚠️  Skipped (not found): {item}")
    
    print("=" * 50)
    print(f"🔒 Backup Location: {BACKUP_DIR}")
    print(f"📦 To restore: cp -r {BACKUP_DIR}/* $HOME/AERO_ROOT/")
    print("\nProceed with caution, brother. Verify before committing.\n")

if __name__ == "__main__":
    main()
