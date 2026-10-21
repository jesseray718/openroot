#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# master_purge_v7_20260920.py — retry fleet master purge via correct mechanisms:
#   A) 29 dangling-master deletes: REST unencoded path -> git push --delete fallback
#   B) 3 both-branch repos (agape-primitives, etaledger, fractallattice): default->main
#      via PATCH, then master delete through same mechanism
# DRY-RUN default; CONFIRM=1 executes.
import os, subprocess, datetime, pathlib, sys
OPENROOT = "/home/jesse/openroot"
CONFIRM = (os.environ.get("CONFIRM", "0") == "1")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.chdir(OPENROOT)
print("[canary] OPENROOT-master-purge-v7-20260920 paste intact")
report = []
def say(m):
    print(m); report.append(m)
def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)

LEDGER = pathlib.Path(OPENROOT, "data/master_heads_ledger_20260920_020335.json")
import json
ledger = json.loads(LEDGER.read_text())

# classes
both_exist = ["agape-primitives", "etaledger", "fractallattice"]  # 422 rename fails: main taken
delete_targets = [r for r, i in ledger.items()
                  if i["default"] != "master" and not r.split("/")[-1] in both_exist]

def kill_master(repo):
    """Try 3 deletion mechanisms in order, return True on success."""
    owner, name = repo.split("/")
    # mech 1: REST, unencoded path (older gh mangles %2F)
    r = gh("api", "-X", "DELETE", "repos/%s/git/refs/heads/master" % repo)
    if r.returncode == 0:
        return "rest-unencoded"
    # mech 2: git push --delete over https, using gh credential helper
    p = subprocess.run(["git", "push", "https://github.com/%s.git" % repo, "--delete", "master"],
                        capture_output=True, text=True,
                        env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    if p.returncode == 0:
        return "git-push"
    return None

say("== STAGE A [retry-delete] %d dangling masters ==" % len(delete_targets))
ok, fail = [], []
for repo in sorted(delete_targets):
    if not CONFIRM:
        say("[held] preview-delete: %s" % repo)
        continue
    how = kill_master(repo)
    if how:
        ok.append(repo); say("[banked] deleted master via %s: %s" % (how, repo))
    else:
        fail.append(repo); say("[held] STILL FAILING %s — likely default-branch protection or perm issue; check repo settings" % repo)

say("== STAGE B [default-flip] 3 both-branch repos ==")
for name in both_exist:
    repo = "jesseray718/" + name
    if not CONFIRM:
        say("[held] preview: PATCH %s default_branch=main, then delete master" % repo)
        continue
    p = gh("api", "-X", "PATCH", "repos/%s" % repo, "-f", "default_branch=main")
    if p.returncode != 0:
        say("[held] PATCH FAILED %s :: %s" % (repo, p.stderr.strip()[:120])); continue
    say("[banked] default branch flipped to main: %s" % repo)
    how = kill_master(repo)
    say("[banked] master deleted via %s" % how if how else "[held] master delete still failing: %s — repo is now on main, master harmless-but-stale" % repo)

say("== STAGE C [verify] ==")
if CONFIRM:
    for repo in sorted(set(delete_targets + ["jesseray718/" + b for b in both_exist])):
        r = gh("api", "repos/%s/branches/master" % repo)
        say("[banked] %s: master %s" % (repo, "STILL PRESENT" if r.returncode == 0 else "gone"))

rep = pathlib.Path(OPENROOT, "context_bridge", "report-master-purge-%s.md" % STAMP)
rep.write_text("\n".join(report) + "\n\n## Handoff %s\nmode=%s\nok=%d fail=%d\nnext: if fail>0, inspect branch protection per-repo; verify defaults fleet-wide\n" % (STAMP, "EXECUTE" if CONFIRM else "DRY-RUN", len(ok), len(fail)))
say("[banked] report sealed: " + str(rep))
print("[exit=0]")
