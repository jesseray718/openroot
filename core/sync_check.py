#!/data/data/com.termux/files/usr/bin/python3
from pathlib import Path
import os
print("=== Syncthing / CUSB Integrity Probe ===")
candidates = [
    "/data/data/com.termux/files/home/storage/shared/Syncthing",
    "/sdcard/Syncthing",
    "/storage/emulated/0/Syncthing",
    "/mnt/media/CUSB/OpenRoot",
    "/sdcard/openroot",
]
for c in candidates:
    p = Path(c)
    if p.exists():
        print(f"[OK]  {c}")
        try:
            print(f"     contents: {len(list(p.iterdir()))} entries")
        except Exception as e:
            print(f"     (permission) {e}")
    else:
        print(f"[--]  {c}")
print("=== end ===")
