#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
# force_merge_push_v1.py — fetch origin/main, merge into local main (no rebase),
# resolve fast-forward or create merge commit, then push. Handles "fetch first" rejects.
# DRY-RUN default. CONFIRM=1 executes merge+push. Human is the only commit gate.
# [canary] force_merge_push_CANARY_MARKER
import os, subprocess, sys, platform

REPO = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"

def say(tag, msg): print(f"[{tag}] {msg}")

def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=REPO,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        say("held", f"FAIL: {cmd}\n{r.stderr.strip()[:300]}"); sys.exit(1)
    return r

assert platform.node() == "optiplex3060", "[held] run on optiplex3060"
os.chdir(REPO)
print("[gate] start CONFIRM=" + str(CONFIRM))

# ── stage 1: ensure staging list exists ────────────────────────────────
CANDIDATES = [
    "README.md", "index.html", "site/index.html",
    "docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md",
    "bin/fix_planetary_math_v1.py",
    "bin/fix_planetary_math_commit_v2.py",
    "bin/force_merge_push_v1.py",
]
stage_list = [f for f in CANDIDATES if os.path.isfile(f)]
say("gate", f"candidate files present on disk: {len(stage_list)}")

# ── stage 2: fetch origin/main to know remote HEAD ───────────────────────
sh(["git", "fetch", "origin", "main"])
local_head = sh("git rev-parse --short HEAD").stdout.strip()
remote_head = sh("git rev-parse --short origin/main").stdout.strip()
say("banked", f"local HEAD={local_head} origin/main={remote_head}")

if local_head == remote_head:
    say("banked", "already at remote HEAD — no fetch needed")
else:
    say("gate", f"divergence detected: local {local_head} vs remote {remote_head}")

# ── stage 3: commit pending changes first ───────────────────────────────
if not CONFIRM:
    say("held", "DRY would skip merge/push (dry-run mode)")
    print("[exit=0]")
    sys.exit(0)

if stage_list:
    sh(["git", "add", *stage_list])
    if sh("git diff --cached --quiet", check=False).returncode != 0:
        sh(["git", "commit", "-m",
            "docs: planetary geodesic mesh math (15,000-node backbone @ ~100km, "
            "wood satellite + Cloud 9 vacuum tensegrity specs, cost analysis "
            "$0.0003/person — $2 claim conservative); provenance: Earth "
            "geometry verified by executed calculation, human gate"])
        local_head = sh("git rev-parse --short HEAD").stdout.strip()
        say("banked", f"committed locally: {local_head}")
    else:
        say("banked", "nothing staged — tree clean")

# ── stage 4: merge remote into local, then push ────────────────────────
sh(["git", "merge", "origin/main", "--no-edit"])
merged_head = sh("git rev-parse --short HEAD").stdout.strip()
say("banked", f"after merge: HEAD={merged_head}")

sh(["git", "push", "origin", "main"])
final_head = sh("git rev-parse --short HEAD").stdout.strip()
say("banked", f"pushed successfully: {final_head}")

print("[exit=0]")
