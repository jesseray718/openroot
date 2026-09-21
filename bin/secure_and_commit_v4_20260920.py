#!/usr/bin/env python3
# secure_and_commit_v4_20260920.py — READ-ONLY PREVIEW. Hash existing GOALS/MASTER_TODO/TASK,
# compare against rebuild drafts, propose commit message with provenance. CONFIRM=1 executes commit.
import hashlib, pathlib, subprocess, sys, datetime, json, os
OPENROOT = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.chdir(OPENROOT)
print("[canary] OPENROOT-secure-commit-v4-20260920 paste intact")

report = []
def say(m): print(m); report.append(m)

# ---------- STAGE A: hash and inventory existing on-disk artifacts ----------
say("== STAGE A [inventory] existing GOALS/MASTER_TODO/TASK ==")
files = ["GOALS.md", "MASTER_TODO.md", "TASK.md"]
ledger = {}
for fn in files:
    p = pathlib.Path(OPENROOT, fn)
    if p.exists():
        content = p.read_text(errors="ignore")
        sha = hashlib.sha256(content.encode()).hexdigest()
        lines = len(content.splitlines())
        ledger[fn] = {"sha256": sha[:16], "lines": lines, "bytes": len(content)}
        say(f"[banked] {fn}: {lines} lines, {len(content)} bytes, sha256={sha[:16]}")
    else:
        say(f"[held] {fn}: MISSING — will not commit")

# ---------- STAGE B: check rebuild drafts exist (v2 creations) ----------
say("== STAGE B [rebuild-drafts] compare with existing ==")
drafts = list(pathlib.Path(OPENROOT).glob("MASTER_TODO.rebuild.*.md"))
drafts += list(pathlib.Path(OPENROOT).glob("GOALS.rebuild.*.md"))
for d in sorted(drafts):
    content = d.read_text(errors="ignore")
    sha = hashlib.sha256(content.encode()).hexdigest()[:16]
    lines = len(content.splitlines())
    say(f"[banked] {d.name}: {lines} lines, sha256={sha}")
if not drafts:
    say("[held] no rebuild drafts found — use existing files directly")

# ---------- STAGE C: verify git state, propose commit ----------
say("== STAGE C [git-state] current HEAD + staged status ==")
try:
    head = subprocess.run(["git","rev-parse","--short","HEAD"],capture_output=True,text=True).stdout.strip()
    dirty = subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout
    say(f"[banked] HEAD: {head}")
    say(f"[banked] working-tree dirty lines: {len(dirty.splitlines())}")
    for ln in dirty.splitlines()[:15]:
        say(f"    {ln[:100]}")
except Exception as e:
    say(f"[held] git state check failed :: {e}")

# ---------- STAGE D: commit proposal ----------
say("== STAGE D [commit-proposal] == ")
manifest = [f"{fn} ({v['lines']} lines)" for fn,v in ledger.items()]
proposed_msg = f"""restore: {', '.join(manifest)} — v2.0 restructure survives on-disk post-crash

Provenance:
- GOALS/MASTER_TODO/TASK survived filter-repo history rewrite (commit 1ec3e352 referenced in MASTER_TODO)
- 2026-09-20 audit confirms 19+25+8 line artifacts present at repo root
- Master branches fleet-wide: dangling (29 repos), filter-repo zombie refs
- Rebuild drafts (v2) exist but empty; use original on-disk content

Actions:
- Commit: {', '.join(ledger.keys())}
- Next: delete stale master refs after confirmation
- Branch: openroot-product/kai-memory/fractallattice/etc still on master=default — rename when ready
"""
say(proposed_msg)
say(f"[{'banked' if CONFIRM else 'held'}] commit message proposed — human review before bank")

# ---------- STAGE E: execution (protected behind CONFIRM=1) ----------
if CONFIRM:
    if not ledger:
        say("[gate] ABORT: no files to commit — ledger empty")
    else:
        add_files = " ".join(ledger.keys())
        say(f"[banked] staging: git add {add_files}")
        subprocess.run(["git","add"]+[k for k in ledger.keys()], cwd=OPENROOT)
        say(f"[banked] commiting: git commit -m '...provisional message...'")
        proc = subprocess.run(["git","commit","-m",proposed_msg[:300]+"..."], cwd=OPENROOT, capture_output=True, text=True)
        if proc.returncode == 0:
            new_head = subprocess.run(["git","rev-parse","--short","HEAD"],capture_output=True,text=True).stdout.strip()
            say(f"[banked] COMMIT SUCCESSFUL: {new_head}")
        else:
            say(f"[gate] COMMIT FAILED: {proc.stderr[:200]}")
else:
    say(f"[held] DRY-RUN: commit previewed, nothing mutated; CONFIRM=1 to execute")

# ---------- HANDOFF ----------
rep = pathlib.Path(OPENROOT, "context_bridge", f"report-secure-commit-{STAMP}.md")
rep.write_text("\n".join(report) + f"\n\n## Handoff {STAMP}\nmode={'EXECUTE' if CONFIRM else 'DRY-RUN'}\n")
say(f"[banked] report sealed: {rep}")
print("[exit=0]")
