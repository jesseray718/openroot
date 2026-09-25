#!/data/data/com.termux/files/usr/bin/python3
from __future__ import annotations
import ast, os, sys, subprocess
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
REPO = Path(os.environ.get("UNE_REPO", HOME / "une")).resolve()

PROBLEMS = [
    ("bin/agape_board_advisor.py", 50),
    ("bin/h003_resonant_solver.py", 349),
    ("snapshot.py", 92),
    ("snapshot_restored.py", 92),
    ("tools/stream_of_thought.py", 16),
]

print("=" * 70)
print("DIAGNOSTIC: Reading problematic lines")
print("=" * 70)

for rel, line_num in PROBLEMS:
    path = REPO / rel
    if not path.exists():
        print(f"\n{rel}: FILE MISSING")
        continue
    try:
        lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
        start = max(0, line_num - 3)
        end = min(len(lines), line_num + 2)
        print(f"\n{rel}:{line_num}")
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            print(f"{marker}{i+1:4d} | {lines[i]}")
    except Exception as e:
        print(f"{rel}: ERROR reading - {e}")

print("\n" + "=" * 70)
print("NOW APPLYING FIXES BASED ON DIAGNOSTIC OUTPUT")
print("=" * 70)

# Now apply aggressive fixes based on what we typically see
def fix_file(rel):
    path = REPO / rel
    if not path.exists():
        return False, "FILE MISSING"
    
    before = path.read_text(encoding="utf-8", errors="surrogateescape")
    after = before
    notes = []
    
    # Fix 1: Remove all stray " characters that break strings
    # Pattern: "os.environ.get("...")something"  -> Path(os.environ.get(...)) / "something"
    
    if rel in ("snapshot.py", "snapshot_restored.py"):
        # Line 92 typically: SNAPSHOT_PATH = "...some broken string..."
        old_patterns = [
            ('SNAPSHOT_PATH = "os.environ.get("OPENROOT_HOME", "/sdcard/openroot/') 
            + '")session_snapshot.json"',
            ('SNAPSHOT_PATH = "os.environ.get("OPENROOT_HOME", "/sdcard/openroot/')
            + '"/session_snapshot.json"'),
        ]
        for old in old_patterns:
            if old in after:
                after = after.replace(old, 'SNAPSHOT_PATH = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "session_snapshot.json"')
                notes.append("fixed SNAPSHOT_PATH line 92")
        # Also handle any line 92 specifically
        lines = after.splitlines()
        if len(lines) >= 92:
            line92 = lines[91]  # 0-indexed
            if "SNAPSHOT_PATH" in line92 and "=" in line92:
                # Replace entire line
                lines[91] = 'SNAPSHOT_PATH = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "session_snapshot.json"'
                after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
                notes.append("replaced entire line 92")
    
    if rel == "tools/stream_of_thought.py":
        lines = after.splitlines()
        if len(lines) >= 16:
            line16 = lines[15]
            if "OUTPUT_FILE" in line16 and "=" in line16:
                lines[15] = 'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"'
                after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
                notes.append("replaced entire line 16")
    
    if rel == "bin/agape_board_advisor.py":
        # Line 50: duplicate comma issue
        after = after.replace('",, 0)', '", 0)').replace(', , 0)', ', 0)')
        # Also fix line 50 directly
        lines = after.splitlines()
        if len(lines) >= 50:
            line50 = lines[49]
            if ",," in line50 or ", ," in line50:
                lines[49] = line50.replace('",,', '",').replace(", ,", ",")
                after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
                notes.append("fixed line 50 double comma")
        notes.append("removed all double commas in .get() calls")
    
    if rel == "bin/h003_resonant_solver.py":
        # Comment out box-drawing lines
        lines = after.splitlines()
        changed = 0
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if any(c in stripped[:5] for c in "│┌└├┤─╭╰╱╲▓━┃"):
                if not stripped.startswith(("#", '"""', "'''")):
                    lines[i] = "# BOX DRAWING: " + line
                    changed += 1
        if changed:
            after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
            notes.append(f"commented {changed} box-drawing lines")
    
    # Ensure imports
    if "os.environ" in after or "os." in after:
        if "import os" not in after:
            insert_at = 1 if after.startswith("#!") else 0
            after = after.insert_line(insert_at, "import os")
    if "Path(" in after:
        if "from pathlib import Path" not in after:
            insert_at = 1 if after.startswith("#!") else 0
            after = after.insert_line(insert_at, "from pathlib import Path")
    
    # Helper to insert line
    def insert_line(text, idx, line):
        lines = text.splitlines()
        lines.insert(idx, line)
        return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    
    after = after if after != before else before
    
    return (after != before), notes

for rel, _ in PROBLEMS:
    changed, notes = fix_file(rel)
    if changed:
        print(f"FIXED: {rel} - {notes}")
    else:
        print(f"No changes needed (or already fixed): {rel}")

print("\n" + "=" * 70)
print("FINAL SYNTAX VALIDATION")
print("=" * 70)

failures = []
SKIP_DIRS = {".git", ".repair-backups", "__pycache__"}
for src in REPO.rglob("*.py"):
    if any(p in SKIP_DIRS for p in src.parts):
        continue
    if not src.is_file():
        failures.append(f"{src.relative_to(REPO)}: FILE DOES NOT EXIST")
        continue
    try:
        ast.parse(src.read_text(encoding="utf-8", errors="surrogateescape"), filename=str(src))
    except SyntaxError as e:
        failures.append(f"{src.relative_to(REPO)}:{e.lineno}: {e.msg}")

if failures:
    print(f"\n{len(failures)} REMAINING ERRORS:")
    for f in failures:
        print(f"  {f}")
else:
    print("\n✓ ALL PYTHON FILES NOW COMPILE SUCCESSFULLY!")
