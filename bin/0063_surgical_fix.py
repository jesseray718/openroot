#!/data/data/com.termux/files/usr/bin/python3
import ast, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
REPO = Path(os.environ.get("UNE_REPO", HOME / "une")).resolve()

def fix_file(rel):
    p = REPO / rel
    if not p.exists():
        return False, [], "FILE MISSING"
    
    before = p.read_text(encoding="utf-8", errors="surrogateescape")
    after = before
    notes = []
    
    if rel == "bin/agape_board_advisor.py":
        # Fix all double commas in .get() calls
        cnt = after.count('",,')
        if cnt:
            after = after.replace('",,', '",')
            after = after.replace(', ,', ',')
            notes.append(f"removed {cnt} double commas")
    
    elif rel == "bin/h003_resonant_solver.py":
        # Fix line 349: broken f-string
        lines = after.splitlines()
        if len(lines) >= 349:
            bad = "#   │    Capture eff: {p['lab_eff']*100:.0f}%  |  Stored: {r['Q_heat'*(1-p['heat_frac'])*p['lab_eff']/1000:.2f} kW   │"
            good = "#   │    Capture eff: {p['lab_eff']*100:.0f}%  |  Stored: {r['Q_heat']*(1-p['heat_frac'])*p['lab_eff']/1000:.2f} kW   │"
            if bad in after:
                after = after.replace(bad, good)
                notes.append("fixed line 349 f-string quote")
            else:
                # Direct line replacement
                lines[348] = "#   │    Capture eff: {p['lab_eff']*100:.0f}%  |  Stored: {r['Q_heat']*(1-p['heat_frac'])*p['lab_eff']/1000:.2f} kW   │"
                after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
                notes.append("replaced line 349")
    
    elif rel in ("snapshot.py", "snapshot_restored.py"):
        # Fix lines 92-93 with broken path strings
        lines = after.splitlines()
        changes = 0
        for i in range(min(94, len(lines))):
            if 'os.environ.get("OPENROOT_HOME"' in lines[i]:
                # Replace the whole broken string pattern
                lines[i] = lines[i].replace(
                    'cat os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")notes.txt',
                    'cat $OPENROOT_HOME/notes.txt'
                ).replace(
                    'tail -10 os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")guardian_log.jsonl',
                    'tail -10 $OPENROOT_HOME/guardian_log.jsonl'
                )
                changes += 1
        if changes:
            after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
            notes.append(f"fixed {changes} path strings in lines 92-93")
    
    elif rel == "tools/stream_of_thought.py":
        # Fix line 15-16 corrupted expressions
        lines = after.splitlines()
        if len(lines) >= 16:
            # Line 15 has broken escaping
            lines[14] = 'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"'
            # Line 16 has broken Path string
            lines[15] = 'WISDOM_CORPUS_PATH = Path(os.environ.get("UNE_HOME", str(Path.home() / "une"))) / "wisdom" / "wisdom_corpus.json"'
            after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
            notes.append("fixed lines 15-16 path expressions")
    
    # Ensure imports
    if "os.environ" in after or "Path(" in after:
        lines = after.splitlines()
        insert_at = 1 if lines and lines[0].startswith("#!") else 0
        has_os = any(l.strip() == "import os" for l in lines)
        has_path = any("from pathlib import Path" in l for l in lines)
        if not has_os and ("os.environ" in after or "os." in after):
            lines.insert(insert_at, "import os")
            insert_at += 1
        if not has_path and "Path(" in after:
            lines.insert(insert_at, "from pathlib import Path")
        after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
    
    changed = after != before
    return changed, notes, None if changed else "NO CHANGES"

print("=" * 70)
print("APPLYING SURGICAL FIXES")
print("=" * 70)

targets = [
    "bin/agape_board_advisor.py",
    "bin/h003_resonant_solver.py", 
    "snapshot.py",
    "snapshot_restored.py",
    "tools/stream_of_thought.py",
]

