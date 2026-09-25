#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# next_actions_v2_20260920.py — stale-master triage (delete-if-behind), forks excluded;
# widened GOALS/MASTER_TODO salvage. Dry-run default, CONFIRM=1 executes deletions.
import json, os, subprocess, sys, datetime, hashlib, pathlib, re

OPENROOT = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.chdir(OPENROOT)
print("[canary] OPENROOT-next-actions-v2-20260920 paste intact")

def gh(*args, ok_none=False):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None if ok_none else sys.exit(f"[gate] gh failed: {' '.join(args)} :: {r.stderr.strip()}")
    return r.stdout.strip()

report = []
def say(msg):
    print(msg); report.append(msg)

# ---------- STAGE A: master vs default-branch ancestry, owned repos only ----------
say("== STAGE A [branch-triage] forks excluded ==")
repos = json.loads(gh("repo", "list", "jesseray718", "--limit", "300",
                      "--json", "nameWithOwner,isFork,defaultBranchRef"))
owned = [r for r in repos if not r["isFork"]]
say(f"[banked] {len(repos)} total, {len(owned)} owned (non-fork), {len(repos)-len(owned)} forks skipped")

plan_delete, plan_hold, plan_rename = [], [], []
for r in owned:
    repo = r["nameWithOwner"]
    default = (r.get("defaultBranchRef") or {}).get("name", "") or "main"
    if gh("api", f"repos/{repo}/branches/master", ok_none=True) is None:
        continue  # no master — done
    if default == "master":
        plan_rename.append(repo)
        say(f"[held] {repo}: master is DEFAULT branch — rename path required, not delete")
        continue
    try:
        cmp = json.loads(gh("api", f"repos/{repo}/compare/{default}...master"))
    except SystemExit:
        plan_hold.append(repo); say(f"[held] {repo}: compare failed — manual look"); continue
    ahead, behind = cmp.get("ahead_by", -1), cmp.get("behind_by", -1)
    if ahead == 0:
        plan_delete.append((repo, behind))
        say(f"[{'banked' if CONFIRM else 'held'}] {repo}: master 0-ahead of {default} (behind {behind}) — STALE, safe delete")
    else:
        plan_hold.append(repo)
        say(f"[held] {repo}: master AHEAD by {ahead} — possible orphaned pre-prune work, DO NOT DELETE")

if CONFIRM:
    for repo, behind in plan_delete:
        try:
            gh("api", "-X", "DELETE", f"repos/{repo}/git/refs%2Fheads%2Fmaster")
            say(f"[banked] {repo}: stale master deleted")
        except SystemExit:
            say(f"[held] {repo}: delete failed (branch protection?) — manual")
else:
    say(f"[held] DRY-RUN: {len(plan_delete)} stale-master deletions previewed; rerun with CONFIRM=1 to execute")

# ---------- STAGE B: widened salvage across ALL context_bridge ----------
say("== STAGE B [salvage-v2] all context_bridge sources ==")
cb = pathlib.Path(OPENROOT, "context_bridge")
sources = sorted(cb.glob("*.md")) + sorted(cb.glob("*.log"))
tasks = set()
pat = re.compile(r"^[-*+] \[[ xX]\]\s+(.{3,})|^\s*\d+\)\s+(.{3,})", re.M)
for f in sources:
    try:
        txt = f.read_text(errors="ignore")
    except OSError:
        continue
    for m in pat.finditer(txt):
        t = (m.group(1) or m.group(2)).strip()
        if t and not t.startswith("http"):
            tasks.add(t[:200])
for stray in ["GOALS.md", "MASTER_TODO.md", "TASK.md"]:
    p = pathlib.Path(OPENROOT, stray)
    if p.exists():
        say(f"[banked] on-disk remnant found: {stray} ({p.stat().st_size} bytes) — diff vs draft before overwrite")

salvage = pathlib.Path(OPENROOT, f"data/salvaged_tasks_v2_{STAMP}.txt")
salvage.write_text("\n".join(sorted(tasks)))
sha = hashlib.sha256(salvage.read_bytes()).hexdigest()
say(f"[banked] {len(sources)} sources scanned -> {len(tasks)} unique tasks -> {salvage}")
say(f"[gate] salvage sha256={sha}" +
    ("  [EMPTY — 18-task restructure is a permanent known-loss; rebuild from boot-seed queue]"
     if not tasks else ""))

draft = pathlib.Path(OPENROOT, "MASTER_TODO.rebuild.v2.md")
draft.write_text("# MASTER_TODO.md rebuild draft v2\n- status: draft | generated: "
                 + STAMP + "\n## Recovered Tasks\n"
                 + "\n".join(f"- {t}" for t in sorted(tasks)) + "\n")
subprocess.run(["git", "add", "-N", str(draft)], cwd=OPENROOT)
say(f"[held] {draft} written ({len(tasks)} tasks), staged add-N — human commit gate applies")

# ---------- STAGE C: handoff ----------
rep = pathlib.Path(cb, f"report-next-actions-v2-{STAMP}.md")
rep.write_text("\n".join(report)
               + f"\n\n## Handoff {STAMP}\nmode={'EXECUTE' if CONFIRM else 'DRY-RUN'}\n"
               + f"plan: {len(plan_delete)} deletes, {len(plan_rename)} renames-needed, {len(plan_hold)} held\n"
               + "next: verify held-list (ahead-masters may hide orphaned work); commit MASTER_TODO if salvage non-empty\n")
print(f"[banked] report sealed: {rep}")
print("[exit=0]")
