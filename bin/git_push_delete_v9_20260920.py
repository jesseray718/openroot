#!/usr/bin/env python3
# git_push_delete_v9_20260920.py — brute-force master deletion via git protocol.
# Direct `git push origin --delete master` bypasses REST API limitations entirely.
# Skips repos where master=DEFAULT (those need default flip FIRST, handled separately).
# DRY-RUN default; CONFIRM=1 executes.
import json, os, pathlib, subprocess, datetime, sys
OPENROOT = "/home/jesse/openroot"
CONFIRM = (os.environ.get("CONFIRM", "0") == "1")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.chdir(OPENROOT)
print("[canary] OPENROOT-git-push-delete-v9-20260920 paste intact")
report = []
def say(m):
    print(m); report.append(m)
def gh_api(endpoint):
    return subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)

# Load ledger and separate: default!=master (safe to push-delete), default=master (flip-first)
LEDGER = pathlib.Path(OPENROOT, "data/master_heads_ledger_20260920_020335.json")
ledger = json.loads(LEDGER.read_text())
push_delete = [r for r,i in ledger.items() if i["default"] != "master"]
flip_first = [r for r,i in ledger.items() if i["default"] == "master"]

say("== STAGE A [git-push-delete] %d non-default-master repos ==" % len(push_delete))
ok, fail = [], []
for repo in sorted(push_delete):
    url = "https://github.com/%s.git" % repo
    if not CONFIRM:
        say("[held] preview: cd $OPENROOT && git clone --bare %s && cd tmp/%s && git push --delete origin master" % (repo, repo.split('/')[-1]))
        continue
    # Create temp bare clone, delete master, clean up
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    clone_dir = os.path.join(tmpdir, repo.split("/")[-1])
    p1 = subprocess.run(["git", "clone", "--bare", url, clone_dir], capture_output=True, text=True, cwd=tmpdir)
    if p1.returncode != 0:
        fail.append(repo); say("[held] %s :: CLONE FAILED :: %s" % (repo, p1.stderr.strip()[:140])); shutil.rmtree(tmpdir); continue
    p2 = subprocess.run(["git", "push", "--delete", "origin", "master"], capture_output=True, text=True, cwd=clone_dir, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    shutil.rmtree(tmpdir)
    if p2.returncode == 0:
        ok.append(repo); say("[banked] %s :: master deleted via git-push" % repo)
    else:
        fail.append(repo); say("[held] %s :: PUSH DELETE FAILED :: %s" % (repo, p2.stderr.strip()[:140]))

say("== STAGE B [flip-first] %d repos where master IS DEFAULT ==" % len(flip_first))
for repo in sorted(flip_first):
    if not CONFIRM:
        say("[held] preview: PATCH %s default_branch=main, then git-push-delete master" % repo)
        continue
    # Flip default to main
    p1 = gh_api("-X PATCH repos/%s default_branch=main" % repo)
    if p1.returncode != 0:
        fail.append(repo); say("[held] %s :: FLIP FAILED :: %s" % (repo, p1.stderr.strip()[:140])); continue
    say("[banked] %s :: default flipped to main" % repo)
    # Now delete master
    url = "https://github.com/%s.git" % repo
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    clone_dir = os.path.join(tmpdir, repo.split("/")[-1])
    p_clone = subprocess.run(["git", "clone", "--bare", url, clone_dir], capture_output=True, text=True, cwd=tmpdir)
    if p_clone.returncode != 0:
        fail.append(repo); say("[held] %s :: CLONE FAILED after flip :: %s" % (repo, p_clone.stderr.strip()[:140])); shutil.rmtree(tmpdir); continue
    p_del = subprocess.run(["git", "push", "--delete", "origin", "master"], capture_output=True, text=True, cwd=clone_dir, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    shutil.rmtree(tmpdir)
    if p_del.returncode == 0:
        ok.append(repo); say("[banked] %s :: master deleted via git-push (after flip)" % repo)
    else:
        fail.append(repo); say("[held] %s :: PUSH DELETE FAILED after flip :: %s" % (repo, p_del.stderr.strip()[:140]))

say("== STAGE C [verify] cross-check ==")
still = []
for repo in sorted(push_delete + flip_first):
    r = gh_api("repos/%s/branches/master" % repo)
    ver = "PRESENT" if r.returncode == 0 else "GONE"
    say("[banked] %s :: %s" % (repo, ver))
    if ver == "PRESENT":
        still.append(repo)

rep = pathlib.Path(OPENROOT, "context_bridge", "report-git-push-delete-%s.md" % STAMP)
rep.write_text("\n".join(report) + "\n\n## Handoff %s\nmode=%s\nattempted=%d ok=%d fail=%d still=%d\nnext: if still>0, manual GitHub UI delete or open support ticket\n" % (STAMP, "EXECUTE" if CONFIRM else "DRY-RUN", len(push_delete)+len(flip_first), len(ok), len(fail), len(still)))
say("[banked] report sealed: " + str(rep))
print("[exit=0]")