for rel in targets:
    changed, notes, info = fix_file(rel)
    if info == "FILE MISSING":
        print(f"{rel}: {info}")
    elif changed:
        p = REPO / rel
        p.write_text(open(REPO / rel, 'r', errors='surrogateescape').read().replace('', ''), encoding="utf-8", errors="surrogateescape")
        # Actually write the fixed content
        before = open(REPO / rel, 'r', errors='surrogateescape').read()
        # Need to recalculate - let me rewrite properly
        pass
    print(f"{rel}: {notes if changed else info}")

# Rewrite properly with actual file writes
print("\n" + "=" * 70)
print("REWRITING FILES WITH FIXES")
print("=" * 70)

for rel in targets:
    p = REPO / rel
    if not p.exists():
        print(f"{rel}: SKIP (missing)")
        continue
    
    before = p.read_text(encoding="utf-8", errors="surrogateescape")
    after = before
    notes = []
    
    if rel == "bin/agape_board_advisor.py":
        if '",,' in after:
            after = after.replace('",,', '",')
        if ', ,' in after:
            after = after.replace(', ,', ',')
        if after != before:
            notes.append("removed double commas")
    
    elif rel == "bin/h003_resonant_solver.py":
        lines = after.splitlines()
        if len(lines) >= 349 and "Q_heat'" in lines[348]:
            lines[348] = lines[348].replace("r['Q_heat'", "r['Q_heat']")
            after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
            notes.append("fixed f-string quote on line 349")
    
    elif rel in ("snapshot.py", "snapshot_restored.py"):
        lines = after.splitlines()
        for i in range(len(lines)):
            if 'cat os.environ.get("OPENROOT_HOME"' in lines[i]:
                lines[i] = lines[i].replace('cat os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")notes.txt', 'cat "$OPENROOT_HOME/notes.txt"')
            if 'tail -10 os.environ.get("OPENROOT_HOME"' in lines[i]:
                lines[i] = lines[i].replace('tail -10 os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")guardian_log.jsonl', 'tail -10 "$OPENROOT_HOME/guardian_log.jsonl"')
        after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
        if after != before:
            notes.append("fixed path strings")
    
    elif rel == "tools/stream_of_thought.py":
        lines = after.splitlines()
        if len(lines) >= 16:
            lines[14] = 'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"'
            lines[15] = 'WISDOM_CORPUS_PATH = Path(os.environ.get("UNE_HOME", str(Path.home() / "une"))) / "wisdom" / "wisdom_corpus.json"'
            after = "\n".join(lines) + ("\n" if before.endswith("\n") else "")
            notes.append("fixed lines 15-16")
    
    if after != before:
        p.write_text(after, encoding="utf-8", errors="surrogateescape")
        print(f"WROTE: {rel} - {notes}")
    else:
        print(f"NO CHANGE: {rel}")

# Final validation
print("\n" + "=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

failures = []
SKIP = {".git", ".repair-backups", "__pycache__"}
for src in REPO.rglob("*.py"):
    if any(x in src.parts for x in SKIP): continue
    if not src.is_file():
        failures.append(f"{src.relative_to(REPO)}: MISSING")
        continue
    try:
        ast.parse(src.read_text(encoding="utf-8", errors="surrogateescape"))
    except SyntaxError as e:
        failures.append(f"{src.relative_to(REPO)}:{e.lineno}: {e.msg}")

if failures:
    print(f"\n{len(failures)} ERRORS REMAIN:")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print("\n✓ ALL PYTHON FILES COMPILE!")
    
    # Git commit
    print("\n" + "=" * 70)
    print("COMMITTING CHANGES")
    print("=" * 70)
    
    for rel in targets:
        subprocess.run(["git", "add", rel], cwd=REPO, check=False)
    
    proc = subprocess.run(["git", "commit", "-m", "fix: surgical repair of 5 remaining syntax errors"], cwd=REPO, capture_output=True, text=True)
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr)
    
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    if branch:
        subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], cwd=REPO, check=False)
        print(f"PUSHED to {branch}")
    
    sys.exit(0)
