#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
openroot_cleanup_and_publish_v1.py - v2026-10-10
Cleans dirty working tree, commits pending changes, publishes via rootkit relay.
Idempotent: safe to re-run; second run reports nothing-to-commit and re-verifies.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
BIN = ROOT / "bin"

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)

def main():
    print("[GATE] openroot cleanup and publish")

    # STAGE 1: stage known-modified files (tolerates clean state)
    r = run(["git", "add", ".gitignore", "ledger/newton_chain.jsonl"])
    if r.returncode != 0:
        print("[held] stage failed: " + r.stderr.strip())
        return 1
    print("[banked] staged modified files")

    # STAGE 2: report untracked (informational, no action taken)
    r = run(["git", "status", "--porcelain"])
    untracked = [ln for ln in r.stdout.splitlines() if ln.strip().startswith("??")]
    print(f"[gate] untracked files present: {len(untracked)} (no auto-add; human decides)")
    for ln in untracked[:30]:
        print("  " + ln)

    # STAGE 3: commit staged changes
    r = run(["git", "commit", "-m",
             "chore: commit ledger chain + gitignore; canary OPENROOT-CLEANUP-PUBLISH-V1"])
    if r.returncode == 0:
        print("[banked] commit created")
        print((r.stdout or "").rstrip())
    elif "nothing to commit" in (r.stdout + r.stderr).lower():
        print("[banked] nothing to commit (already clean)")
    else:
        print("[held] commit failed: " + r.stderr.strip())
        return 1

    # STAGE 4: guarded publish via rootkit relay (chain + popw + bin gates)
    job_id = "job-bom-dbe87f1ecee3-ea4809a2"
    r = run([sys.executable, str(BIN / "rootkit.py"),
             "publish", "--job-id", job_id, "--push"])
    print((r.stdout or "").rstrip())
    if r.returncode != 0:
        print("[held] publish gate failed rc=" + str(r.returncode))
        return 1
    print("[banked] publish complete")

    # STAGE 5: verify remote sync
    r = run(["git", "rev-parse", "HEAD"])
    local_head = r.stdout.strip()
    r = run(["git", "rev-parse", "origin/main"])
    remote_head = r.stdout.strip()
    if local_head == remote_head:
        print(f"[banked] remote in sync: {local_head[:12]}")
        return 0
    print(f"[held] remote diverged: local={local_head[:12]} origin/main={remote_head[:12]} (may need fetch first)")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
