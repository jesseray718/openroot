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
BACKUP = REPO / ".repair-backups" / f"all-syntax-{STAMP}"
PATCH = BACKUP / "all-syntax-repair.patch"
REPORT = BACKUP / "report.txt"

SKIP_DIRS = {
    ".git",
    ".repair-backups",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "logs",
    "runtime",
}

DOC_PREFIXES = (
    Path("/storage/emulated/0/Documents"),
    Path("/sdcard/Documents"),
    HOME / "storage/shared/Documents",
    HOME / "Documents",
)

def say(message: str) -> None:
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | {message}")

def is_documents_path(path: Path) -> bool:
    try:
        candidate = path.resolve()
    except OSError:
        candidate = path.absolute()

    for prefix in DOC_PREFIXES:
        try:
            candidate.relative_to(prefix.resolve())
            return True
        except ValueError:
            continue
    return False

def ensure_import(text: str, import_line: str, predicate) -> str:
    lines = text.splitlines()

    if any(predicate(line) for line in lines):
        return text

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if insert_at < len(lines) and "coding" in lines[insert_at]:
        insert_at += 1

    lines.insert(insert_at, import_line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

def ensure_imports(text: str) -> str:
    if "os.environ" in text:
        text = ensure_import(
            text,
            "import os",
            lambda line: line == "import os" or line.startswith("from os import "),
        )

    if "Path(" in text:
        text = ensure_import(
            text,
            "from pathlib import Path",
            lambda line: line.startswith("from pathlib import ") and "Path" in line,
        )

    return text

def path_expression(suffix: str) -> str:
    suffix = suffix.strip("/")
    parts = [part for part in suffix.split("/") if part]
    base = 'Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot"))'
    if not parts:
        return base
    return base + "".join(f' / {part!r}' for part in parts)

def replace_bad_openroot_string_literals(text: str) -> tuple[str, int]:
    """
    Changes only malformed values that have this exact broken source shape:
    "os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")relative/path"
    """
    changes = 0

    double_pattern = re.compile(
        r'"os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot/?\"\)([^"\n]*)"'
    )
    single_pattern = re.compile(
        r"'os\.environ\.get\(\"OPENROOT_HOME\", \"/sdcard/openroot/?\"\)([^'\n]*)'"
    )

    def double_replacer(match: re.Match[str]) -> str:
        nonlocal changes
        changes += 1
        return f"str({path_expression(match.group(1))})"

    def single_replacer(match: re.Match[str]) -> str:
        nonlocal changes
        changes += 1
        return f"str({path_expression(match.group(1))})"

    text = double_pattern.sub(double_replacer, text)
    text = single_pattern.sub(single_replacer, text)
    return text, changes

def move_future_import_to_top(text: str) -> tuple[str, bool]:
    future_line = "from __future__ import annotations"
    if future_line not in text:
        return text, False

    lines = text.splitlines()
    indexes = [i for i, line in enumerate(lines) if line.strip() == future_line]

    if len(indexes) != 1:
        return text, False

    old_index = indexes[0]
    allowed = 1 if lines and lines[0].startswith("#!") else 0

    if old_index <= allowed:
        return text, False

    lines.pop(old_index)
    lines.insert(allowed, future_line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), True

def repair_known_nonpath_errors(relative: str, text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    if relative == "bin/agape_board_advisor.py":
        old = '.get("total_annual_joule_value",, 0)'
        new = '.get("total_annual_joule_value", 0)'
        if old in text:
            text = text.replace(old, new)
            changes.append("removed duplicate comma in wealth report lookup")

    if relative == "councils/tri_council.py":
        old = "print(json.dumps(result, indent=最近'd)"
        new = "print(json.dumps(result, indent=2))"
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired malformed json indent argument")

    if relative == "computational_flow/atomic_scan.py":
        old = '"os.path.expanduser("~") + "/"une",'
        new = 'str(Path.home() / "une"),'
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired malformed UNE home path")

    if relative == "computational_flow/fs_hook.py":
        old = 'UNE_ROOT = Path("os.path.expanduser("~") + "/"une")'
        new = 'UNE_ROOT = Path(os.environ.get("UNE_ROOT", str(Path.home() / "une")))'
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired UNE_ROOT path")

    if relative == "computational_flow/push_proof.py":
        old = 'REPO_PATH = "os.path.expanduser("~") + "/".projects/openroot"'
        new = 'REPO_PATH = str(Path(os.environ.get("OPENROOT_REPO", str(Path.home() / ".projects" / "openroot"))))'
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired OpenRoot repository path")

    if relative == "computational_flow/structure_enforcer.py":
        old = 'os.environ.get("OPENROOT_HOME", "os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")"),'
        new = 'os.environ.get("OPENROOT_HOME", "/sdcard/openroot"),'
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired nested OPENROOT_HOME default")

    if relative == "bin/concrete_calculus.py":
        old = 'print("   Existing tool available: os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")bin/thermal_cascade_calc.py.save")'
        new = 'print("   Existing tool available: " + str(Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "bin" / "thermal_cascade_calc.py.save"))'
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired tool-location message")

    if relative == "bin/full_mesh_loop.py":
        old = 'MARKOR_DIR = Path("os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")markor") if Path("/sdcard").exists() else UNE_ROOT'
        new = 'MARKOR_DIR = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "markor" if Path("/sdcard").exists() else UNE_ROOT'
        if old in text:
            text = text.replace(old, new)
            changes.append("repaired Markor directory expression")

    if relative == "bin/h003_resonant_solver.py":
        lines = text.splitlines()
        removed = 0
        kept = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith(("│", "┌", "└", "├", "┤", "─")) and not stripped.startswith(("#", '"""', "'''")):
                kept.append("# " + line)
                removed += 1
            else:
                kept.append(line)
        if removed:
            text = "\n".join(kept) + ("\n" if text.endswith("\n") else "")
            changes.append(f"commented {removed} bare box-drawing display line(s)")

    text, moved = move_future_import_to_top(text)
    if moved:
        changes.append("moved future import to legal position")

    text = ensure_imports(text)
    return text, changes

def candidate_files() -> list[Path]:
    files: list[Path] = []
    for source in REPO.rglob("*.py"):
        if any(part in SKIP_DIRS for part in source.parts):
            continue
        if is_documents_path(source):
            continue
        if source.is_file():
            files.append(source)
    return sorted(files)

def compile_failures() -> list[str]:
    failures: list[str] = []
    for source in candidate_files():
        try:
            ast.parse(source.read_text(encoding="utf-8", errors="surrogateescape"), filename=str(source))
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            line = getattr(exc, "lineno", "?")
            message = getattr(exc, "msg", str(exc))
            failures.append(f"{source.relative_to(REPO)}:{line}: {message}")
    return failures

def backup_and_write(path: Path, before: str, after: str) -> None:
    relative = path.relative_to(REPO)
    saved = BACKUP / "files" / relative
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_text(before, encoding="utf-8", errors="surrogateescape")
    path.write_text(after, encoding="utf-8", errors="surrogateescape")

    with PATCH.open("a", encoding="utf-8") as patch:
        patch.writelines(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{relative}",
                tofile=f"b/{relative}",
            )
        )

def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        check=False,
        capture_output=True,
    )

