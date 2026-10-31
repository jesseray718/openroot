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
TARGET = REPO / "bin/agape_board_advisor.py"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUP = REPO / ".repair-backups" / f"advisor-final-{STAMP}"
PATCH = BACKUP / "advisor-final.patch"
REPORT = BACKUP / "report.txt"

SKIP = {
    ".git", ".repair-backups", "__pycache__", ".pytest_cache",
    ".mypy_cache", "node_modules", ".venv", "venv", "logs", "runtime",
}

def say(message: str) -> None:
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} | {message}")

def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )

def files() -> list[Path]:
    return sorted(
        path for path in REPO.rglob("*.py")
        if path.is_file() and not any(part in SKIP for part in path.parts)
    )

def failures() -> list[str]:
    result = []
    for path in files():
        try:
            ast.parse(
                path.read_text(encoding="utf-8", errors="surrogateescape"),
                filename=str(path),
            )
        except SyntaxError as exc:
            result.append(f"{path.relative_to(REPO)}:{exc.lineno}: {exc.msg}")
    return result

def backup_and_write(before: str, after: str) -> None:
    saved = BACKUP / "files" / "bin" / "agape_board_advisor.py"
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_text(before, encoding="utf-8", errors="surrogateescape")

    with PATCH.open("w", encoding="utf-8") as handle:
        handle.writelines(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile="a/bin/agape_board_advisor.py",
                tofile="b/bin/agape_board_advisor.py",
            )
        )

    TARGET.write_text(after, encoding="utf-8", errors="surrogateescape")

def show_context(line_number: int) -> None:
    lines = TARGET.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    start = max(0, line_number - 6)
    end = min(len(lines), line_number + 5)
    print("\nSOURCE CONTEXT:")
    for index in range(start, end):
        marker = ">>" if index + 1 == line_number else "  "
        print(f"{marker} {index + 1:4d} | {lines[index]}")

def main() -> int:
    if not (REPO / ".git").is_dir():
        print(f"ERROR | Not a Git repository: {REPO}", file=sys.stderr)
        return 2

    if not TARGET.is_file():
        print(f"ERROR | Missing target: {TARGET}", file=sys.stderr)
        return 2

    BACKUP.mkdir(parents=True, exist_ok=True)
    before = TARGET.read_text(encoding="utf-8", errors="surrogateescape")
    after = before

    # Repairs duplicate commas only where they appear before a default value
    # in function/method calls, e.g. get("key",, 0) -> get("key", 0).
    after = re.sub(r'(,\s*),\s*([0-9A-Za-z_"\'])', r'\1 \2', after)

    # Repairs the recurring broken form:
    # "os.environ.get("OPENROOT_HOME", "/sdcard/openroot/")relative"
    def fix_openroot(match: re.Match[str]) -> str:
        suffix = match.group(1).strip("/")
        if suffix:
            return f'str(Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")) / {suffix!r})'
        return 'str(Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot")))'

    after = re.sub(
        r'"os\.environ\.get\("OPENROOT_HOME", "/sdcard/openroot/?\"\)([^"\n]*)"',
        fix_openroot,
        after,
    )

    # Make imports available only if the replacement requires them.
    if "os.environ" in after and not re.search(r"^(import os|from os import )", after, re.M):
        lines = after.splitlines()
        insert = 1 if lines and lines[0].startswith("#!") else 0
        lines.insert(insert, "import os")
        after = "\n".join(lines) + ("\n" if after.endswith("\n") else "")

    if "Path(" in after and not re.search(r"^from pathlib import .*Path", after, re.M):
        lines = after.splitlines()
        insert = 1 if lines and lines[0].startswith("#!") else 0
        lines.insert(insert, "from pathlib import Path")
        after = "\n".join(lines) + ("\n" if after.endswith("\n") else "")

    if after != before:
        backup_and_write(before, after)
        say("REPAIRED | bin/agape_board_advisor.py")
    else:
        say("NO_MATCH | No safe automatic transformation matched line 155.")

    bad = failures()

    REPORT.write_text(
        "\n".join([
            f"timestamp={datetime.now(timezone.utc).isoformat()}",
            f"repo={REPO}",
            f"target={TARGET.relative_to(REPO)}",
            f"syntax_failures={len(bad)}",
            *bad,
            "",
        ]),
        encoding="utf-8",
    )

    say(f"BACKUP | {BACKUP}")
    say(f"PATCH | {PATCH}")
    say(f"REPORT | {REPORT}")
    say(f"SYNTAX_FAILURES | {len(bad)}")

    if bad:
        print("\nNo commit was made.")
        print("\n".join(bad))
        for item in bad:
            if item.startswith("bin/agape_board_advisor.py:"):
                show_context(int(item.split(":")[1]))
        return 1

    if git("diff", "--check").returncode != 0:
        print(git("diff", "--check").stdout, file=sys.stderr)
        print("No commit was made: whitespace validation failed.", file=sys.stderr)
        return 1

    add = git("add", "--", "bin/agape_board_advisor.py")
    if add.returncode != 0:
        print(add.stdout + add.stderr, file=sys.stderr)
        return 1

    checked = git("diff", "--cached", "--check")
    if checked.returncode != 0:
        print(checked.stdout + checked.stderr, file=sys.stderr)
        return 1

    if git("diff", "--cached", "--quiet").returncode == 0:
        say("DONE | Nothing new to commit.")
        return 0

    print(git("diff", "--cached", "--stat").stdout)

    commit = git("commit", "-m", "Fix remaining advisor syntax error")
    if commit.returncode != 0:
        print(commit.stdout + commit.stderr, file=sys.stderr)
        return 1

    branch = git("branch", "--show-current").stdout.strip()
    if not branch:
        print("Commit succeeded locally; detached HEAD prevented push.", file=sys.stderr)
        return 1

    push = git("push", "origin", f"HEAD:{branch}")
    if push.returncode != 0:
        print(push.stdout + push.stderr, file=sys.stderr)
        print("Commit succeeded locally, but push failed.", file=sys.stderr)
        return 1

    say("DONE | Full syntax validation passed; commit pushed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
