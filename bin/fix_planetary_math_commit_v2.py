#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# fix_planetary_math_commit_v2.py — stage ONLY files that exist on disk, commit,
# push. Fixes v1's fatal pathspec abort on missing START-HERE.md.
# DRY-RUN default. CONFIRM=1 commits+pushes. Human is the only commit gate.
# [canary] fix_planetary_commit_v2_CANARY_MARKER
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

CANDIDATES = [
    "README.md", "index.html", "site/index.html",
    "spoke-links.md", "HELLO.md", "TALENT-ALIGNMENT-PROMPT.md",
    "docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md",
    "bin/kill_simplex_write_doc_v1.py",
    "bin/fix_planetary_math_v1.py",
    "bin/fix_planetary_math_commit_v2.py",
]

stage_list = [f for f in CANDIDATES if os.path.isfile(f)]
say("gate", f"candidate files present on disk: {len(stage_list)} / {len(CANDIDATES)}")
for f in stage_list:
    say("banked", f"  will stage: {f}")

# Simplex strip is already done — nothing to re-do there.
# Sanity check the doc content landed correctly:
doc = "docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md"
if os.path.isfile(doc):
    txt = open(doc).read()
    for probe in ("10f² + 2", "15,000", "0.0003", "chicken wire", "pentavalent"):
        assert probe in txt, f"[held] probe missing from doc: {probe}"
    say("banked", f"doc probes green: {doc} ({os.path.getsize(doc):,} bytes)")
else:
    say("held", f"{doc} not on disk — run fix_planetary_math_v1.py first")

if CONFIRM:
    if not stage_list:
        say("held", "no files to stage — check git status"); sys.exit(1)
    sh(["git", "add", *stage_list])
    if sh("git diff --cached --quiet", check=False).returncode != 0:
        sh(["git", "commit", "-m",
            "docs: planetary geodesic mesh math (15,000-node backbone @ ~100km, "
            "wood satellite + Cloud 9 vacuum tensegrity specs, cost analysis "
            "$0.0003/person — $2 claim conservative); provenance: Earth "
            "geometry verified by executed calculation, human gate"])
        sh(["git", "push", "origin", "main"])
        say("banked", f"pushed {sh('git rev-parse --short HEAD').stdout.strip()}")
    else:
        say("banked", "nothing staged — tree clean")
else:
    say("held", f"DRY would commit+push ({len(stage_list)} files)")

print("[exit=0]")
