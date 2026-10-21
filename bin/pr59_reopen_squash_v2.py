#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
# pr59_reopen_squash_v2.py - reopen PR #59, squash-merge, delete branch. Dry-run unless CONFIRM=1.
import json, os, subprocess, sys

CONFIRM = os.environ.get("CONFIRM") == "1"
RD = "/home/jesse/openroot"

def sh(*args):
    r = subprocess.run(args, capture_output=True, text=True, cwd=RD)
    if r.returncode:
        print("[held] FAIL:", " ".join(args), r.stderr.strip())
        sys.exit(1)
    return r.stdout.strip()

def pr():
    return json.loads(sh("gh", "pr", "view", "59", "--json", "state,headRefName"))

print(f"[gate] CONFIRM={CONFIRM} ({'EXECUTE' if CONFIRM else 'dry-run'})")
p = pr()
print(f"[gate] PR59 state={p['state']} head={p['headRefName']}")
if p["state"] == "MERGED":
    print("[banked] already merged - idempotent exit")
elif p["state"] == "CLOSED" and not CONFIRM:
    print("[held] would: gh pr reopen 59")
else:
    if p["state"] == "CLOSED":
        sh("gh", "pr", "reopen", "59")
        print("[banked] reopened PR59")
    if not CONFIRM:
        print("[held] would: gh pr merge 59 --squash --delete-branch")
    else:
        sh("gh", "pr", "merge", "59", "--squash", "--delete-branch")
if CONFIRM:
    p = pr()
    if p["state"] != "MERGED":
        print("[held] MERGE NOT VERIFIED - inspect manually")
        sys.exit(1)
    sh("git", "checkout", "main")
    sh("git", "pull", "--ff-only", "origin", "main")
    print("[banked] squash-merged PR59, main=" + sh("git", "rev-parse", "--short", "origin/main"))
print("[exit=0]")
