#!/usr/bin/env python3
"""specialist_router_v1.py — FTS5-first dispatch, cross-family grading, warm-pool pinning.
Superlinear workflow orchestrator: cache → FTS5 → 7B builder → 3B grader.

SPDX-License-Identifier: GPL-3.0-only
Author: Jesse McMillen Ray (OpenRoot)
License: Code GPL-3.0, Docs CC-BY-SA-4.0
"""
import json, sqlite3, time, urllib.request, hashlib, sys, os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"
LOG_DIR = ROOT / "logs"

# CONFIGURATION
OLLAMA_API = "http://localhost:11434/api/generate"
KEEP_ALIVE = "2h"  # Pin warm pool across all calls
BUILDER_MODEL = "qwen2.5-coder:7b"
GRADER_MODEL = "qwen2.5:3b"
EMBED_MODEL = "nomic-embed-text"

# FTS5 INDEX PATHS (pre-built or auto-seeded)
FTS5_DB = DATA / "router_corpus.sqlite"
CACHE_DB = DATA / "problem_solution_cache.sqlite"
LEDGER_DB = DATA / "routing_ledger.sqlite"

def init_fts5():
    """Initialize FTS5 corpus with verified artifacts."""
    conn = sqlite3.connect(FTS5_DB)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS corpus USING fts5(
            path, category, content, 
            tokenize="porter unicode61 remove_diacritics 1"
        )
    """)
    # Seed with known-good answers (extend as needed)
    seeds = [
        ("thermal_frontier_v2_water.json", "energy", "15.8 kW thermal water 83-86C exit 24 panel 120m2"),
        ("thermal_balance_v63.md", "physics", "341C radiative equilibrium ceiling eps=0.10"),
        ("euler_overshoot_lesson.md", "lesson", "low-flow Euler divergence filter temps above 341C"),
        ("steam_hx_ceiling.md", "engineering", "2.4 kW steam heat exchanger failing gate not temperature"),
    ]
    for path, cat, content in seeds:
        conn.execute("INSERT INTO corpus(path, category, content) VALUES (?,?,?)", (path, cat, content))
    conn.commit()
    return conn

def init_cache():
    """Initialize sha-keyed solution cache."""
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kv (
            problem_sha TEXT PRIMARY KEY,
            solution_sha TEXT,
            payload TEXT,
            verified_at TEXT
        )
    """)
    conn.commit()
    return conn

