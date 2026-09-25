#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {".py", ".sh", ".js", ".ts", ".go", ".c", ".h", ".yaml", ".yml"}
SPDX_REQUIRED = {".py", ".sh", ".js", ".ts", ".go", ".c", ".h"}
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
]

def tracked_paths():
    output = subprocess.check_output(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        stderr=subprocess.STDOUT,
    )
    return [ROOT / item for item in output.splitlines() if item]

def is_authored(path):
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return False
    if relative.parts and relative.parts[0] == "bin":
        name = path.name
        if re.match(r"^\d{4}_", name):
            return False
    return True

failures = []
counts = {"python": 0, "json": 0, "shell": 0, "spdx": 0, "text": 0}

for path in tracked_paths():
    if not path.is_file():
        continue

    rel = path.relative_to(ROOT)
    suffix = path.suffix.lower()

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        failures.append(f"Read error: {rel}: {exc}")
        continue

    if suffix == ".py":
        counts["python"] += 1
        try:
            ast.parse(text, filename=str(rel))
        except SyntaxError as exc:
            failures.append(f"Python syntax error: {rel}:{exc.lineno}:{exc.offset}: {exc.msg}")

    if suffix == ".json":
        counts["json"] += 1
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            failures.append(f"JSON error: {rel}:{exc.lineno}:{exc.colno}: {exc.msg}")

    if suffix == ".sh":
        counts["shell"] += 1
        check = subprocess.run(
            ["bash", "-n", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if check.returncode != 0:
            failures.append(f"Shell syntax error: {rel}: {check.stderr.strip()}")

    if suffix in SPDX_REQUIRED and is_authored(path):
        counts["spdx"] += 1
        if "SPDX-License-Identifier:" not in text[:4096]:
            failures.append(f"Missing SPDX marker: {rel}")

    if suffix in TEXT_SUFFIXES or suffix in {".json", ".md", ".txt"}:
        counts["text"] += 1
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"Possible secret pattern: {rel}")

print("Preflight scanned: " + ", ".join(f"{key}={value}" for key, value in counts.items()))

if failures:
    print("\n".join(failures), file=sys.stderr)
    raise SystemExit(1)
