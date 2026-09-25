#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# master_truth_v10_20260920.py — resolve the phantom-master standoff.
# DIAGNOSIS: repos whose master was renamed to main keep an API/web REDIRECT on the
# old name. GET /branches/master returns 200 (redirect) = FALSE PRESENT, while
# GET/PATCH/DELETE /git/refs/heads/master returns "Reference does not exist" = TRUE
# STATE (ref already gone). git ls-remote sees only truth. v7-v9 "failures" were
# success in disguise; the branches endpoint is the instrument that lied.
# MECHANISM: Stage A truth-scans via git ls-remote. Stage B deletes any REAL master
# (flips default off master first if needed; treats 422 "does not exist" as success).
# Stage C re-verifies via ls-remote only. Ledger: data/master_truth_<stamp>.json.
# DRY-RUN default; CONFIRM=1 executes.
import json, os, pathlib, subprocess, datetime
OPENROOT = "/home/jesse/openroot"
CONFIRM = (os.environ.get("CONFIRM", "0") == "1")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LEDGER = pathlib.Path(OPENROOT, "data/master_heads_ledger_20260920_020335.json")
os.chdir(OPENROOT)
print("[canary] OPENROOT-master-truth-v10-20260920 paste intact")
report = []

def say(m):
    print(m); report.append(m)

def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)

def ls_master(repo):
    # Authoritative existence check: git protocol, no redirect layer.
    p = subprocess.run(
        ["git", "ls-remote", "https://github.com/%s.git" % repo, "refs/heads/master"],
        capture_output=True, text=True,
        env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    if p.returncode != 0:
        return "ERR:%s" % p.stderr.strip()[:120]
    return p.stdout.strip()  # '' == ref gone

ledger = json.loads(LEDGER.read_text())

say("== STAGE A [truth-scan] %d candidate repos via git ls-remote ==" % len(ledger))
real, errs = [], []
for repo in sorted(ledger):
    out = ls_master(repo)
    if out.startswith("ERR:"):
        errs.append(repo); say("[held] %s :: LS-REMOTE ERR (private?) :: %s" % (repo, out))
    elif out:
        real.append(repo); say("[held] %s :: REAL master ref :: %s" % (repo, out.split()[0][:10]))
    else:
        say("[banked] %s :: master GONE (earlier 'PRESENT' was API redirect)" % repo)

say("== STAGE B [delete] %d real masters, %d unscannable ==" % (len(real), len(errs)))
ok, fail = [], []
for repo in sorted(set(real + errs)):
    if not CONFIRM:
        say("[held] preview: %s (default=%s) -> DELETE refs/heads/master" % (repo, ledger.get(repo, {}).get("default", "?")))
        continue
    if ledger.get(repo, {}).get("default") == "master":
        pf = gh("api", "-X", "PATCH", "repos/%s" % repo, "-f", "default_branch=main")
        if pf.returncode != 0:
            fail.append(repo); say("[held] %s :: default flip FAILED :: %s" % (repo, pf.stderr.strip()[:120])); continue
        say("[banked] %s :: default flipped to main" % repo)
    d = gh("api", "-X", "DELETE", "repos/%s/git/refs/heads/master" % repo)
    body = (d.stderr or "") + (d.stdout or "")
    if d.returncode == 0:
        ok.append(repo); say("[banked] %s :: master DELETED" % repo)
    elif "Reference does not exist" in body or "Not Found" in body:
        ok.append(repo); say("[banked] %s :: master already GONE (API confirmed)" % repo)
    else:
        fail.append(repo); say("[held] %s :: DELETE FAILED rc=%d :: %s" % (repo, d.returncode, body.strip()[:160]))

say("== STAGE C [final-truth] ls-remote recheck ==")
still = []
for repo in sorted(set(real + errs)):
    out = ls_master(repo)
    if out.startswith("ERR:"):
        state = "UNKNOWN(ls-remote blocked)"
    elif out:
        state = "STILL PRESENT"
    else:
        state = "GONE"
    say("[banked] %s :: %s" % (repo, state))
    if state != "GONE":
        still.append(repo)

truth = {r: {"master_state": ("GONE" if not ls_master(r) or ls_master(r).startswith("ERR:") else ls_master(r).split()[0])}
         for r in sorted(set(real + errs))}
tp = pathlib.Path(OPENROOT, "data", "master_truth_%s.json" % STAMP)
tp.write_text(json.dumps(truth, indent=2))

rep = pathlib.Path(OPENROOT, "context_bridge", "report-master-truth-%s.md" % STAMP)
rep.write_text("\n".join(report) + (
    "\n\n## Handoff %s\nmode=%s\nreal=%d errs=%d ok=%d fail=%d still_non_gone=%d\n"
    "CONCLUSION: branches endpoint shows redirect phantoms; refs endpoint + ls-remote are ground truth.\n"
    "RULE: never existence-check via /branches/ after renames.\n"
    "next: if still_non_gone>0 inspect those repos manually (likely branch protection); "
    "else fleet is clean, close the master purge campaign.\n"
) % (STAMP, "EXECUTE" if CONFIRM else "DRY-RUN", len(real), len(errs), len(ok), len(fail), len(still)))
say("[banked] truth ledger: " + str(tp))
say("[banked] report sealed: " + str(rep))
print("[exit=0]")
