#!/data/data/com.termux/files/usr/bin/python3
import os, ast, sys
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

for rel, lineno in PROBLEMS:
    p = REPO / rel
    if not p.exists():
        print(f"\n{rel}: FILE MISSING")
        continue
    lines = p.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    start = max(0, lineno - 3)
    end = min(len(lines), lineno + 2)
    print(f"\n--- {rel}:{lineno} ---")
    for i in range(start, end):
        marker = ">>>" if i == lineno - 1 else "   "
        print(f"{marker} {i+1:4d} | {repr(lines[i])}")
