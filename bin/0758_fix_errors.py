#!/data/data/com.termux/files/usr/bin/python3
"""Auto-fix known PTTR typos across all AERO_ROOT files."""
import os, glob

ROOT = "/data/data/com.termux/files/home/AERO_ROOT"
FIXES = {
    "PTTR): 000:1": "PTTR): >9,000:1",
    "PTTR: 000:1": "PTTR: >9,000:1",
}

count_files = 0
count_fixes = 0

for filepath in glob.glob(os.path.join(ROOT, "**/*.txt"), recursive=True):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        continue

    original = content
    for bad, good in FIXES.items():
        if bad in content:
            content = content.replace(bad, good)
            count_fixes += content.count(good) - original.count(good)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        count_files += 1
        print(f"  Fixed: {filepath}")

print(f"\nDone! Fixed {count_fixes} error(s) in {count_files} file(s).")
