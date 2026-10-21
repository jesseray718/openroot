#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
"""queue_advance_v1.py — mines context_bridge (recency*frequency), forges PR53
comment via 7B, grades via 3B, gh posts only on CONFIRM=1. Dry-run default.
[canary] queue_advance_v1_CANARY_MARKER"""
import glob, json, os, re, subprocess, sys, time, urllib.request, sqlite3
from datetime import datetime, timezone

REPO = "/home/jesse/openroot"
CB = os.path.join(REPO, "context_bridge")
OUT = os.path.join(REPO, "reports", "goals_draft")
DB = os.path.join(REPO, "data", "queue_advance.db")
OLLAMA = "http://localhost:11434/api/generate"
M_AUTHOR = os.environ.get("AGENT_MODEL", "qwen2.5-coder:7b")
M_GRADER = "qwen2.5:3b"
CONFIRM = os.environ.get("CONFIRM", "0")
PR_NUM = 53
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def say(tag, msg): print(f"[{tag}] {msg}")

def ollama(model, prompt, timeout=180):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())["response"]
    except Exception as e:
        say("held", f"ollama call failed ({model}): {e}")
        return None

# [1] MINE
os.makedirs(OUT, exist_ok=True)
sessions = sorted(glob.glob(os.path.join(CB, "session-*.md")))
if not sessions:
    say("held", "no context_bridge sessions — abort"); print("[exit=0]"); sys.exit(0)

PATTERNS = [re.compile(r"^\s*-\s+\[ \]\s*(.+)$", re.M),
            re.compile(r"^\s*\d+\.\s+(.+)$", re.M),
            re.compile(r"^#+\s*(?:NEXT|ACTION|TODO)[^\n]*\n((?:.*\n){1,8})", re.M | re.I)]
tasks = {}
now = time.time()
for sf in sessions:
    mtime = os.path.getmtime(sf)
    try: text = open(sf, encoding="utf-8", errors="replace").read()
    except OSError: continue
    for pat in PATTERNS:
        for m in pat.finditer(text):
            raw = m.group(1) if pat.groups else m.group(0)
            for line in raw.split("\n"):
                t = re.sub(r"^\s*[-\d.\[\]x ]*", "", line).strip()
                if len(t) < 5 or len(t) > 160: continue
                t = re.sub(r"\s+", " ", t)
                d = tasks.setdefault(t, {"count": 0, "last": mtime})
                d["count"] += 1
                d["last"] = max(d["last"], mtime)

ranked = []
for t, d in tasks.items():
    age_days = max(0.0, (now - d["last"]) / 86400.0)
    ranked.append((d["count"] / (1.0 + age_days), d["count"], t))
ranked.sort(reverse=True)

with open(os.path.join(OUT, "task_rank.tsv"), "w") as f:
    f.write("score\tfreq\ttask\n")
    for s, c, t in ranked[:25]:
        f.write(f"{s:.3f}\t{c}\t{t}\n")
say("banked", f"mined {len(tasks)} unique tasks from {len(sessions)} sessions -> task_rank.tsv")

os.makedirs(os.path.dirname(DB), exist_ok=True)
con = sqlite3.connect(DB)
con.execute("CREATE TABLE IF NOT EXISTS runs (ts TEXT, stage TEXT, detail TEXT)")
con.execute("INSERT INTO runs VALUES (?,?,?)",
            (TS, "mine", f"sessions={len(sessions)} tasks={len(tasks)}"))
con.commit(); con.close()

# [2] FORGE — 7B authors, 3B grades, max 3 passes
BASE = """Context: OpenRoot maintainer Jesse. Contributor Reh1t opened PR 53 (RAG ingestion)
against an OLD main. Repo main was force-pushed (history rewritten via git filter-repo),
so Reh1t's clone is stale and their PR will show spurious add/add conflicts (same pattern
as prior PR 59). Tone: warm, grateful, zero blame, technically precise, brief.
Must contain: (a) genuine thanks, (b) plain explanation that main was force-pushed,
(c) exact recovery commands: git fetch origin then checkout their branch then
git rebase origin/main, (d) offer to review promptly after rebase,
(e) reassurance the staleness is our history rewrite, not their mistake.
80-130 words, markdown. Output the comment only, no preamble."""

GATE = """You are a strict reviewer. Score this PR comment 0-10 on factual accuracy,
tone, brevity, and actionability of rebase instructions. Reply ONLY with JSON:
{"score": <int>, "verdict": "accept or reject", "issues": "<one line or empty>"}

COMMENT:
"""

comment, best, best_score, prev_issues = None, None, -1, ""
for i in range(1, 4):
    if i == 1:
        c = ollama(M_AUTHOR, BASE)
    else:
        c = ollama(M_AUTHOR, BASE + f"\nPrevious draft scored {best_score}/10, issues: "
                     + prev_issues + ". Fix and output improved comment only.")
    if not c: continue
    g = ollama(M_GRADER, GATE + c, timeout=60)
    try:
        verdict = json.loads(g[g.index("{"):g.rindex("}") + 1])
        score = int(verdict["score"])
        ok = str(verdict["verdict"]).startswith("accept")
        prev_issues = verdict.get("issues", "")
    except Exception:
        say("held", f"pass {i}: grader unparsable, retrying"); prev_issues = "unparseable"; continue
    say("gate", f"pass {i}: 3B score={score} verdict={verdict['verdict']}")
    if score > best_score: best, best_score = c, score
    if ok: comment = c; break

if not comment:
    if best:
        comment = best
        say("held", f"no accept in 3 passes — using best draft ({best_score}/10)")
    else:
        say("held", "local stack unavailable — manual fallback")
        comment = ("@Reh1t Thank you for this contribution! One heads-up: our `main` was recently "
                   "force-pushed during a history cleanup, so your clone is pointing at old history "
                   "and this PR will show some spurious conflicts — that's on us, not your work. "
                   "A fresh `git fetch origin` then rebase onto `origin/main` from your branch should "
                   "clear it up. Happy to review promptly once rebased — thanks again!")

outpath = os.path.join(OUT, "pr53_comment_draft.md")
open(outpath, "w").write(comment.strip() + "\n")
say("banked", f"PR53 comment sealed ({len(comment.split())} words) -> {outpath}")

# [3] EMIT / POST (gated)
gh_cmd = ["gh", "pr", "comment", str(PR_NUM), "--body-file", outpath,
          "--repo", "jesseray718/openroot"]
if CONFIRM == "1":
    r = subprocess.run(gh_cmd, capture_output=True, text=True, cwd=REPO)
    if r.returncode == 0:
        say("banked", f"posted #{PR_NUM} comment: {r.stdout.strip()}")
    else:
        say("held", f"gh failed rc={r.returncode}: {r.stderr.strip()}"); sys.exit(1)
else:
    say("held", f"DRY RUN — review {outpath}, then CONFIRM=1 python3 {os.path.abspath(__file__)}")
print("[exit=0]")
