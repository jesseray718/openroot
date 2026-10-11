#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
untracked_triage_v1.py - classify and act on untracked files.
CANARY:OPENROOT-UNTRACKED-TRIAGE-V1
Default: dry-run report only. CONFIRM=1 env var required to stage/commit.
Buckets: CODE -> commit | DOCS -> commit | DATA -> inspect/hold | UNKNOWN -> hold.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/jesse/openroot")

CODE_DIRS = ("relay/", "scripts/audit/")
CODE_EXTS = (".sh", ".py", ".json")
DOC_DIRS = ("context_bridge/",)
DATA_HOLD = ("data/a1_config.json",)
LEDGER_HOLD = ("ledger/newton_chain_v2_RELINKED.jsonl",)

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True)

def classify(path):
    if path.endswith("/"):
        d = path
        if d.startswith(CODE_DIRS):
            return "CODE"
        if d.startswith(DOC_DIRS):
            return "DOCS"
        return "UNKNOWN"
    if path in DATA_HOLD or path in LEDGER_HOLD:
        return "DATA"
    if path.endswith(CODE_EXTS) and "/" not in path:
        return "CODE"
    if path.startswith("reports/") or path.startswith("attic/"):
        return "DATA"
    return "UNKNOWN"

def item_type(p):
    return "dir " if (ROOT / p.rstrip("/")).is_dir() else "file"

def main():
    confirm = os.environ.get("CONFIRM") == "1"
    mode = "[gate] CONFIRM=1 LIVE MODE" if confirm else "[gate] DRY RUN (set CONFIRM=1 to execute)"
    print("CANARY:OPENROOT-UNTRACKED-TRIAGE-V1")
    print(mode)

    r = git("status", "--porcelain")
    untracked = [ln[3:] for ln in r.stdout.splitlines()
                 if ln.strip().startswith("??")]

    if not untracked:
        print("[banked] no untracked files; tree already triaged")
        return 0
    print(f"[gate] {len(untracked)} untracked items\n")

    buckets = {"CODE": [], "DOCS": [], "DATA": [], "UNKNOWN": []}
    for p in untracked:
        b = classify(p)
        buckets[b].append(p)
        tgt = ROOT / p.rstrip("/")
        try:
            size = sum(f.stat().st_size for f in tgt.rglob("*") if f.is_file()) if tgt.is_dir() else tgt.stat().st_size
        except OSError:
            size = -1
        print(f"  [{b:7s}] {item_type(p)} {p:60s} {size/1024:.1f}KiB" if size >= 0
              else f"  [{b:7s}] {item_type(p)} {p}")

    for name, desc in (("CODE", "scripts/configs -> commit"),
                       ("DOCS", "context_bridge docs -> commit")):
        if not buckets[name]:
            continue
        print(f"\n[stage:{name}] {desc}")
        if not confirm:
            for p in buckets[name]:
                print(f"  (dry) git add {p}")
            continue
        r = git("add", *buckets[name])
        if r.returncode != 0:
            print("[held] add failed: " + r.stderr.strip())
            return 1
        # compile gate for python/sh artifacts added from this bucket
        for p in buckets[name]:
            tgt = ROOT / p.rstrip("/")
            files = tgt.rglob("*") if tgt.is_dir() else [tgt]
            for f in files:
                if f.suffix == ".py":
                    c = subprocess.run([sys.executable, "-m", "py_compile", str(f)],
                                      capture_output=True, text=True)
                    if c.returncode != 0:
                        print(f"[held] py_compile failed: {f}\n{c.stderr}")
                        return 1
        msg = f"triage: adopt {name.lower()} artifacts ({len(buckets[name])} items); CANARY:OPENROOT-UNTRACKED-TRIAGE-V1"
        r = git("commit", "-m", msg)
        print("[banked] committed: " + (r.stdout or "").strip().splitlines()[0])
    for name in ("DATA", "UNKNOWN"):
        if buckets[name]:
            print(f"\n[held] {name} ({len(buckets[name])} items) requires human decision - no action taken")
    print("\n" + "[banked] triage complete - CODE/DOCS " +
          ("committed" if confirm else "staged-for-review (dry run)") + ", DATA/UNKNOWN held")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
