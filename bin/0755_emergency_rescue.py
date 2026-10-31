#!/data/data/com.termux/files/usr/bin/env python3
"""
EMERGENCY DATA RESCUE v1.0
Compresses project files to prevent loss when RAM is low.
Moves compressed archive to /sdcard/Backup_Science/.
"""
import os
import zipfile
from datetime import datetime

# CONFIGURATION
SOURCE_DIR = os.path.expanduser("~/AERO_ROOT")
BACKUP_DIR = "/sdcard/Backup_Science"
DATE_STR = datetime.now().strftime("%Y%m%d_%H%M")
ZIP_FILENAME = f"AeroCement_Data_Rescue_{DATE_STR}.zip"
ZIP_PATH = os.path.join(BACKUP_DIR, ZIP_FILENAME)

def main():
    print("🚨 EMERGENCY RESCUE INITIATED...")
    
    # 1. Create Backup Directory on /sdcard
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"✅ Backup Target: {BACKUP_DIR}")

    # 2. Create Zip Archive
    print(f"📦 Compressing data to: {ZIP_FILENAME}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(SOURCE_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, SOURCE_DIR)
                    zipf.write(file_path, arcname)
        
        # Get size
        size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
        print(f"✅ Compression Complete! Size: {size_mb:.2f} MB")
        print(f"   Safe Copy Location: {ZIP_PATH}")
        
        # 3. Verify File Exists
        if os.path.exists(ZIP_PATH):
            print("\n🛡️  YOUR DATA IS SAFE!")
            print("   You can now clear Termux cache or delete old temp files.")
            print("   To restore later: unzip this file back to ~/")
        else:
            print("❌ Error: Zip file not created.")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("   Please check storage permissions.")

if __name__ == "__main__":
    main()