def main() -> int:
    if not (REPO / ".git").is_dir():
        print(f"ERROR | Not a Git repository: {REPO}", file=sys.stderr)
        return 2

    if is_documents_path(REPO):
        print("ERROR | Refusing to modify a Documents path.", file=sys.stderr)
        return 2

    BACKUP.mkdir(parents=True, exist_ok=True)
    report: list[str] = [
        f"timestamp={datetime.now(timezone.utc).isoformat()}",
        f"repo={REPO}",
        "policy=Documents excluded; backups local to .repair-backups",
        "",
    ]
    changed: list[str] = []

    for source in candidate_files():
        relative = str(source.relative_to(REPO))
        before = source.read_text(encoding="utf-8", errors="surrogateescape")

        after, path_count = replace_bad_openroot_string_literals(before)
        after, special_changes = repair_known_nonpath_errors(relative, after)

        notes: list[str] = []
        if path_count:
            notes.append(f"repaired {path_count} malformed OPENROOT_HOME path expression(s)")
        notes.extend(special_changes)

        if after != before:
            backup_and_write(source, before, after)
            changed.append(relative)
            report.append(f"REPAIRED {relative}")
            report.extend(f"  - {note}" for note in notes)

    failures = compile_failures()
    report.extend([
        "",
        f"changed={len(changed)}",
        f"syntax_failures={len(failures)}",
    ])

    if failures:
        report.extend(["", "SYNTAX_FAILURES", *failures])

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    say(f"BACKUP | {BACKUP}")
    say(f"PATCH | {PATCH}")
    say(f"REPORT | {REPORT}")
    say(f"CHANGED | {len(changed)}")
    say(f"SYNTAX_FAILURES | {len(failures)}")

    if failures:
        print("\nRemaining errors; no Git changes were staged or committed:")
        print("\n".join(failures))
        return 1

    warning_files = (
        REPO / "computational_flow/agape_explore_ui.py",
        REPO / "computational_flow/hindsight_compounding_engine.py",
    )
    for path in warning_files:
        if path.is_file():
            before = path.read_text(encoding="utf-8", errors="surrogateescape")
            after = before.replace(r"\~", "~")
            if after != before:
                backup_and_write(path, before, after)
                if str(path.relative_to(REPO)) not in changed:
                    changed.append(str(path.relative_to(REPO)))

    diff_check = git("diff", "--check")
    if diff_check.returncode != 0:
        print(diff_check.stdout + diff_check.stderr, file=sys.stderr)
        print("Whitespace validation failed; no commit made.", file=sys.stderr)
        return 1

    allowed = [
        ".github/CODEOWNERS",
        ".github/copilot-instructions.md",
        ".github/workflows/openroot-ci.yml",
        ".gitignore",
        ".env.example",
        "CONTRIBUTING.md",
        "PATHINVENTORY.yaml",
        "SPONSOR.md",
        "runphone.sh",
        "config/syncthing-profile.example.md",
        "docs/ETA_GOVERNANCE.md",
        "tests/test_closed_loop.py",
        "tools/closed_loop.py",
    ] + changed

    for relative in sorted(set(allowed)):
        path = REPO / relative
        if path.exists() or path.is_symlink():
            result = git("add", "--", relative)
            if result.returncode != 0:
                print(result.stdout + result.stderr, file=sys.stderr)
                return 1

    staged_check = git("diff", "--cached", "--check")
    if staged_check.returncode != 0:
        print(staged_check.stdout + staged_check.stderr, file=sys.stderr)
        print("Staged whitespace validation failed; no commit made.", file=sys.stderr)
        return 1

    staged = git("diff", "--cached", "--quiet")
    if staged.returncode == 0:
        say("DONE | No approved changes were staged; nothing to commit.")
        return 0

    print("\nSTAGED DIFF:")
    print(git("diff", "--cached", "--stat").stdout)

    commit = git("commit", "-m", "Repair malformed path substitutions and syntax")
    if commit.returncode != 0:
        print(commit.stdout + commit.stderr, file=sys.stderr)
        return 1

    branch = git("branch", "--show-current").stdout.strip()
    if not branch:
        print("Commit succeeded, but push was skipped: detached HEAD.", file=sys.stderr)
        return 1

    push = git("push", "origin", f"HEAD:{branch}")
    if push.returncode != 0:
        print(push.stdout + push.stderr, file=sys.stderr)
        print("Commit succeeded locally, but push failed.", file=sys.stderr)
        return 1

    say("DONE | Compilation passed; approved changes committed and pushed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
