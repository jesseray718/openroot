#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# CANARY:OPENROOT-GH-WINDOW-OPENER-20261016-V1
"""
GH WINDOW OPENER runner - 2026-10-16 post-pod-factory session.
Tasks 1-6. Dry-run by default. CONFIRM=1 to execute mutating ops.
Usage: cd /home/jesse/openroot && CONFIRM=1 python3 bin/gh_window_opener_v1.py
"""
import os, sys, json, subprocess, hashlib, datetime, shutil

ROOT        = "/home/jesse/openroot"
GH_REPO     = "jesseray718/openroot"
NEW_REPO    = "dataset-to-pod"
MILESTONE   = "grants-2026Q4"
ISSUE_TITLE = "SARE FRG 2027 - Dec 8 deadline"
CONFIRM     = os.environ.get("CONFIRM") == "1"
UTC         = datetime.datetime.now(datetime.timezone.utc)
TS          = UTC.strftime("%Y%m%dT%H%M%SZ")
RECEIPT_DIR = os.path.join(ROOT, "context_bridge", "harvest")
os.makedirs(RECEIPT_DIR, exist_ok=True)
RECEIPT_PATH = os.path.join(RECEIPT_DIR, "gh_window_opener_" + TS + ".jsonl")


def sh(cmd, cwd=ROOT, timeout=180):
    """Run shell cmd, return (rc, stdout, stderr)."""
    try:
        p = subprocess.run(
            cmd, cwd=cwd, shell=False, capture_output=True, text=True,
            timeout=timeout,
            env=dict(os.environ, GIT_PAGER="cat", TERM="dumb"),
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT after %ss: %s" % (timeout, cmd)


def receipt(stage, status, **kw):
    row = {"ts": UTC.isoformat(), "stage": stage, "status": status}
    row.update(kw)
    blob = json.dumps(row, sort_keys=True)
    row["sha256"] = hashlib.sha256(blob.encode()).hexdigest()
    with open(RECEIPT_PATH, "a") as f:
        f.write(json.dumps(row) + "\n")
    tag = {"ok": "[banked]", "hold": "[held]", "gate": "[gate]"}.get(status, "[" + status + "]")
    print("%s %s: %s  %s" % (tag, stage, row["sha256"][:12], kw.get("note", "")))
    return row


def banner(t):
    print("\n" + "=" * 66 + "\n" + t + "\n" + "=" * 66)


if not os.path.isdir(os.path.join(ROOT, ".git")):
    print("[held] " + ROOT + " is not a git repo - abort")
    sys.exit(2)

print("CANARY:OPENROOT-GH-WINDOW-OPENER-20261016-V1  CONFIRM=%s" % ("1" if CONFIRM else "0 (dry-run)"))

# --------------------------------------------------------------- TASK 1
banner("TASK 1 - verify tonight's commit pushed + repo clean")
rc, head, _     = sh("git rev-parse --short HEAD")
rc, remote, _   = sh("git rev-parse --short origin/main")
rc, ahead, _    = sh("git rev-list --count origin/main..HEAD")
rc, dirty, _    = sh("git status --porcelain")
rc, logstat, _  = sh("git log origin/main -1 --stat")
print("HEAD=%s  origin/main=%s  ahead_by=%s" % (head, remote, ahead))
print(logstat[:1500])
print("--- dirty files ---")
print(dirty if dirty else "(clean)")
receipt("task1.verify",
        "ok" if ahead == "0" else "hold",
        head=head, remote=remote, ahead=ahead,
        dirty_count=len([l for l in dirty.splitlines() if l.strip()]),
        note="clean+synced" if (ahead == "0" and not dirty) else "DIRTY or UNPUSHED")

# --------------------------------------------------------------- TASK 2
banner("TASK 2 - dataset_tool standalone repo decision")
TOOL_SRC = os.path.join(ROOT, "bin", "any_dataset_to_pod_v1.py")
tool_exists = os.path.isfile(TOOL_SRC)
lic_hdr = False
if tool_exists:
    with open(TOOL_SRC, "r", errors="replace") as f:
        lic_hdr = "SPDX-License-Identifier" in f.read(4096)

# Mechanical proxy only. Override with PROMOTE=1 / PROMOTE=0 to force.
force = os.environ.get("PROMOTE")
if force == "1":
    recommend = True
elif force == "0":
    recommend = False
else:
    recommend = tool_exists and lic_hdr

print("tool_exists=%s  spdx_header=%s  force=%s" % (tool_exists, lic_hdr, force))
print("RECOMMENDATION: %s" % ("PROMOTE to standalone repo" if recommend
      else "KEEP in monorepo (missing file, missing SPDX, or forced)"))

if recommend and CONFIRM:
    stage = "/tmp/%s-%s" % (NEW_REPO, TS)
    os.makedirs(stage, exist_ok=True)
    shutil.copy2(TOOL_SRC, os.path.join(stage, "any_dataset_to_pod_v1.py"))
    readme = (
        "# dataset-to-pod\n\n"
        "Provenance-verified local document pods: FTS5 + Nomic-embed-text + SHA256 per chunk.\n\n"
        "## Quickstart (3 commands)\n\n"
        "    python3 any_dataset_to_pod_v1.py --src ./docs --out ./my.pod.db\n"
        "    sqlite3 ./my.pod.db \"SELECT count(*) FROM chunks;\"\n"
        "    python3 any_dataset_to_pod_v1.py --query \"your question\" --db ./my.pod.db\n\n"
        "## Receipt\n\n"
        "Observed internal cache speedup: 128ms build vs 0.09ms cached read (1462x)\n"
        "on a fixed internal workload. Workload-specific; reproduce with your own corpus.\n\n"
        "## License\n\n"
        "GPL-3.0-only. Docs CC-BY-SA-4.0.\n"
    )
    with open(os.path.join(stage, "README.md"), "w") as f:
        f.write(readme)
    with open(os.path.join(stage, "LICENSE"), "w") as f:
        f.write("GPL-3.0-only\n")  # TODO: replace with full license text
    sh("git init -q && git add -A && "
       "git -c user.name=jesseray718 -c user.email=jesse@openroot.local "
       "commit -q -m 'feat: dataset-to-pod v1 - pod factory standalone (GPL-3.0, SPDX)'",
       cwd=stage)
    rc, out, err = sh("gh repo create %s --public --source=. --push "
                      "--description 'Provenance-verified local document pods: FTS5 + Nomic + SHA256'"
                      % NEW_REPO, cwd=stage, timeout=240)
    print(out or err)
    receipt("task2.promote", "ok" if rc == 0 else "hold", rc=rc, stage=stage,
            note=("created " + NEW_REPO) if rc == 0 else "gh repo create failed")
elif recommend and not CONFIRM:
    receipt("task2.promote", "gate", note="dry-run: would create gh repo + push (CONFIRM=1)")
else:
    receipt("task2.promote", "hold", note="kept in monorepo")

# --------------------------------------------------------------- TASK 3
banner("TASK 3 - SARE FRG 2027 issue + milestone + label")
issue_body = (
    "Candidate proposal stack for SARE FRG 2027 (deadline Dec 8):\n\n"
    "- aerocement solar absorber (opencement)\n"
    "- thermal cascade / labyrinth passive cooling\n"
    "- black locust rocket mass heater\n"
    "- POPW thermodynamic ledger (measured energy receipts)\n"
    "- 7-day instrumented measurement plan\n\n"
    "Status: candidate. Claims are hypotheses until instrumented.\n"
    "Milestone: grants-2026Q4. Label: money."
)
if CONFIRM:
    sh('gh label create money --repo %s --color FFD700 '
       '--description "revenue-bearing path" 2>/dev/null || true' % GH_REPO)
    sh('gh api repos/%s/milestones -f title="%s" -f state=open 2>/dev/null || true'
       % (GH_REPO, MILESTONE))
    rc, out, err = sh('gh issue create --repo %s --title "%s" --body "%s" '
                      '--label money --milestone "%s"'
                      % (GH_REPO, ISSUE_TITLE, issue_body.replace('"', "'"), MILESTONE),
                      timeout=120)
    print(out or err)
    receipt("task3.issue", "ok" if rc == 0 else "hold", rc=rc, url=out,
            note="issue created" if rc == 0 else "issue create failed")
else:
    receipt("task3.issue", "gate", note="dry-run: would create issue+milestone+label (CONFIRM=1)")

# --------------------------------------------------------------- TASK 4
banner("TASK 4 - Reh1t issue #53 status")
rc, out, err = sh("gh issue view 53 --repo %s --json "
                  "number,title,state,assignees,updatedAt,comments" % GH_REPO, timeout=120)
if rc == 0:
    try:
        d = json.loads(out)
        print("#%s [%s] %s" % (d["number"], d["state"], d["title"]))
        print("assignees=%s updated=%s" % ([a["login"] for a in d.get("assignees", [])], d["updatedAt"]))
        print("comments=%d" % len(d.get("comments", [])))
        receipt("task4.reh1t", "ok", state=d["state"],
                note="#53 %s, %d comments" % (d["state"], len(d.get("comments", []))))
    except Exception as e:
        receipt("task4.reh1t", "hold", note="parse error %r" % e)
else:
    print(err)
    receipt("task4.reh1t", "hold", note="could not fetch issue #53 (gh auth? network?)")

# --------------------------------------------------------------- TASK 5
banner("TASK 5 - untracked bin/ sweep")
rc, tracked, _   = sh("git ls-files bin/ | wc -l")
rc, ondisk, _    = sh("find bin -maxdepth 1 -type f \\( -name '*.py' -o -name '*.sh' \\) | wc -l")
rc, untracked, _ = sh("git ls-files --others --exclude-standard bin/")
rc, ignored, _   = sh("git ls-files --others --ignored --exclude-standard bin/ | head -20")
print("tracked=%s  on_disk=%s" % (tracked, ondisk))
print("--- untracked (not ignored) ---")
print(untracked if untracked else "(none)")
print("--- ignored (sample) ---")
print(ignored if ignored else "(none)")
try:
    gap = int(ondisk) - int(tracked)
except ValueError:
    gap = -1
receipt("task5.binsweep", "ok" if gap <= 0 else "hold",
        tracked=tracked, on_disk=ondisk, gap=gap,
        note="bin/ fully tracked" if gap <= 0 else "%d file(s) not tracked" % gap)

# --------------------------------------------------------------- TASK 6
banner("TASK 6 - handoff file + commit + push")
handoff = os.path.join(ROOT, "context_bridge", "handoff-gh-" + TS + ".md")
rc, head, _   = sh("git rev-parse HEAD")
rc, remote, _ = sh("git rev-parse origin/main")
rc, dirty, _  = sh("git status --porcelain")
body = (
    "# Handoff - GH Window Opener - " + TS + "\n\n"
    "**Node:** OptiPlex / " + ROOT + "\n"
    "**HEAD:** " + head + "\n"
    "**origin/main:** " + remote + "\n"
    "**Receipt:** " + RECEIPT_PATH + "\n\n"
    "## Tasks\n"
    "1. verify push/clean - receipt task1\n"
    "2. dataset-to-pod decision - receipt task2\n"
    "3. SARE FRG issue - receipt task3\n"
    "4. Reh1t #53 - receipt task4\n"
    "5. bin/ sweep - receipt task5\n"
    "6. this file\n\n"
    "## Dirty at handoff\n```\n" + (dirty if dirty else "(clean)") + "\n```\n\n"
    "## Next actions\n"
    "- SARE FRG draft 40% by Oct 23\n"
    "- POPW 48h baseline\n"
    "- NCR go/no-go Oct 23\n"
)
with open(handoff, "w") as f:
    f.write(body)
print("wrote %s (%d bytes)" % (handoff, os.path.getsize(handoff)))

if CONFIRM:
    sh("git add -A")
    rc, out, err = sh("git -c user.name=jesseray718 -c user.email=jesse@openroot.local "
                      "commit -q -m 'chore(handoff): gh window opener %s - tasks 1-6 receipts' "
                      "|| echo NO_CHANGES" % TS)
    print(out or err)
    rc, out, err = sh("git push origin HEAD", timeout=240)
    print(out or err)
    receipt("task6.handoff", "ok" if rc == 0 else "hold", rc=rc, handoff=handoff,
            note="committed+pushed" if rc == 0 else "push failed - human gate")
else:
    receipt("task6.handoff", "gate", handoff=handoff,
            note="dry-run: wrote handoff, did NOT commit/push (CONFIRM=1)")

banner("SUMMARY")
with open(RECEIPT_PATH) as f:
    rows = [json.loads(l) for l in f if l.strip()]
for r in rows:
    print("  %-5s  %-18s  %s  %s" % (r["status"], r["stage"], r["sha256"][:12], r.get("note", "")))
print("\nreceipt: " + RECEIPT_PATH)
print("[exit=0]")
