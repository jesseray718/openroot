#!/data/data/com.termux/files/usr/bin/python3
from __future__ import annotations

import ast
import difflib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
REPO = Path(os.environ.get("UNE_REPO", HOME / "une")).resolve()
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP = REPO / ".repair-backups" / f"final-syntax-{STAMP}"
PATCH = BACKUP / "final-syntax.patch"
REPORT = BACKUP / "report.txt"

TARGETS = (
    "bin/agape_board_advisor.py",
    "bin/h003_resonant_solver.py",
    "snapshot.py",
    "snapshot_restored.py",
    "tools/stream_of_thought.py",
)

SKIP_DIRS = {
    ".git", ".repair-backups", "__pycache__", ".pytest_cache",
    ".mypy_cache", "node_modules", ".venv", "venv", "logs", "runtime",
}

def say(message: str) -> None:
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | {message}")

def add_import(text: str, statement: str, exists) -> str:
    lines = text.splitlines()
    if any(exists(line) for line in lines):
        return text

    index = 1 if lines and lines[0].startswith("#!") else 0
    if index < len(lines) and "coding" in lines[index]:
        index += 1

    lines.insert(index, statement)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

def add_os_and_path_imports(text: str) -> str:
    if "os." in text:
        text = add_import(
            text, "import os",
            lambda line: line == "import os" or line.startswith("from os import "),
        )
    if "Path(" in text:
        text = add_import(
            text, "from pathlib import Path",
            lambda line: line.startswith("from pathlib import ") and "Path" in line,
        )
    return text

def backup_write(path: Path, before: str, after: str) -> None:
    relative = path.relative_to(REPO)
    stored = BACKUP / "files" / relative
    stored.parent.mkdir(parents=True, exist_ok=True)
    stored.write_text(before, encoding="utf-8", errors="surrogateescape")

    with PATCH.open("a", encoding="utf-8") as handle:
        handle.writelines(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{relative}",
                tofile=f"b/{relative}",
            )
        )

    path.write_text(after, encoding="utf-8", errors="surrogateescape")

