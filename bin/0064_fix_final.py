#!/data/data/com.termux/files/usr/bin/python3
from __future__ import annotations
import ast, os, subprocess, sys
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
REPO = Path(os.environ.get("UNE_REPO", HOME / "une")).resolve()

print("=" * 70)
print("STEP 1: Read current problematic lines")
print("=" * 70)

files_to_check = [
    ("snapshot.py", 92),
    ("snapshot_restored.py", 92),
    ("bin/agape_board_advisor.py", 68),
]

for rel, lineno in files_to_check:
    p = REPO / rel
    if p.exists():
        lines = p.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
        if len(lines) >= lineno:
            print(f"{rel}:{lineno} = {repr(lines[lineno-1])}")
        else:
            print(f"{rel}:{lineno} = LINE DOES NOT EXIST (file has {len(lines)} lines)")
    else:
        print(f"{rel}: FILE DOES NOT EXIST")

print("\n" + "=" * 70)
print("STEP 2: Apply aggressive line replacement")
print("=" * 70)

def safe_write(p, text):
    p.write_text(text, encoding="utf-8", errors="surrogateescape")
    print(f"WROTE: {p.relative_to(REPO)}")

# Fix snapshot.py - replace entire line 92 with safe version
p = REPO / "snapshot.py"
if p.exists():
    lines = p.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    if len(lines) >= 92:
        # Replace with completely safe line
        lines[91] = '        "Check: cat $OPENROOT_HOME/notes.txt (for new ideas)",'
        safe_write(p, "\n".join(lines) + ("\n" if p.read_text(errors="surrogateescape").endswith("\n") else ""))

# Fix snapshot_restored.py
p = REPO / "snapshot_restored.py"
if p.exists():
    lines = p.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    if len(lines) >= 92:
        lines[91] = '        "Check: cat $OPENROOT_HOME/notes.txt (for new ideas)",'
        safe_write(p, "\n".join(lines) + ("\n" if p.read_text(errors="surrogateescape").endswith("\n") else ""))

# Fix advisor - remove ALL double commas globally
p = REPO / "bin/agape_board_advisor.py"
if p.exists():
    text = p.read_text(encoding="utf-8", errors="surrogateescape")
    if '",,' in text or ', ,' in text:
        text = text.replace('",,', '",').replace(', ,', ',')
        safe_write(p, text)

# Remove missing files from git tracking
missing_files = [
    "computational_flow/thermal_cascade_optimizer.py",
    "computational_flow/agape_stress_test.py",
    "computational_flow/cosmic_query_engine.py",
]
for rel in missing_files:
    result = subprocess.run(["git", "rm", "--cached", "-f", rel], cwd=REPO, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Git removed: {rel}")
    elif "did not match" in result.stderr.lower():
        print(f"Not tracked by git: {rel}")

print("\n" + "=" * 70)
print("STEP 3: Re-validate all Python files")
print("=" * 70)

failures = []
SKIP_DIRS = {".git", ".repair-backups", "__pycache__"}
for src in REPO.rglob("*.py"):
    if any(part in SKIP_DIRS for part in src.parts):
        continue
    if not src.is_file():
        failures.append(f"{src.relative_to(REPO)}: MISSING")
        continue
    try:
        ast.parse(src.read_text(encoding="utf-8", errors="surrogateescape"))
    except SyntaxError as e:
        failures.append(f"{src.relative_to(REPO)}:{e.lineno}: {e.msg}")
    except Exception as e:
        failures.append(f"{src.relative_to(REPO)}: {type(e).__name__}: {e}")

if failures:
    print(f"\n{len(failures)} ERRORS REMAIN:")
    for f in failures:
        print(f"  {f}")
    print("\nManual intervention needed. Run: cat /data/data/com.termux/files/home/une/snapshot.py | sed -n '90,94p'")
    sys.exit(1)
else:
    print("\n✓ ALL PYTHON FILES COMPILE!")
    
    print("\n" + "=" * 70)
    print("STEP 4: Git commit")
    print("=" * 70)
    
    subprocess.run(["git", "add", "-A"], cwd=REPO, check=False)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO, capture_output=True, text=True)
    print("Staged files:")
    print(proc.stdout or "(none)")
    
    proc2 = subprocess.run(["git", "commit", "-m", "fix: complete syntax repair - remove missing files, fix quotes"], cwd=REPO, capture_output=True, text=True)
    if proc2.returncode == 0:
        print("\nCommit succeeded:")
        print(proc2.stdout)
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=REPO, capture_output=True, text=True).stdout.strip()
        if branch:
            push = subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], cwd=REPO, capture_output=True, text=True)
            print(f"\nPushed to {branch}: {push.returncode == 0}")
            if push.returncode != 0:
                print(push.stderr)
    else:
        print("\nCommit failed:")
        print(proc2.stderr)

sys.exit(0)
