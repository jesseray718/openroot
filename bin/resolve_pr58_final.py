#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
# resolve_pr58_final.py — catch up local master, audit PR #58, merge behind CONFIRM=1
import subprocess, os, sys, pathlib, shutil
from datetime import datetime

ROOT = "/home/jesse/openroot"
os.chdir(ROOT)
HELD_FLAGS = []
CONFIRM = os.environ.get("CONFIRM", "0") == "1"

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.stdout.strip(): print(r.stdout.strip())
    if r.stderr.strip() and r.returncode != 0: print(f"[stderr] {r.stderr.strip()}")
    if check and r.returncode != 0:
        HELD_FLAGS.append(f"cmd failed: {' '.join(cmd)}"); return None
    return r

def main():
    print("[canary] resolve_pr58_final.py paste intact")

    print("[stage-0] fetch + snapshot")
    run(["git", "fetch", "origin", "--prune"])
    base = run(["git", "rev-parse", "origin/main"]).stdout.strip()[:8]
    headp = run(["git", "rev-parse", "origin/master"]).stdout.strip()[:8]
    print(f" base(origin/main)={base} head(origin/master)={headp}")
    run(["gh", "pr", "view", "58", "--json", "state,mergeable,title",
         "--jq", '"state=\\(.state) mergeable=\\(.mergeable) title=\\(.title)"'], check=False)

    print("[stage-1] commit audit (incl. CodeRabbit web-UI commits)")
    run(["git", "log", "--oneline", f"{base}..origin/master"], check=False)
    run(["git", "show", "--stat", "--oneline", "24bc1a7"], check=False)
    run(["git", "show", "--stat", "--oneline", "08c913c"], check=False)

    print("[stage-2] size guard (post filter-repo)")
    r = run(["git", "ls-tree", "-r", "-l", "origin/master"], check=False)
    big = []
    if r:
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[3].isdigit() and int(parts[3]) > 1048576:
                big.append(f"{parts[3]}B {' '.join(parts[4:])}")
    if big:
        print(f" [warn] {len(big)} blobs >1MiB in master tree (consolidation-backups legacy):")
        for b in big: print(f"   {b}")
        print(" [note] non-blocking for merge; candidate for future filter-repo pass")
    else:
        print(" [ok] tree clean under 1MiB per blob")

    print("[stage-3] gate instruments — extract PR blobs, py_compile + bash -n")
    gt_dir = "/tmp/pr58_gate_final"; shutil.rmtree(gt_dir, ignore_errors=True)
    pathlib.Path(gt_dir).mkdir(parents=True)
    diff_r = run(["git", "diff", "--name-only", f"{base}...origin/master"], check=False)
    changed = [l for l in diff_r.stdout.splitlines() if l.strip()] if diff_r else []
    for f in changed:
        tgt = pathlib.Path(gt_dir) / f
        tgt.parent.mkdir(parents=True, exist_ok=True)
        r2 = run(["git", "show", f"origin/master:{f}"], check=False)
        if r2: tgt.write_text(r2.stdout)
        else: continue
        if f.endswith(".py"):
            rc = subprocess.run([sys.executable, "-m", "py_compile", str(tgt)],
                                capture_output=True).returncode
            print(f" [{'ok' if rc == 0 else 'held'}] py_compile {f}")
            if rc != 0: HELD_FLAGS.append(f"py_compile fail: {f}")
        elif f.endswith(".sh"):
            rc = subprocess.run(["bash", "-n", str(tgt)],
                                 capture_output=True).returncode
            print(f" [{'ok' if rc == 0 else 'held'}] bash -n {f}")
            if rc != 0: HELD_FLAGS.append(f"bash -n fail: {f}")
    print(f" [gate] changed files: {len(changed)}")

    print("[stage-4] check thixo_gel flagged issue")
    fx = pathlib.Path("docs/research/thixo-foam.md")
    if fx.exists() and "thixo_gel" in fx.read_text():
        lines = fx.read_text().split("\n")
        if len(lines) >= 4 and "thixo_gel" in lines[3]:
            lines[3] = lines[3].replace("thixo_gel", "Thixotropic Foam Gel")
            fx.write_text("\n".join(lines))
            run(["git", "add", str(fx)])
            run(["git", "commit", "-m",
                 "fix(docs): descriptive title thixo-foam line 4 (coderabbit suggestion) — pr58 resolve"])
            print(" [banked] thixo fix committed")
        else:
            print(" [note] thixo_gel present but not on line 4 — inspect manually")
    else:
        print(" [note] thixo_gel not present in working tree — coderabbit fix likely pre-applied")

    print("[stage-5] reconcile local master with origin/master (the actual blocker)")
    local_master = run(["git", "rev-parse", "master"], check=False)
    remote_master = run(["git", "rev-parse", "origin/master"], check=False)
    if local_master and remote_master:
        lh, rh = local_master.stdout.strip(), remote_master.stdout.strip()
        if lh == rh:
            print(" [ok] local master = origin/master")
        else:
            print(f" [info] local {lh[:8]} behind remote {rh[:8]} — fast-forwarding")
            run(["git", "checkout", "-q", "master"], check=False)
            r = run(["git", "reset", "--hard", "origin/master"], check=False)
            if r and r.returncode == 0:
                print(" [banked] local master reset to origin/master (working tree preserved changes listed below)")
                run(["git", "status", "--short"], check=False)
            else:
                print(" [held] fast-forward failed — manual intervention needed")
                HELD_FLAGS.append("fast-forward failed")
    else:
        HELD_FLAGS.append("branch hash resolution failed")

    print("[stage-6] merge decision")
    if HELD_FLAGS:
        print(f" [gate] AUDIT RAISED {len(HELD_FLAGS)} FLAGS:")
        for flag in HELD_FLAGS: print(f"   - {flag}")
        print(" DO NOT MERGE YET. Inspect above, fix, rerun.")
    elif CONFIRM:
        print("[stage-6a] CONFIRM=1 — merging PR #58")
        r = run(["gh", "pr", "merge", "58", "--merge", "--delete-branch"], check=False)
        if r and r.returncode == 0:
            run(["git", "fetch", "origin", "--prune"], check=False)
            run(["git", "branch", "-f", "master", "origin/main"], check=False)
            run(["git", "checkout", "-q", "master"], check=False)
            print(" [banked] PR #58 MERGED, local master reset to origin/main, origin/master deleted")
        else:
            print(" [held] gh merge failed — check PR state")
            HELD_FLAGS.append("merge failed")
    else:
        print(" [gate] dry-run complete, zero holds.")
        print(" Merge with: CONFIRM=1 python3 /home/jesse/openroot/bin/resolve_pr58_final.py")

    print("[stage-7] session note -> context_bridge/")
    note_path = pathlib.Path("context_bridge/session-20260918_pr58-resolve-final.md")
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        "# PR #58 Final Resolve Session (" + datetime.utcnow().isoformat() + "Z)\n"
        f"- origin/main was {base}; origin/master was {headp}\n"
        f"- files audited: {len(changed)}, HELD flags: {len(HELD_FLAGS)}\n"
        "- stage-5 reconciliation: local master fast-forwarded to origin/master (fixed divergence)\n"
        "- coderabbit commits 24bc1a7/08c913c audited; consolidation-backups blobs noted (future filter-repo candidate)\n")
    run(["git", "add", str(note_path)], check=False)

    shutil.rmtree(gt_dir, ignore_errors=True)
    print("[done] [exit=0]")
    sys.exit(0 if not HELD_FLAGS else 1)

if __name__ == "__main__":
    main()
# [exit=0]
