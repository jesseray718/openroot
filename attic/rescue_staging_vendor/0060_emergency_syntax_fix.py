#!/data/data/com.termux/files/usr/bin/python3
from __future__ import annotations
import ast, difflib, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
REPO = Path(os.environ.get("UNE_REPO", HOME / "une")).resolve()
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP = REPO / ".repair-backups" / f"emergency-{STAMP}"
PATCH_FILE = BACKUP / "emergency-fix.patch"
REPORT_FILE = BACKUP / "report.txt"

TARGETS = {
    "bin/agape_board_advisor.py": "advisor",
    "bin/h003_resonant_solver.py": "solver",
    "snapshot.py": "snapshot",
    "snapshot_restored.py": "snapshot_restored",
    "tools/stream_of_thought.py": "stream",
}
SKIP_DIRS = {".git", ".repair-backups", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", ".venv", "venv", "logs", "runtime"}

def backup_and_write(path, before, after):
    rel = path.relative_to(REPO)
    dest = BACKUP / "files" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(before, encoding="utf-8", errors="surrogateescape")
    path.write_text(after, encoding="utf-8", errors="surrogateescape")
    with PATCH_FILE.open("a", encoding="utf-8") as f:
        f.writelines(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile=f"a/{rel}", tofile=f"b/{rel}"))

def ensure_imports(text):
    lines = text.splitlines()
    insert_at = 1 if lines and lines[0].startswith("#!") else 0
    has_os = any(l.strip() == "import os" or l.startswith("from os import") for l in lines)
    has_path = any(l.startswith("from pathlib import ") and "Path" in l for l in lines)
    if ("os.environ" in text or "os." in text) and not has_os:
        lines.insert(insert_at, "import os"); insert_at += 1
    if "Path(" in text and not has_path:
        lines.insert(insert_at, "from pathlib import Path")
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

def fix_advisor(text):
    notes = []
    if '",, 0)' in text: text = text.replace('",, 0)', '", 0)'); notes.append("fixed duplicate comma in dict.get()")
    if '", , 0)' in text: text = text.replace('", , 0)', '", 0)'); notes.append("fixed spaced duplicate comma")
    return text, notes

def fix_solver(text):
    notes = []; lines = text.splitlines(); result = []; changed = 0
    for line in lines:
        stripped = line.lstrip()
        if re.match(r'^[│┌└├┤─╭╰╱╲▓━┃│]', stripped) and not stripped.startswith(("#", '"""', "'''")):
            result.append("# DISPLAY LINE: " + line); changed += 1
        else: result.append(line)
    if changed: text = "\n".join(result) + ("\n" if text.endswith("\n") else ""); notes.append(f"commented {changed} box-drawing lines")
    return text, notes

def fix_snapshot(text):
    notes = []
    patterns = [(r'SNAPSHOT_PATH\s*=\s*"os\.environ\.get\("OPENROOT_HOME",\s*"/sdcard/openroot/?"\)(?:\s*\+?\s*)?["\']?session_snapshot\.json["\']?', 'SNAPSHOT_PATH = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "session_snapshot.json"')]
    for pattern, replacement in patterns:
        if re.search(pattern, text): text = re.sub(pattern, replacement, text); notes.append("fixed SNAPSHOT_PATH")
    return text, notes

def fix_stream(text):
    notes = []
    patterns = [(r'OUTPUT_FILE\s*=\s*"os\.environ\.get\("OPENROOT_HOME",\s*"/sdcard/openroot/?"\)(?:\s*\+?\s*)?["\']?/?"(?:stream_of_thought_report\.json)["\']?', 'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"')]
    for pattern, replacement in patterns:
        if re.search(pattern, text): text = re.sub(pattern, replacement, text); notes.append("fixed OUTPUT_FILE")
    return text, notes

def main():
    if not (REPO / ".git").is_dir(): print(f"ERROR | Not a git repo: {REPO}", file=sys.stderr); return 1
    BACKUP.mkdir(parents=True, exist_ok=True); changed = []; report_lines = [f"timestamp={datetime.now(timezone.utc).isoformat()}", f"repo={REPO}", ""]
    for rel, fix_type in TARGETS.items():
        path = REPO / rel
        if not path.is_file(): report_lines.append(f"SKIP {rel} (missing)"); continue
        before = path.read_text(encoding="utf-8", errors="surrogateescape"); after = before; notes = []
        if fix_type == "advisor": after, notes = fix_advisor(before)
        elif fix_type == "solver": after, notes = fix_solver(before)
        elif fix_type in ("snapshot", "snapshot_restored"): after, notes = fix_snapshot(before)
        elif fix_type == "stream": after, notes = fix_stream(before)
        after = ensure_imports(after)
        if after != before: backup_and_write(path, before, after); changed.append(rel); report_lines.append(f"FIXED {rel}"); report_lines.extend(f"  - {n}" for n in notes)
    failures = []
    for src in REPO.rglob("*.py"):
        if any(p in SKIP_DIRS for p in src.parts): continue
        try: ast.parse(src.read_text(encoding="utf-8", errors="surrogateescape"), filename=str(src))
        except SyntaxError as e: failures.append(f"{src.relative_to(REPO)}:{e.lineno}: {e.msg}")
        except OSError as e: failures.append(f"{src.relative_to(REPO)}: read error: {e}")
    report_lines.extend(["", f"changed={len(changed)}", f"errors={len(failures)}"])
    if failures: report_lines.extend(["", "REMAINING_ERRORS"] + failures)
    REPORT_FILE.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | BACKUP: {BACKUP}"); print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | CHANGED: {len(changed)}"); print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | ERRORS: {len(failures)}")
    if failures: print("ERROR | Syntax errors remain"); print("\n".join(failures), file=sys.stderr); return 1
    result = subprocess.run(["git", "diff", "--check"], cwd=REPO, capture_output=True, text=True)
    if result.returncode != 0: print(result.stdout + result.stderr, file=sys.stderr); return 1
    for rel in changed: subprocess.run(["git", "add", "--", rel], cwd=REPO, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO).returncode == 0: print("DONE | Nothing staged"); return 0
    print(subprocess.run(["git", "diff", "--cached", "--stat"], cwd=REPO, capture_output=True, text=True).stdout, file=sys.stderr)
    subprocess.run(["git", "commit", "-m", "Emergency syntax repair - final pass"], cwd=REPO, check=True)
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    if not branch: print("Commit succeeded, push skipped (detached HEAD)", file=sys.stderr); return 0
    subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], cwd=REPO, check=True)
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | DONE | All syntax errors fixed, committed, and pushed")
    return 0

if __name__ == "__main__": raise SystemExit(main())
