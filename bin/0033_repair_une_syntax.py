#!/data/data/com.termux/files/usr/bin/python3
from __future__ import annotations

import difflib
import os
import py_compile
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
REPO = Path(os.environ.get("UNE_REPO", HOME / "une")).resolve()
STAMP = os.environ.get("UNE_REPAIR_STAMP", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
BACKUP_ROOT = REPO / ".repair-backups" / STAMP
PATCH_FILE = BACKUP_ROOT / "syntax-repair.patch"
REPORT_FILE = BACKUP_ROOT / "report.txt"

TARGETS = (
    "bin/omega_zero.py",
    "bin/orphan_cleanup.py",
    "bin/transmutation_engine.py",
    "computational_flow/atomic_scan.py",
    "computational_flow/fs_hook.py",
    "computational_flow/push_proof.py",
    "computational_flow/q_system.py",
    "computational_flow/structure_enforcer.py",
    "councils/tri_council.py",
    "meta_audit.py",
    "meta_meta.py",
    "self_improve.py",
    "snapshot.py",
    "snapshot_restored.py",
    "tools/stream_of_thought.py",
)

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

DOCUMENT_PREFIXES = (
    Path("/storage/emulated/0/Documents"),
    Path("/sdcard/Documents"),
    HOME / "storage/shared/Documents",
    HOME / "Documents",
)

def is_document_path(path: Path) -> bool:
    try:
        candidate = path.resolve()
    except OSError:
        candidate = path.absolute()
    for prefix in DOCUMENT_PREFIXES:
        try:
            candidate.relative_to(prefix.resolve())
            return True
        except ValueError:
            pass
    return False

def add_imports(text: str) -> str:
    lines = text.splitlines()
    additions = []

    if "os.environ" in text and not any(
        line == "import os" or line.startswith("from os import ")
        for line in lines
    ):
        additions.append("import os")

    if "Path(" in text and not any(
        line.startswith("from pathlib import ") and "Path" in line
        for line in lines
    ):
        additions.append("from pathlib import Path")

    if not additions:
        return text

    index = 0
    if lines and lines[0].startswith("#!"):
        index = 1
    if index < len(lines) and "coding" in lines[index]:
        index += 1

    lines[index:index] = additions
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

def replace(text: str, old: str, new: str, changes: list[str], label: str) -> str:
    if old in text:
        changes.append(label)
        return text.replace(old, new)
    return text

def repair_text(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    broken_root = 'os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")'
    root_expr = 'os.environ.get("OPENROOT_HOME", "/sdcard/openroot")'

    text = replace(
        text,
        'print("Trigger: echo \'text\' > ' + broken_root + 'tmp/input_trigger.txt")',
        'print("Trigger: echo \'text\' > " + str(Path(' + root_expr + ') / "tmp" / "input_trigger.txt"))',
        changes,
        "omega_zero: trigger path",
    )

    text = replace(
        text,
        'print("  2. Move to ' + broken_root + 'orphans_archive/")',
        'print("  2. Move to " + str(Path(' + root_expr + ') / "orphans_archive"))',
        changes,
        "orphan_cleanup: archive path",
    )

    text = replace(
        text,
        '"description": "Found ' + broken_root + ' hardcoded."',
        '"description": "Found hard-coded OpenRoot path; use OPENROOT_HOME configuration."',
        changes,
        "transmutation_engine: invalid description string",
    )

    text = replace(
        text,
        '"os.path.expanduser(\\"~\\") + "/"une",',
        'str(Path.home() / "une"),',
        changes,
        "atomic_scan: home path",
    )

    text = replace(
        text,
        'UNE_ROOT = Path("os.path.expanduser(\\"~\\") + "/"une")',
        'UNE_ROOT = Path(os.environ.get("UNE_ROOT", str(Path.home() / "une")))',
        changes,
        "fs_hook: UNE_ROOT",
    )

    text = replace(
        text,
        'REPO_PATH = "os.path.expanduser(\\"~\\") + "/".projects/openroot"',
        'REPO_PATH = str(Path(os.environ.get("OPENROOT_REPO", str(Path.home() / ".projects" / "openroot"))))',
        changes,
        "push_proof: repository path",
    )

    text = replace(
        text,
        'out_path = "' + broken_root + 'agape_kb/q_system_snapshot.json"',
        'out_path = str(Path(' + root_expr + ') / "agape_kb" / "q_system_snapshot.json")',
        changes,
        "q_system: snapshot path",
    )

    text = replace(
        text,
        'os.environ.get("OPENROOT_HOME", "os.environ.get(\\"OPENROOT_HOME\\", \\"/sdcard/openroot/\\")"),',
        'os.environ.get("OPENROOT_HOME", "/sdcard/openroot"),',
        changes,
        "structure_enforcer: nested environment default",
    )

    text = replace(
        text,
        'Path("' + broken_root + 'agape_kb/audit_report.json")',
        'Path(' + root_expr + ') / "agape_kb" / "audit_report.json"',
        changes,
        "audit path",
    )

    text = replace(
        text,
        'CB = "' + broken_root + 'context_bridge/immortal_context_merged.json"',
        'CB = str(Path(' + root_expr + ') / "context_bridge" / "immortal_context_merged.json")',
        changes,
        "snapshot context bridge path",
    )

    text = replace(
        text,
        'OUTPUT_FILE = "os.environ.get(\\"OPENROOT_HOME\\", \\"/sdcard/openroot\\") + "/"stream_of_thought_report.json"',
        'OUTPUT_FILE = str(Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / "stream_of_thought_report.json")',
        changes,
        "stream_of_thought output path",
    )

    text = replace(
        text,
        "print(json.dumps(result, indent=最近'd)",
        "print(json.dumps(result, indent=2))",
        changes,
        "tri_council invalid JSON indentation",
    )

    return add_imports(text), changes

def main() -> int:
    if not (REPO / ".git").is_dir():
        print(f"ERROR | Not a Git repository: {REPO}", file=sys.stderr)
        return 2

    if is_document_path(REPO):
        print("ERROR | Repository is in a Documents location; aborting.", file=sys.stderr)
        return 2

    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    report: list[str] = [
        f"timestamp_utc={datetime.now(timezone.utc).isoformat()}",
        f"repo={REPO}",
        "policy=Documents paths excluded",
        "",
    ]
    repaired: list[str] = []

    for relative in TARGETS:
        path = REPO / relative
        if not path.exists():
            report.append(f"MISSING {relative}")
            continue
        if is_document_path(path):
            report.append(f"SKIPPED_DOCUMENTS {relative}")
            continue

        before = path.read_text(encoding="utf-8", errors="surrogateescape")
        after, changes = repair_text(before)

        if before == after:
            report.append(f"NO_KNOWN_REPAIR {relative}")
            continue

        backup = BACKUP_ROOT / "files" / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
        path.write_text(after, encoding="utf-8", errors="surrogateescape")

        repaired.append(relative)
        report.append(f"REPAIRED {relative}")
        report.extend(f"  - {item}" for item in changes)

        with PATCH_FILE.open("a", encoding="utf-8") as f:
            f.writelines(
                difflib.unified_diff(
                    before.splitlines(keepends=True),
                    after.splitlines(keepends=True),
                    fromfile=f"a/{relative}",
                    tofile=f"b/{relative}",
                )
            )

    failures: list[str] = []
    checked = 0
    skipped = 0

    for source in REPO.rglob("*.py"):
        if any(part in SKIP_DIRS for part in source.parts):
            continue
        if is_document_path(source):
            skipped += 1
            report.append(f"SKIPPED_DOCUMENTS {source.relative_to(REPO)}")
            continue
        if not source.is_file():
            skipped += 1
            report.append(f"SKIPPED_MISSING_OR_DANGLING {source.relative_to(REPO)}")
            continue

        checked += 1
        try:
            py_compile.compile(str(source), doraise=True)
        except (py_compile.PyCompileError, FileNotFoundError, OSError) as exc:
            failures.append(f"{source.relative_to(REPO)}\n{exc}")

    report.extend([
        "",
        f"REPAIRED_COUNT={len(repaired)}",
        f"COMPILED_COUNT={checked}",
        f"SKIPPED_COUNT={skipped}",
        f"FAILURE_COUNT={len(failures)}",
    ])

    if failures:
        report.extend(["", "COMPILE_FAILURES", *failures])

    REPORT_FILE.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"BACKUP   | {BACKUP_ROOT}")
    print(f"PATCH    | {PATCH_FILE}")
    print(f"REPORT   | {REPORT_FILE}")
    print(f"REPAIRED | {len(repaired)}")
    print(f"COMPILED | {checked}")
    print(f"SKIPPED  | {skipped}")
    print(f"FAILURES | {len(failures)}")

    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
