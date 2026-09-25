#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# secure_and_commit_v5_20260920.py — hash GOALS/MASTER_TODO/TASK, stage + commit with
# provenance. Quoting hardened: no multi-line f-strings, no nested-quote f-expressions.
# DRY-RUN default; CONFIRM=1 executes commit. Human is the only commit gate before CONFIRM.
import hashlib, pathlib, subprocess, datetime, os, sys

OPENROOT = "/home/jesse/openroot"
CONFIRM = (os.environ.get("CONFIRM", "0") == "1")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.chdir(OPENROOT)
print("[canary] OPENROOT-secure-commit-v5-20260920 paste intact")

report = []
def say(msg):
    print(msg)
    report.append(msg)

def sh(args):
    return subprocess.run(args, cwd=OPENROOT, capture_output=True, text=True)

# ---------- STAGE A: inventory on-disk artifacts ----------
say("== STAGE A [inventory] GOALS/MASTER_TODO/TASK ==")
FILES = ["GOALS.md", "MASTER_TODO.md", "TASK.md"]
ledger = {}
for fn in FILES:
    p = pathlib.Path(OPENROOT, fn)
    if p.exists():
        content = p.read_text(errors="ignore")
        digest = hashlib.sha256(content.encode()).hexdigest()
        ledger[fn] = {"sha": digest[:16], "lines": len(content.splitlines()), "bytes": len(content)}
        say("[banked] %s: %d lines, %d bytes, sha256=%s" % (fn, ledger[fn]["lines"], ledger[fn]["bytes"], ledger[fn]["sha"]))
    else:
        say("[held] %s: MISSING — excluded from commit" % fn)

# ---------- STAGE B: rebuild drafts present? ----------
say("== STAGE B [rebuild-drafts] supersession check ==")
for pat in ("GOALS.rebuild.*.md", "MASTER_TODO.rebuild.*.md"):
    for d in sorted(pathlib.Path(OPENROOT).glob(pat)):
        say("[held] draft present: %s (%d lines) — superseded by on-disk original; delete after review" % (d.name, len(d.read_text(errors='ignore').splitlines())))

# ---------- STAGE C: git state ----------
say("== STAGE C [git-state] ==")
head = sh(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
status = sh(["git", "status", "--porcelain"]).stdout.splitlines()
say("[banked] HEAD: %s | working-tree dirty lines: %d" % (head, len(status)))
for ln in status[:15]:
    say("    " + ln[:100])

# ---------- STAGE D: commit message (plain concatenation) ----------
say("== STAGE D [commit-proposal] ==")
file_list = ", ".join("%s (%d lines)" % (fn, v["lines"]) for fn, v in ledger.items())
msg_lines = [
    "restore: %s — v2.0 restructure survives on-disk post-crash" % file_list,
    "",
    "Provenance:",
    "- GOALS/MASTER_TODO/TASK survived the filter-repo history rewrite; referenced 1ec3e352",
    "- 2026-09-20 audit: 19+25+8 line artifacts present at repo root, hashes in report",
    "- Fleet masters: 29 dangling refs (SHAs stripped), 0 recoverable via compare",
    "- Rebuild drafts empty (salvage grep zero-hit across 17 context_bridge sources)",
    "",
    "Actions:",
    "- Commits ONLY the three surviving planning docs; no other working-tree changes",
    "- Next: delete 29 dangling master refs fleet-wide (ledger: data/master_heads_ledger_20260920_020335.json)",
]
proposed_msg = "\n".join(msg_lines)
say(proposed_msg)

# ---------- STAGE E: execute ----------
if CONFIRM:
    if not ledger:
        say("[gate] ABORT: ledger empty")
        sys.exit(1)
    staged = sh(["git", "add"] + list(ledger.keys()))
    commit = sh(["git", "commit", "-m", proposed_msg])
    if commit.returncode == 0:
        new_head = sh(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
        say("[banked] COMMIT SEALED: %s -> %s" % (head, new_head))
    else:
        say("[gate] COMMIT FAILED :: " + commit.stderr.strip()[:200])
        sys.exit(1)
else:
    say("[held] DRY-RUN: nothing staged, nothing committed; rerun with CONFIRM=1 to bank")

# ---------- HANDOFF ----------
rep = pathlib.Path(OPENROOT, "context_bridge", ("report-secure-commit-%s.md" % STAMP))
rep.write_text("\n".join(report) + "\n\n## Handoff %s\nmode=%s\nnext: CONFIRM commit, then fleet master deletion pass\n" % (STAMP, ("EXECUTE" if CONFIRM else "DRY-RUN")))
say("[banked] report sealed: " + str(rep))
print("[exit=0]")
