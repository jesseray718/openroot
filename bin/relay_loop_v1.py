#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
relay_loop_v1.py

Guarded publish relay:
  1) verify rootkit chain is green
  2) verify POPW attestation exists for --job-id
  3) enforce bin/ tracking guard (git add -N bin/)
  4) check clean/staged state
  5) optional commit
  6) optional tag
  7) optional push

Defaults are safe:
  - no commit unless --commit
  - no tag unless --tag
  - no push unless --push
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
BIN = ROOT / "bin"

def run(cmd, check=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd)}\n{r.stderr}")
    return r

def verify_chain():
    r = run([sys.executable, str(BIN / "newton_chain_v1.py"), "verify"])
    if r.returncode not in (0, 1, 2):
        return False, "chain verify invocation failed"

    # Expect JSON like {"blocks":N,"status":"green"}
    try:
        payload = json.loads((r.stdout or "").strip() or "{}")
        status = payload.get("status")
        if status == "green":
            return True, f"chain green ({payload.get('blocks', 0)} blocks)"
        return False, f"chain not green: {payload}"
    except Exception:
        return False, f"chain verify output parse failed: {r.stdout.strip()}"

def verify_popw(job_id):
    r = run([sys.executable, str(BIN / "popw_ledger_v1.py"), "list", "--job-id", job_id])
    if r.returncode != 0:
        return False, f"popw list failed: {r.stderr.strip()}"
    try:
        payload = json.loads((r.stdout or "").strip() or "{}")
    except Exception:
        return False, f"popw list parse failed: {r.stdout.strip()}"

    rows = payload.get("attestations", [])
    if not rows:
        return False, f"no POPW attestations for job_id={job_id}"
    return True, f"popw ok ({len(rows)} attestations)"

def guard_bin_tracking():
    # If bin has no tracked files, stage intent-only to avoid untracked blindness
    r = run(["git", "-C", str(ROOT), "ls-files", "bin/"])
    tracked = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    if tracked:
        return True, f"bin tracked ({len(tracked)} files)"
    run(["git", "-C", str(ROOT), "add", "-N", "bin/"])
    return False, "bin had no tracked files; applied git add -N bin/ (HELD)"

def has_staged_changes():
    r = run(["git", "-C", str(ROOT), "diff", "--cached", "--name-only"])
    files = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    return len(files) > 0, files

def working_tree_dirty():
    r = run(["git", "-C", str(ROOT), "status", "--porcelain"])
    lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    return len(lines) > 0, lines

def maybe_commit(message):
    # Commit only if staged changes exist
    staged, files = has_staged_changes()
    if not staged:
        return False, "no staged changes to commit"
    r = run(["git", "-C", str(ROOT), "commit", "-m", message])
    if r.returncode != 0:
        return False, f"commit failed: {r.stderr.strip()}"
    return True, (r.stdout or "").strip()

def maybe_tag(tag):
    r = run(["git", "-C", str(ROOT), "tag", tag])
    if r.returncode != 0:
        return False, f"tag failed: {r.stderr.strip()}"
    return True, f"tagged {tag}"

def maybe_push():
    r = run(["git", "-C", str(ROOT), "push"])
    if r.returncode != 0:
        return False, f"push failed: {r.stderr.strip()}"
    return True, (r.stdout or "").strip()

def main():
    ap = argparse.ArgumentParser(description="Guarded publish relay")
    ap.add_argument("--job-id", required=True, help="job id that must have POPW attestation")
    ap.add_argument("--commit", action="store_true", help="create commit if staged changes exist")
    ap.add_argument("--message", default="relay: guarded publish", help="commit message")
    ap.add_argument("--tag", default=None, help="optional git tag")
    ap.add_argument("--push", action="store_true", help="push to remote after guards pass")
    ap.add_argument("--allow-dirty", action="store_true", help="allow uncommitted working tree")
    args = ap.parse_args()

    ok_chain, msg_chain = verify_chain()
    if not ok_chain:
        print(f"[held] chain gate failed: {msg_chain}")
        return 1
    print(f"[banked] {msg_chain}")

    ok_popw, msg_popw = verify_popw(args.job_id)
    if not ok_popw:
        print(f"[held] popw gate failed: {msg_popw}")
        return 1
    print(f"[banked] {msg_popw}")

    ok_bin, msg_bin = guard_bin_tracking()
    if not ok_bin:
        print(f"[held] {msg_bin}")
        return 1
    print(f"[banked] {msg_bin}")

    if not args.allow_dirty:
        dirty, dirty_lines = working_tree_dirty()
        if dirty:
            print("[held] working tree not clean; commit/stash first")
            for ln in dirty_lines[:30]:
                print(f"  {ln}")
            return 1

    if args.commit:
        ok_commit, msg_commit = maybe_commit(args.message)
        if not ok_commit:
            print(f"[held] commit gate: {msg_commit}")
            return 1
        print(f"[banked] {msg_commit}")

    if args.tag:
        ok_tag, msg_tag = maybe_tag(args.tag)
        if not ok_tag:
            print(f"[held] tag gate: {msg_tag}")
            return 1
        print(f"[banked] {msg_tag}")

    if args.push:
        ok_push, msg_push = maybe_push()
        if not ok_push:
            print(f"[held] push gate: {msg_push}")
            return 1
        print(f"[banked] push ok")
        if msg_push:
            print(msg_push)

    print("[banked] relay gate complete (no unsafe actions performed)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
