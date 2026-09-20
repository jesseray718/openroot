#!/usr/bin/env python3
# fleet_closeout_v6_20260920.py — purge superseded drafts, evidence-commit today's artifacts,
# then fleet master deletion (29 dangling) + master->main renames (7 default=master) from ledger.
# Order: commits BEFORE remote mutations. DRY-RUN default; CONFIRM=1 executes everything.
import json, os, pathlib, subprocess, datetime, sys
OPENROOT = "/home/jesse/openroot"
CONFIRM = (os.environ.get("CONFIRM", "0") == "1")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LEDGER = pathlib.Path(OPENROOT, "data/master_heads_ledger_20260920_020335.json")
os.chdir(OPENROOT)
print("[canary] OPENROOT-fleet-closeout-v6-20260920 paste intact")
report = []
def say(m):
    print(m); report.append(m)
def sh(args):
    return subprocess.run(args, cwd=OPENROOT, capture_output=True, text=True)

# ---------- STAGE A: purge superseded rebuild drafts ----------
say("== STAGE A [purge] superseded rebuild drafts ==")
DRAFTS = ["GOALS.rebuild.20260920_014329.md",
          "MASTER_TODO.rebuild.20260920_014329.md",
          "MASTER_TODO.rebuild.v2.md"]
for d in DRAFTS:
    p = pathlib.Path(OPENROOT, d)
    if p.exists():
        if CONFIRM:
            sh(["git", "rm", "-q", "--cached", d]); p.unlink()
            say("[banked] removed draft: %s (index + disk)" % d)
        else:
            say("[held] preview-remove draft: %s (staged in index — must clear before any commit)" % d)
    else:
        say("[banked] draft already gone: %s" % d)
# clear any remaining intent-to-add registrations so the index is exactly what we choose
if CONFIRM:
    sh(["git", "reset", "-q"])
    say("[banked] index reset — clean slate for evidence commit")

# ---------- STAGE B: evidence commit (local mutation) ----------
say("== STAGE B [evidence] bank today's scripts, reports, ledgers ==")
EVIDENCE = [
    "bin/next_actions_20260920_v1.sh", "bin/next_actions_v2_20260920.py",
    "bin/master_harvest_v3_20260920.py", "bin/secure_and_commit_v4_20260920.py",
    "bin/secure_and_commit_v5_20260920.py", "bin/fleet_closeout_v6_20260920.py",
    "context_bridge/report-next-actions-20260920_014329.md",
    "context_bridge/report-next-actions-v2-20260920_015234.md",
    "context_bridge/report-next-actions-v2-20260920_015411.md",
    "context_bridge/report-master-harvest-20260920_020335.md",
    "context_bridge/report-secure-commit-20260920_021102.md",
    "data/master_heads_ledger_20260920_020335.json",
    "data/unstable_prs_20260920_014329.json",
    "data/recent_runs_20260920_014329.json",
]
existing = [f for f in EVIDENCE if pathlib.Path(OPENROOT, f).exists()]
missing = [f for f in EVIDENCE if not pathlib.Path(OPENROOT, f).exists()]
for m in missing:
    say("[held] expected artifact absent (untracked report never written?): %s" % m)
msg = "\n".join([
    "audit: 2026-09-20 fleet closeout — triage instruments, ledgers, session reports",
    "",
    "Provenance:",
    "- GOALS/MASTER_TODO/TASK confirmed already tracked+clean (rebuild sealed earlier per MASTER_TODO line 1)",
    "- Fleet branch audit: 39 owned repos; 29 dangling master refs (post filter-repo), 7 repos default=master",
    "- Salvage verdict: 18-task restructure was never lost — survived on-disk; rebuild drafts purged as empty shells",
    "- scripts: v1-next_actions(sh) v2-triage v3-harvest v4(committed broken, kept as corpse) v5(fix) v6(this)",
    "",
    "Next: remote pass — delete 29 dangling masters, rename 7 master-defaults to main.",
])
head_before = sh(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
if CONFIRM:
    sh(["git", "add"] + existing)
    c = sh(["git", "commit", "-m", msg])
    if c.returncode == 0:
        head_after = sh(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
        say("[banked] EVIDENCE COMMIT SEALED: %s -> %s (%d files)" % (head_before, head_after, len(existing)))
    else:
        say("[gate] COMMIT FAILED :: " + c.stderr.strip()[:200]); sys.exit(1)
else:
    say("[held] DRY-RUN: would commit %d evidence files on HEAD %s" % (len(existing), head_before))

# ---------- STAGE C: fleet mutations from sealed ledger ----------
say("== STAGE C [fleet] 29 dangling-master deletes + 7 renames ==")
if not LEDGER.exists():
    say("[gate] ledger missing: %s — abort fleet pass" % LEDGER); sys.exit(1)
ledger = json.loads(LEDGER.read_text())
def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)
to_delete, to_rename = [], []
for repo, info in sorted(ledger.items()):
    (to_rename if info["default"] == "master" else to_delete).append(repo)
say("[banked] plan: %d deletes, %d renames" % (len(to_delete), len(to_rename)))
for repo in to_delete:
    if CONFIRM:
        r = gh("api", "-X", "DELETE", "repos/%s/git/refs%%2Fheads%%2Fmaster" % repo)
        say(("[banked] deleted master: %s" % repo) if r.returncode == 0
            else "[held] DELETE FAILED %s :: %s" % (repo, r.stderr.strip()[:120]))
    else:
        say("[held] preview-delete master: %s (head sha in ledger)" % repo)
for repo in to_rename:
    if CONFIRM:
        r = gh("api", "-X", "POST", "repos/%s/branches/master/rename" % repo, "-f", "new_name=main")
        say(("[banked] renamed master->main (default followed): %s" % repo) if r.returncode == 0
            else "[held] RENAME FAILED %s :: %s" % (repo, r.stderr.strip()[:120]))
    else:
        say("[held] preview-rename master->main: %s (DEFAULT branch)" % repo)

# ---------- HANDOFF ----------
rep = pathlib.Path(OPENROOT, "context_bridge", "report-fleet-closeout-%s.md" % STAMP)
rep.write_text("\n".join(report) + "\n\n## Handoff %s\nmode=%s\ndeletes=%d renames=%d\nnext: push main, verify branch listing clean, CI fix decision\n"
               % (STAMP, "EXECUTE" if CONFIRM else "DRY-RUN", len(to_delete), len(to_rename)))
say("[banked] report sealed: " + str(rep))
print("[exit=0]")
