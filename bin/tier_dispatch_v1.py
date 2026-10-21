#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""tier_dispatch_v1.py — Budget-aware tier router for the LB loop
Local free checkpoints grade everything. Only problems that survive all
local gates get staged for the paid big brain. Every dispatch is logged
to sqlite with token estimates so you can measure $ per verified insight.

Tiers:
  0 = deterministic local (awk, sqlite, py_compile, hash gates)  cost=$0
  1 = local small models (qwen 3B grader, nomic embed)          cost=$0
  2 = ultra-cheap API (DeepSeek V4 Flash ~$0.14/M in)           cost≈$
  3 = cheap frontier (GPT-5.6 Luna ~$0.20/M in)                 cost=$$
  4 = orchestration brain (Fugu Max ~$2/$6, Kimi K3 $3/$15)     cost=$$$
Usage:
  python3 tier_dispatch_v1.py classify "<task text>"
  python3 tier_dispatch_v1.py enqueue "<task>" [--require-tier N]
  python3 tier_dispatch_v1.py drain           # run queued tier-4 jobs (dry-run prints payloads)
  python3 tier_dispatch_v1.py budget          # spend report
"""
import sys, json, sqlite3, hashlib
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "openroot" / "data" / "tier_dispatch.db"

TIER_COST_PER_MTOK = {  # input/output per MILLION tokens; VERIFY current pricing before real calls
    2: (0.14, 0.28),    # DeepSeek V4 Flash (reported Jun 2026)
    3: (0.20, 0.80),    # GPT-5.6 Luna post-cut (reported Aug 2026)
    4: (2.00, 6.00),    # Sakana Fugu Max (reported Sep 2026)
}
MODEL_FOR_TIER = {2: "deepseek-v4-flash", 3: "gpt-5.6-luna", 4: "fugu-max"}

HARD_KEYWORDS = ["theorem", "prove", "architecture", "design", "derive",
                 "optimize", "refactor", "synthes", "audit", "strategy"]
MID_KEYWORDS = ["summar", "draft", "convert", "format", "translate", "extract"]

def now(): return datetime.now(timezone.utc).isoformat()

def init():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS dispatch_queue (
        id INTEGER PRIMARY KEY, ts TEXT, task TEXT, task_sha TEXT,
        tier INTEGER, status TEXT DEFAULT 'queued',
        est_in_tok INTEGER, est_out_tok INTEGER, est_cost_usd REAL);
    CREATE TABLE IF NOT EXISTS dispatch_log (
        id INTEGER PRIMARY KEY, ts TEXT, task_sha TEXT, tier INTEGER,
        model TEXT, in_tok INTEGER, out_tok INTEGER, cost_usd REAL, verdict TEXT);
    """)
    c.commit()
    return c

def classify(task: str) -> dict:
    """Stage-1/2 gating. Rises in tier only when local gates can't settle it."""
    t = task.lower()
    hard = sum(1 for k in HARD_KEYWORDS if k in t)
    mid = sum(1 for k in MID_KEYWORDS if k in t)
    tokens = len(task.split()) * 1.3
    if hard >= 2:                tier, why = 4, "multi-hard-keyword synthesis"
    elif hard == 1:              tier, why = 3, "single hard keyword"
    elif mid >= 1 or tokens > 200: tier, why = 2, "mechanical transform, large context"
    else:                        tier, why = 1, "simple enough for local 3B"
    if "verify" in t or "test" in t or "compile" in t:
        tier = 0; why = "deterministic gate handles it (tier 0, free)"
    return {"tier": tier, "why": why, "est_tokens": int(tokens)}

def est_cost(tier, in_tok, out_tok):
    if tier not in TIER_COST_PER_MTOK: return 0.0
    i, o = TIER_COST_PER_MTOK[tier]
    return round(in_tok / 1e6 * i + out_tok / 1e6 * o, 6)

def enqueue(c, task, require_tier=None):
    cls = classify(task)
    tier = require_tier if require_tier is not None else cls["tier"]
    sha = hashlib.sha256(task.encode()).hexdigest()[:16]
    cur = c.execute("SELECT id FROM dispatch_queue WHERE task_sha=? AND status='queued'", (sha,)).fetchone()
    if cur:
        return {"idempotent_hit": cur[0], "sha": sha}
    est_in = max(len(task.split()) * 2, 500)
    est_out = max(est_in // 2, 200)
    c.execute("INSERT INTO dispatch_queue (ts, task, task_sha, tier, est_in_tok, est_out_tok, est_cost_usd) VALUES (?,?,?,?,?,?,?)",
              (now(), task, sha, tier, est_in, est_out, est_cost(tier, est_in, est_out)))
    c.commit()
    return {"queued": sha, "tier": tier, "why": cls["why"], "est_cost_usd": est_cost(tier, est_in, est_out)}

def drain(c, dry=False):
    """Pull tier>=2 queued jobs. Wires to API when you're ready; today it emits staged payloads."""
    rows = c.execute("SELECT id, task_sha, task, tier, est_in_tok, est_out_tok, est_cost_usd "
                     "FROM dispatch_queue WHERE status='queued' AND tier>=2 ORDER BY tier, id").fetchall()
    out = []
    for rid, sha, task, tier, it, ot, cost in rows:
        payload = {"job_id": rid, "sha": sha, "model": MODEL_FOR_TIER[tier],
                   "prompt": task, "est_in_tok": it, "est_out_tok": ot, "est_cost_usd": cost}
        if not dry:
            c.execute("UPDATE dispatch_queue SET status='staged' WHERE id=?", (rid,))
            c.commit()
        out.append(payload)
    return out

def budget(c):
    total = c.execute("SELECT COALESCE(SUM(cost_usd),0) FROM dispatch_log").fetchone()[0]
    by_tier = c.execute("SELECT tier, COUNT(*), SUM(cost_usd) FROM dispatch_log GROUP BY tier").fetchall()
    queued = c.execute("SELECT tier, COUNT(*), SUM(est_cost_usd) FROM dispatch_queue WHERE status='queued' GROUP BY tier").fetchall()
    return {"spent_usd": round(total, 4),
            "by_tier": [{"tier": t, "calls": n, "cost": round(cst or 0, 4)} for t, n, cst in by_tier],
            "queued": [{"tier": t, "n": n, "est_cost": round(cst or 0, 4)} for t, n, cst in queued]}

if __name__ == "__main__":
    c = init()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "budget"
    if cmd == "classify":
        print(json.dumps(classify(" ".join(sys.argv[2:])), indent=2))
    elif cmd == "enqueue":
        t = sys.argv[2]; rt = None
        if "--require-tier" in sys.argv: rt = int(sys.argv[sys.argv.index("--require-tier") + 1])
        print(json.dumps(enqueue(c, t, rt), indent=2))
    elif cmd == "drain":
        dry = "--execute" not in sys.argv
        print(json.dumps({"dry_run": dry, "jobs": drain(c, dry)}, indent=2))
    elif cmd == "budget":
        print(json.dumps(budget(c), indent=2))
    else:
        print(__doc__)

# At the top of the file, update MODEL_FOR_TIER:
# MODEL_FOR_TIER = {
#     2: "openrouter/deepseek/deepseek-chat",    # Your key: sk-o***6d
#     3: "gemini/gemini-1.5-flash",              # Your key: AQ.A***mw
#     4: "openrouter/fugu-max"                   # Add when you're ready to spend
# }
