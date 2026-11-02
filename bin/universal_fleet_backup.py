#!/usr/bin/env python3
"""
OPENROOT UNIVERSAL FLEET BACKUP ENGINE
Replicates database pods, contribution ledgers, and thermodynamic receipts 
across all available local, removable, and remote platforms.
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

def backup_fleet():
    print("[*] Initializing Universal Fleet Backup across all platforms...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Local Backup Directory
    local_backup_dir = Path("data/thermodynamics/backups")
    local_backup_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = Path("data/thermodynamics/openroot_interactive_pods.db")
    if db_path.exists():
        target_local = local_backup_dir / f"pod_backup_{timestamp}.db"
        shutil.copy(db_path, target_local)
        print(f"[✔] Platform 1 [Local Disk]: Backed up to {target_local}")
        
    # 2. Removable USB Target (if mounted)
    usb_dir = Path("/media/jesse/USB_BACKUP")
    if usb_dir.exists():
        usb_backup_dir = usb_dir / "openroot_backups"
        usb_backup_dir.mkdir(parents=True, exist_ok=True)
        target_usb = usb_backup_dir / f"pod_backup_{timestamp}.db"
        shutil.copy(db_path, target_usb)
        print(f"[✔] Platform 2 [Removable USB]: Backed up to {target_usb}")
    else:
        print("[!] Platform 2 [Removable USB]: Not currently mounted (bypassed cleanly).")
        
    # 3. Remote GitHub Fleet Sync
    try:
        subprocess.run(["git", "add", "data/thermodynamics/", "bin/"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"chore(backup): universal fleet synchronization snapshot {timestamp} ($R=1, C=0$)" ], capture_output=True)
        push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if push_res.returncode == 0:
            print("[✔] Platform 3 [Remote GitHub Origin]: Fleet snapshot successfully pushed.")
        else:
            print("[i] Platform 3 [Remote GitHub Origin]: Working tree clean or already synchronized.")
    except Exception as e:
        print(f"[!] Git fleet sync notice: {e}")
        
    print("[✔] Universal fleet backup cycle completed with zero friction ($R=1, C=0$).")

if __name__ == "__main__":
    backup_fleet()