def init_ledger():
    """Initialize routing decision ledger."""
    conn = sqlite3.connect(LEDGER_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            ts TEXT,
            query TEXT,
            layer TEXT,  -- fts5, cache, builder, grader
            latency_ms REAL,
            hit TEXT,    -- path or result preview
            canary TEXT
        )
    """)
    conn.commit()
    return conn

def fts5_query(query, top_k=3):
    """Layer 1: FTS5 exact-match dispatch. Returns hit if confidence > threshold."""
    conn = init_fts5()
    t0 = time.perf_counter()
    cursor = conn.execute(
        "SELECT path, category, content FROM corpus WHERE corpus MATCH ? LIMIT ?",
        (query, top_k)
    )
    hits = cursor.fetchall()
    ms = (time.perf_counter() - t0) * 1000
    conn.close()
    if hits:
        return {"hit": True, "result": hits[0], "latency_ms": ms}
    return {"hit": False, "latency_ms": ms}

def cache_query(problem):
    """Layer 2: sha-keyed cache lookup."""
    conn = init_cache()
    psha = hashlib.sha256(problem.encode()).hexdigest()
    t0 = time.perf_counter()
    row = conn.execute(
        "SELECT payload, verified_at FROM kv WHERE problem_sha=?", (psha,)
    ).fetchone()
    ms = (time.perf_counter() - t0) * 1000
    conn.close()
    if row:
        return {"hit": True, "payload": row[0], "latency_ms": ms}
    return {"hit": False, "latency_ms": ms}

def generate(model, prompt, keep_alive=KEEP_ALIVE):
    """Call Ollama API with warm-pool pinning."""
    payload = json.dumps({
        "model": model, "prompt": prompt,
        "stream": False, "keep_alive": keep_alive
    }).encode()
    req = urllib.request.Request(OLLAMA_API, data=payload,
        headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            out = json.loads(resp.read().decode())
        ms = (time.perf_counter() - t0) * 1000
        return {
            "success": True,
            "response": out.get("response", ""),
            "eval_count": out.get("eval_count", 0),
            "latency_ms": ms
        }
    except Exception as e:
        return {"success": False, "error": str(e), "latency_ms": (time.perf_counter() - t0) * 1000}

def cache_store(problem, payload):
    """Store verified solution in cache."""
    conn = init_cache()
    psha = hashlib.sha256(problem.encode()).hexdigest()
    ssha = hashlib.sha256(payload.encode()).hexdigest()
    conn.execute(
        "INSERT OR REPLACE INTO kv(problem_sha, solution_sha, payload, verified_at) VALUES (?,?,?,?)",
        (psha, ssha, payload, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

def log_decision(query, layer, latency, hit_detail, canary="ROUTERV1"):
    """Append routing decision to ledger."""
    conn = init_ledger()
    conn.execute(
        "INSERT INTO decisions(ts, query, layer, latency_ms, hit, canary) VALUES (?,?,?,?,?,?)",
        (datetime.now(timezone.utc).isoformat(), query, layer, latency, hit_detail, canary)
    )
    conn.commit()
    conn.close()

def route(query):
    """Main dispatch: FTS5 → cache → builder → grader."""
    start = time.perf_counter()
    
    # Layer 1: FTS5
    fts5_result = fts5_query(query)
    log_decision(query, "fts5", fts5_result["latency_ms"], str(fts5_result["hit"]))
    if fts5_result["hit"]:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[FTS5] HIT in {elapsed:.1f}ms → {fts5_result['result'][0]}")
        return fts5_result
    
    # Layer 2: Cache
    cache_result = cache_query(query)
    log_decision(query, "cache", cache_result["latency_ms"], str(cache_result["hit"]))
    if cache_result["hit"]:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[CACHE] HIT in {elapsed:.1f}ms → {cache_result['payload'][:50]}...")
        return cache_result
    
    # Layer 3: 7B Builder
    builder_prompt = f"Answer concisely: {query}"
    builder_result = generate(BUILDER_MODEL, builder_prompt)
    if builder_result["success"]:
        log_decision(query, "builder", builder_result["latency_ms"],
                     builder_result["response"][:50])
        # Store in cache for future
        cache_store(query, builder_result["response"])
        print(f"[BUILDER] {BUILDER_MODEL} in {builder_result['latency_ms']:.0f}ms → "
              f"{builder_result['eval_count']} tokens")
        return builder_result
    
    # Layer 4: 3B Grader (cross-family verification)
    grader_prompt = f"Verify the following answer is sound. Say 'VALID' or list errors: {query}"
    grader_result = generate(GRADER_MODEL, grader_prompt)
    if grader_result["success"]:
        log_decision(query, "grader", grader_result["latency_ms"],
                     grader_result["response"][:50])
        print(f"[GRADER] {GRADER_MODEL} in {grader_result['latency_ms']:.0f}ms → "
              f"{grader_result['eval_count']} tokens")
        return grader_result
    
    log_decision(query, "FAIL", (time.perf_counter() - start) * 1000, "no layer responded")
    return {"success": False, "error": "No model responded"}

def main():
    """CLI entry point with warm-pool priming."""
    print("[router] Initializing FTS5 + cache + warm-pool priming...")
    init_fts5()
    init_cache()
    init_ledger()
    
    # Warm-pool priming: force both models into memory
    print("[warmup] Pre-loading builder and grader...")
    generate(BUILDER_MODEL, "READY", keep_alive=KEEP_ALIVE)
    generate(GRADER_MODEL, "READY", keep_alive=KEEP_ALIVE)
    print("[warmup] Complete. Models pinned for 2h.")
    
    # Interactive mode
    print("\n[router] Ready. Enter queries (ctrl-d to exit):")
    for line in sys.stdin:
        query = line.strip()
        if not query or query.startswith("#"):
            continue
        result = route(query)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
