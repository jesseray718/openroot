#!/usr/bin/env python3
"""OpenRoot Orphan Cleanup Tool - Lists and optionally archives orphaned files."""
import json, os, shutil
from pathlib import Path

ROOT = Path("/sdcard/openroot")
DOSSIER = ROOT / "dossier.json"
ARCHIVE = ROOT / "orphans_archive"

d = json.loads(DOSSIER.read_text())
orphans = [f for f in d["files"] if f["link_count"] == 0]

print(f"Found {len(orphans)} orphaned files.\n")
print("Options:")
print("  1. List only (default)")
print("  2. Move to /sdcard/openroot/orphans_archive/")
print("  3. Delete permanently")
print("  4. Export list to CSV")

choice = input("\nChoice [1-4]: ").strip() or "1"

if choice == "1":
    for f in orphans:
        print(f"  {f['path']}  ({f['size']} bytes, {f['type']})")
elif choice == "2":
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    moved = 0
    for f in orphans:
        src = ROOT / f["path"]
        dst = ARCHIVE / f["name"]
        if dst.exists():
            dst = ARCHIVE / (f["path"].replace("/", "_"))
        try:
            shutil.move(str(src), str(dst))
            moved += 1
        except Exception as e:
            print(f"  FAIL: {f['path']} - {e}")
    print(f"\nMoved {moved}/{len(orphans)} files to {ARCHIVE}")
elif choice == "3":
    confirm = input(f"Delete {len(orphans)} files permanently? Type YES: ")
    if confirm == "YES":
        deleted = 0
        for f in orphans:
            try:
                (ROOT / f["path"]).unlink()
                deleted += 1
            except: pass
        print(f"\nDeleted {deleted}/{len(orphans)} files.")
    else:
        print("Cancelled.")
elif choice == "4":
    import csv
    csv_path = ROOT / "orphans_list.csv"
    with open(csv_path, "w", newline="") as cf:
        w = csv.writer(cf)
        w.writerow(["path", "name", "type", "size", "ext"])
        for f in orphans:
            w.writerow([f["path"], f["name"], f["type"], f["size"], f["ext"]])
    print(f"\nExported to {csv_path}")
