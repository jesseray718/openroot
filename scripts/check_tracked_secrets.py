#!/usr/bin/env python3
"""Scan tracked regular-file bytes for a limited set of credential formats."""

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9_]{36,255}\b"),
    "GitHub fine-grained token": re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{20,255}\b"),
    "AWS access key ID": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}


def scan(data):
    return [name for name, pattern in PATTERNS.items() if pattern.search(data)]


def main():
    entries = subprocess.check_output(
        ["git", "ls-files", "-s", "-z"], cwd=ROOT
    ).split(b"\0")
    failures = 0
    checked = 0
    for entry in filter(None, entries):
        metadata, raw_path = entry.split(b"\t", 1)
        mode = metadata.split()[0]
        if mode not in (b"100644", b"100755"):
            continue
        path = ROOT / Path(raw_path.decode("utf-8", errors="surrogateescape"))
        try:
            data = path.read_bytes()
        except OSError as exc:
            print(f"[error] cannot read tracked file: {path.relative_to(ROOT)} ({exc})", file=sys.stderr)
            failures += 1
            continue
        checked += 1
        for name in scan(data):
            print(f"[error] possible {name} in {path.relative_to(ROOT)}", file=sys.stderr)
            failures += 1
    print(f"Scanned {checked} tracked files using {len(PATTERNS)} limited patterns")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
