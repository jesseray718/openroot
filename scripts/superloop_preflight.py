#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKABLE_TEXT_SUFFIXES = {
    ".py", ".sh", ".js", ".ts", ".go", ".c", ".h", ".yaml", ".yml", ".json", ".md", ".txt"
}

SPDX_REQUIRED_SUFFIXES = {
    ".py", ".sh", ".js", ".ts", ".go", ".c", ".h"
}

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
]

def git_stdout(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout

def verify_revision(revision):
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", revision],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"Cannot resolve Git revision: {revision}")

def changed_paths(base_revision):
    if not base_revision:
        return [Path(line) for line in git_stdout("ls-files").splitlines() if line]

    verify_revision(base_revision)

    output = git_stdout(
        "diff",
        "--diff-filter=ACMR",
        "--name-only",
        f"{base_revision}...HEAD",
    )

    return [Path(line) for line in output.splitlines() if line]

def requires_spdx(relative_path):
    if relative_path.suffix.lower() not in SPDX_REQUIRED_SUFFIXES:
        return False

    parts = relative_path.parts

    if not parts:
        return False

    if parts[0] in {
        "archive",
        "attic",
        "data",
        "vendor",
        "third_party",
        "node_modules",
        "tmp",
    }:
        return False

    if parts[0] == "bin" and re.match(r"^\d{4}_", relative_path.name):
        return False

    return True

def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")

base = sys.argv[1] if len(sys.argv) > 1 else None
errors = []

counts = {
    "paths": 0,
    "python": 0,
    "json": 0,
    "shell": 0,
    "spdx": 0,
    "text": 0,
}

for relative_path in changed_paths(base):
    path = ROOT / relative_path

    if not path.is_file():
        continue

    suffix = path.suffix.lower()

    if suffix not in CHECKABLE_TEXT_SUFFIXES:
        continue

    counts["paths"] += 1

    try:
        text = read_text(path)
    except OSError as exc:
        errors.append(f"Read error: {relative_path}: {exc}")
        continue

    if suffix == ".py":
        counts["python"] += 1
        try:
            ast.parse(text, filename=str(relative_path))
        except SyntaxError as exc:
            errors.append(
                f"Python syntax error: {relative_path}:{exc.lineno}:{exc.offset}: {exc.msg}"
            )

    if suffix == ".json":
        counts["json"] += 1
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(
                f"JSON error: {relative_path}:{exc.lineno}:{exc.colno}: {exc.msg}"
            )

    if suffix == ".sh":
        counts["shell"] += 1
        check = subprocess.run(
            ["bash", "-n", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if check.returncode != 0:
            errors.append(
                f"Shell syntax error: {relative_path}: {check.stderr.strip()}"
            )

    if requires_spdx(relative_path):
        counts["spdx"] += 1
        if "SPDX-License-Identifier:" not in text[:4096]:
            errors.append(f"Missing SPDX marker: {relative_path}")

    counts["text"] += 1
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"Possible secret pattern: {relative_path}")

print("Preflight changed-file scan: " + ", ".join(
    f"{key}={value}" for key, value in counts.items()
))

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