def repair_advisor(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []

    replacements = {
        '.get("total_annual_joule_value",, 0)': '.get("total_annual_joule_value", 0)',
        '.get("total_annual_joule_value", , 0)': '.get("total_annual_joule_value", 0)',
        ',, 0)': ', 0)',
    }

    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            notes.append(f"replaced {old!r}")

    return text, notes

def repair_snapshot(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []

    patterns = (
        (
            r'SNAPSHOT_PATH\s*=\s*str\(Path\(os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot"\)\) / "session_snapshot\.json"\)\s*"\)',
            'SNAPSHOT_PATH = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "session_snapshot.json"',
        ),
        (
            r'SNAPSHOT_PATH\s*=\s*"os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot/?\"\)session_snapshot\.json"',
            'SNAPSHOT_PATH = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "session_snapshot.json"',
        ),
        (
            r'SNAPSHOT_PATH\s*=\s*Path\(str\(Path\(os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot"\)\) / "session_snapshot\.json"\)\)',
            'SNAPSHOT_PATH = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "session_snapshot.json"',
        ),
    )

    for pattern, replacement in patterns:
        text, count = re.subn(pattern, replacement, text)
        if count:
            notes.append(f"repaired SNAPSHOT_PATH ({count})")

    text = add_os_and_path_imports(text)
    return text, notes

def repair_stream(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []

    patterns = (
        (
            r'OUTPUT_FILE\s*=\s*str\(Path\(os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot"\)\) / "stream_of_thought_report\.json"\)\s*"\)',
            'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"',
        ),
        (
            r'OUTPUT_FILE\s*=\s*"os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot/?\"\) /?"stream_of_thought_report\.json"',
            'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"',
        ),
        (
            r'OUTPUT_FILE\s*=\s*"os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot/?\"\) \+ "/"stream_of_thought_report\.json"',
            'OUTPUT_FILE = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json"',
        ),
    )

    for pattern, replacement in patterns:
        text, count = re.subn(pattern, replacement, text)
        if count:
            notes.append(f"repaired OUTPUT_FILE ({count})")

    text = add_os_and_path_imports(text)
    return text, notes

def repair_resonant_solver(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    lines = text.splitlines()
    changed = 0
    result: list[str] = []

    for line in lines:
        stripped = line.lstrip()

        # The source contains pasted terminal box art that was not placed in
        # quotes. It cannot be executable Python, so retain it as a comment.
        if stripped.startswith(("│", "┌", "└", "├", "┤", "─", "╭", "╰", "╱", "╲")):
            result.append("# " + line)
            changed += 1
        else:
            result.append(line)

    if changed:
        text = "\n".join(result) + ("\n" if text.endswith("\n") else "")
        notes.append(f"commented {changed} bare box-art line(s)")

    return text, notes

def all_python_files() -> list[Path]:
    sources: list[Path] = []

    for source in REPO.rglob("*.py"):
        if any(part in SKIP_DIRS for part in source.parts):
            continue
        if source.is_file():
            sources.append(source)

    return sorted(sources)

def syntax_failures() -> list[str]:
    failures: list[str] = []

    for source in all_python_files():
        try:
            ast.parse(
                source.read_text(encoding="utf-8", errors="surrogateescape"),
                filename=str(source),
            )
        except SyntaxError as exc:
            failures.append(
                f"{source.relative_to(REPO)}:{exc.lineno}: {exc.msg}"
            )
        except OSError as exc:
            failures.append(f"{source.relative_to(REPO)}: read error: {exc}")

    return failures

def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )

def main() -> int:
    if not (REPO / ".git").is_dir():
        print(f"ERROR | Not a Git repository: {REPO}", file=sys.stderr)
        return 2

    BACKUP.mkdir(parents=True, exist_ok=True)
    changed: list[str] = []
    notes: list[str] = []

    for relative in TARGETS:
        path = REPO / relative
        if not path.is_file():
            notes.append(f"SKIPPED missing {relative}")
            continue

        before = path.read_text(encoding="utf-8", errors="surrogateescape")
        after = before
        repairs: list[str] = []

        if relative == "bin/agape_board_advisor.py":
            after, repairs = repair_advisor(after)
        elif relative in {"snapshot.py", "snapshot_restored.py"}:
            after, repairs = repair_snapshot(after)
        elif relative == "tools/stream_of_thought.py":
            after, repairs = repair_stream(after)
        elif relative == "bin/h003_resonant_solver.py":
            after, repairs = repair_resonant_solver(after)

        if after != before:
            backup_write(path, before, after)
            changed.append(relative)
            notes.append(f"REPAIRED {relative}")
            notes.extend(f"  - {item}" for item in repairs)

    failures = syntax_failures()

    REPORT.write_text(
        "\n".join([
            f"timestamp={datetime.now(timezone.utc).isoformat()}",
            f"repo={REPO}",
            f"changed={len(changed)}",
            "",
            *notes,
            "",
            f"syntax_failures={len(failures)}",
            *failures,
            "",
        ]),
        encoding="utf-8",
    )

    say(f"BACKUP | {BACKUP}")
    say(f"PATCH | {PATCH}")
    say(f"REPORT | {REPORT}")
    say(f"CHANGED | {len(changed)}")
    say(f"SYNTAX_FAILURES | {len(failures)}")

    if failures:
        print("\nNo commit was made. Remaining syntax errors:")
        print("\n".join(failures))
        return 1

    diff_check = git("diff", "--check")
    if diff_check.returncode != 0:
        print(diff_check.stdout + diff_check.stderr, file=sys.stderr)
        print("No commit was made: whitespace validation failed.", file=sys.stderr)
        return 1

    # Stage only tracked changed source files. Backups, logs, Documents,
    # generated bytecode, and unrelated untracked files remain untouched.
    staged_paths = set(changed)

    for relative in staged_paths:
        result = git("add", "--", relative)
        if result.returncode != 0:
            print(result.stdout + result.stderr, file=sys.stderr)
            return 1

    staged_check = git("diff", "--cached", "--check")
    if staged_check.returncode != 0:
        print(staged_check.stdout + staged_check.stderr, file=sys.stderr)
        print("No commit was made: staged whitespace validation failed.", file=sys.stderr)
        return 1

    if git("diff", "--cached", "--quiet").returncode == 0:
        say("DONE | Nothing was staged; no commit required.")
        return 0

    print("\nSTAGED:")
    print(git("diff", "--cached", "--stat").stdout)

    commit = git("commit", "-m", "Complete Python syntax repair")
    if commit.returncode != 0:
        print(commit.stdout + commit.stderr, file=sys.stderr)
        return 1

    branch = git("branch", "--show-current").stdout.strip()
    if not branch:
        print("Commit succeeded locally, but push skipped: detached HEAD.", file=sys.stderr)
        return 1

    push = git("push", "origin", f"HEAD:{branch}")
    if push.returncode != 0:
        print(push.stdout + push.stderr, file=sys.stderr)
        print("Commit succeeded locally, but push failed.", file=sys.stderr)
        return 1

    say("DONE | Full Python syntax validation passed; commit pushed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
