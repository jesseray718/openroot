#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: provenance.py BASE_SHA HEAD_SHA", file=sys.stderr)
        return 2

    base, head = sys.argv[1], sys.argv[2]
    failures: list[str] = []
    try:
        merge_base = git("merge-base", base, head)
        commit = git("rev-parse", head)
        subject = git("show", "-s", "--format=%s", head)
        changed = git("diff", "--name-only", "--diff-filter=ACMR", base, head).splitlines()
    except subprocess.CalledProcessError as exc:
        failures.append(str(exc))
        merge_base = ""
        commit = ""
        subject = ""
        changed = []

    report = {
        "check_id": "provenance",
        "status": "passed" if not failures else "failed",
        "base_sha": base,
        "head_sha": head,
        "merge_base_sha": merge_base,
        "head_commit_sha": commit,
        "head_subject": subject,
        "changed_paths": changed,
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
