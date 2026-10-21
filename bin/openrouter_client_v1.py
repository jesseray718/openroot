#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""openrouter_client_v1.py — Live OpenRouter calls for the LB loop
Models (real catalog pricing, verified 2026-09-20 from /api/v1/models):
  tier 2: mistralai/mistral-nemo          $0.019/$0.03  per M tok
  tier 3: deepseek/deepseek-chat (V3)     $0.32/$0.89
  tier 4: qwen/qwen-2.5-72b-instruct      $0.36/$0.40
Budget law: refuses to run if cumulative spend >= SPEND_CAP (default $0.50).
Usage:
  keys                          show key status (masked)
  ask "<question>" [--tier N]   one call, tier defaults 2 (cheap!)
  drain [--execute]            run queued tier>=2 jobs from tier_dispatch db
  budget                       spend report from sqlite ledger
Setup (once): export OPENROUTER_API_KEY=sk-or-...  (or put it in ~/openroot/.env)
"""
import os, sys, json, sqlite3, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "openroot" / "data" / "tier_dispatch.db"
SPEND_CAP = float(os.environ.get("OR_SPEND_CAP", "0.50"))

MODELS = {
    2: ("mistralai/mistral-nemo",          0.019, 0.03),
    3: ("deepseek/deepseek-chat",         0.32,  0.89),
    4: ("qwen/qwen-2.5-72b-instruct",      0.36,  0.40),
}

def get_key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if k: return k.strip()
    envf = Path.home() / "openroot" / ".env"
    if envf.exists():
        for line in envf.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def now(): return datetime.now(timezone.utc).isoformat()

def conn():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS dispatch_log (
        id INTEGER PRIMARY KEY, ts TEXT, task_sha TEXT, tier INTEGER,
        model TEXT, in_tok INTEGER, out_tok INTEGER, cost_usd REAL, verdict TEXT)""")
    c.commit()
    return c

def spent(c):
    return c.execute("SELECT COALESCE(SUM(cost_usd),0) FROM dispatch_log").fetchone()[0]

def call(model, prompt, max_tokens=1024):
    """One OpenRouter chat call. Returns (text, in_tok, out_tok, cost) or raises."""
    key = get_key()
    if not key:
        raise SystemExit("[ERROR] OPENROUTER_API_KEY not set. Export it or add to ~/openroot/.env")
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

def guard(c, est_cost):
    total = spent(c)
    if total + est_cost > SPEND_CAP:
        raise SystemExit(f"[GATE] Spend cap: ${total:.4f} spent + ${est_cost:.4f} est > ${SPEND_CAP:.2f} cap. Raise OR_SPEND_CAP to override.")

def record(c, sha, tier, model, it, ot, cost, verdict):
    c.execute("INSERT INTO dispatch_log (ts, task_sha, tier, model, in_tok, out_tok, cost_usd, verdict) VALUES (?,?,?,?,?,?,?,?)",
              (now(), sha, tier, model, it, ot, cost, verdict))
    c.commit()

def ask(prompt, tier=2, max_tokens=1024):
    c = conn()
    model, ci, co = MODELS[tier]
    est = max(len(prompt.split())*2, 100)/1e6*ci + max_tokens/1e6*co
    guard(c, est)
    print(f"[CALL] {model} (tier {tier}, est ${est:.6f})")
    text, it, ot = call(model, prompt, max_tokens)
    cost = it/1e6*ci + ot/1e6*co
    import hashlib
    record(c, hashlib.sha256(prompt.encode()).hexdigest()[:16], tier, model, it, ot, cost, "ok")
    print(f"[USED] {it}+{ot} tok, ${cost:.6f} (total ${spent(c):.4f})")
    print(text)
    return text

def drain(execute=False):
    c = conn()
    rows = c.execute("""SELECT q.id, q.task_sha, q.task, q.tier FROM dispatch_queue q
                        WHERE q.status='queued' AND q.tier>=2 ORDER BY q.tier, q.id""").fetchall()
    if not rows:
        print("[DRAIN] Queue empty — nothing tier>=2 pending"); return
    if not execute:
        for rid, sha, task, tier in rows:
            print(f"[DRY] job {rid} tier {tier} MODELS[{tier}][0]: {task[:60]}")
        print(f"[DRAIN] Dry run — {len(rows)} jobs. Add --execute to run (spends real money).")
        return
    if os.environ.get("CONFIRM") != "1":
        raise SystemExit("[GATE] Real spend requires CONFIRM=1 env var (your destructive-ops doctrine).")
    for rid, sha, task, tier in rows:
        model, ci, co = MODELS[tier]
        print(f"\n===== JOB {rid} (tier {tier} -> {model}) =====")
        try:
            text, it, ot = call(model, task, max_tokens=2048)
            cost = it/1e6*ci + ot/1e6*co
            guard(c, cost)
            record(c, sha, tier, model, it, ot, cost, "drained")
            c.execute("UPDATE dispatch_queue SET status='done' WHERE id=?", (rid,)); c.commit()
            print(text)
            print(f"[USED] {it}+{ot} tok, ${cost:.6f} | running total ${spent(c):.4f}")
        except urllib.error.HTTPError as e:
            print(f"[ERROR] job {rid}: HTTP {e.code} — {e.read().decode()[:200]}")
            c.execute("UPDATE dispatch_queue SET status='failed' WHERE id=?", (rid,)); c.commit()

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "keys":
        k = get_key()
        print(f"[KEYS] OPENROUTER_API_KEY: {k[:5]}***{k[-3:]}" if k else "[KEYS] NOT FOUND — export OPENROUTER_API_KEY or add to ~/openroot/.env")
    elif cmd == "ask":
        tier = int(sys.argv[sys.argv.index("--tier")+1]) if "--tier" in sys.argv else 2
        ask(" ".join(sys.argv[2:]).replace(f"--tier {tier}", "").strip(), tier)
    elif cmd == "drain":
        drain(execute="--execute" in sys.argv)
    elif cmd == "budget":
        c = conn()
        print(json.dumps({"spent_usd": round(spent(c), 6),
                          "cap_usd": SPEND_CAP,
                          "calls": c.execute("SELECT COUNT(*) FROM dispatch_log").fetchone()[0]}, indent=2))
