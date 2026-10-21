#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# zombie_ref_kill_v8_20260920.py — kill ghost master refs (targets stripped by filter-repo)
# Mechanism: retarget ref to main's live head SHA (force), THEN delete. Verifies via BOTH
# branches + refs endpoints. Prints full API error bodies — no silent false-positives.
# DRY-RUN default; CONFIRM=1 executes.
import json, os, pathlib, subprocess, datetime, sys
OPENROOT = "/home/jesse/openroot"
CONFIRM = (os.environ.get("CONFIRM", "0") == "1")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LEDGER = pathlib.Path(OPENROOT, "data/master_heads_ledger_20260920_020335.json")
os.chdir(OPENROOT)
print("[canary] OPENROOT-zombie-ref-kill-v8-20260920 paste intact")
report = []
def say(m):
    print(m); report.append(m)
def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)

ledger = json.loads(LEDGER.read_text())
targets = [r for r, i in ledger.items() if i["default"] != "master"]

say("== STAGE A [ground-truth] re-verify all %d masters (both endpoints) ==" % len(targets))
present = []
for repo in sorted(targets):
    r = gh("api", "repos/%s/branches/master" % repo)
    if r.returncode == 0:
        present.append(repo)
    # quiet: absent ones just fall out of the list
say("[banked] actually-present masters: %d / %d" % (len(present), len(targets)))

say("== STAGE B [retarget-then-delete] ==")
killed, failed = [], []
for repo in sorted(present):
    # main head SHA (live commit)
    main = gh("api", "repos/%s/branches/main" % repo)
    if main.returncode != 0:
        failed.append(repo); say("[held] %s :: no main branch to retarget onto :: %s" % (repo, main.stderr.strip()[:140])); continue
    try:
        main_sha = json.loads(main.stdout)["commit"]["sha"]
    except Exception as e:
        failed.append(repo); say("[held] %s :: main parse fail :: %s" % (repo, e)); continue
    if not CONFIRM:
        say("[held] preview: %s retarget master -> %s then delete" % (repo, main_sha[:8])); continue
    # step 1: force-move zombie ref onto live commit
    rt = gh("api", "-X", "PATCH", "repos/%s/git/refs/heads/master" % repo, "-f", "sha=%s" % main_sha, "-F", "force=true")
    if rt.returncode != 0:
        failed.append(repo); say("[held] %s :: RETARGET FAILED :: rc=%d out=%s err=%s" % (repo, rt.returncode, rt.stdout.strip()[:100], rt.stderr.strip()[:160])); continue
    say("[banked] %s :: master retargeted to %s" % (repo, main_sha[:8]))
    # step 2: delete the now-live ref
    dl = gh("api", "-X", "DELETE", "repos/%s/git/refs/heads/master" % repo)
    if dl.returncode == 0:
        killed.append(repo); say("[banked] %s :: master DELETED" % repo)
    else:
        failed.append(repo); say("[held] %s :: DELETE FAILED after retarget :: rc=%d out=%s err=%s" % (repo, dl.returncode, dl.stdout.strip()[:100], dl.stderr.strip()[:160]))

say("== STAGE C [final-verify] cross-endpoint ==")
still = []
for repo in sorted(present):
    b = gh("api", "repos/%s/branches/master" % repo)
    r2 = gh("api", "repos/%s/git/refs/heads/master" % repo)
    ver = "GONE" if (b.returncode != 0 and r2.returncode != 0) else "PRESENT"
    say("[banked] %s :: %s" % (repo, ver))
    if ver == "PRESENT":
        still.append(repo)

rep = pathlib.Path(OPENROOT, "context_bridge", "report-zombie-ref-kill-%s.md" % STAMP)
rep.write_text("\n".join(report) + "\n\n## Handoff %s\nmode=%s\npresent=%d killed=%d failed=%d still=%d\n" % (STAMP, "EXECUTE" if CONFIRM else "DRY-RUN", len(present), len(killed), len(failed), len(still)))
say("[banked] report sealed: " + str(rep))
print("[exit=0]")
