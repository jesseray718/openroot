#!/usr/bin/env python3
"""
stack_test_core_v1.py — superlinear loop layer-by-layer latency tests.
Layers: FTS5 exact-hit | embed cache hit vs miss | router dispatch | 7B generate.
Emits one JSON report for the timing ledger.

SPDX-License-Identifier: GPL-3.0-only
Author: Jesse McMillen Ray (OpenRoot)
"""
import json, sqlite3, time, sys, os, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"
RESULTS = []

def record(layer, name, ms, detail=""):
    RESULTS.append({"layer": layer, "test": name, "ms": round(ms, 2), "detail": detail})
    flag = "SUB-SECOND" if ms < 1000 else "model-tier"
    print(f"  [{flag:>11}] {name}: {ms:.1f} ms {detail}")

def ftlayer_test():
    """Layer 1: FTS5 exact-hit retrieval in temp DB (no model call)."""
    db = DATA / "stack_test_fts5.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS corpus USING fts5(path, content)")
    corpus = [
        ("thermal_frontier_v1.json", "732 configs frontier scan thermal"),
        ("thermal_frontier_v2_water.json", "15.8 kW water heating 83-86C exit 24 panel"),
        ("session-2026-09-24-handoff.md", "341C radiative ceiling euler overshoot filter"),
        ("sare_grant_framing.md", "SARE bottom-first thermal cascade farm"),
        ("superlinear_methodology.md", "cache chain router triad marginal utility"),
    ]
    for path, content in corpus:
        conn.execute("INSERT INTO corpus(path, content) VALUES (?, ?)", (path, content))
    conn.commit()

    t0 = time.perf_counter()
    hits = conn.execute(
        "SELECT path FROM corpus WHERE corpus MATCH ?", ("thermal AND frontier",)
    ).fetchall()
    record("fts5", "FTS5 exact-hit query", (time.perf_counter() - t0) * 1000,
           f"-> {[h[0] for h in hits]}")
    conn.close()
    os.remove(db)

def cache_layer_test():
    """Layer 2: sha-keyed cache hit vs miss (the non-recompute doctrine)."""
    db = DATA / "stack_test_cache.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE IF NOT EXISTS kv (
        problem_sha TEXT PRIMARY KEY, solution_sha TEXT, payload TEXT)""")
    problem = "What is the radiative equilibrium ceiling for eps=0.10 blackbody absorption?"
    solution = "341C at eps=0.10 radiative equilibrium (thermal_balance v6.3 verified)"
    import hashlib
    psha = hashlib.sha256(problem.encode()).hexdigest()
    ssha = hashlib.sha256(solution.encode()).hexdigest()
    conn.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (psha, ssha, solution))
    conn.commit()

    t0 = time.perf_counter()  # MISS path (cold derive stand-in)
    derived = hashlib.sha256(("derive:" + problem).encode()).hexdigest()
    miss_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()  # HIT path
    row = conn.execute("SELECT payload FROM kv WHERE problem_sha=?", (psha,)).fetchone()
    hit_ms = (time.perf_counter() - t0) * 1000
    assert row and row[0] == solution, "cache hit returned wrong payload"

    speedup = miss_ms / max(hit_ms, 1e-6)
    record("cache", "sha-cache HIT lookup", hit_ms, f"payload OK, speedup-vs-hash {speedup:.1f}x")
    record("cache", "sha-cache MISS derive (stand-in)", miss_ms, "novel work escalates to 7B")
    conn.close()
    os.remove(db)

def router_layer_test():
    """Layer 3: FTS5-first dispatch — corpus hit returns, no model call."""
    db = DATA / "stack_test_fts5.sqlite2"
    conn = sqlite3.connect(db)
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS kb USING fts5(k, v)")
    conn.executemany("INSERT INTO kb(k,v) VALUES (?,?)", [
        ("euler overshoot", "low-flow Euler step divergence; filter temps > 341C"),
        ("steam hx ceiling", "~2.4 kW — steam was the failing gate, not temperature"),
    ])
    conn.commit()
    query = "euler overshoot"
    t0 = time.perf_counter()
    hits = conn.execute("SELECT v FROM kb WHERE kb MATCH ?", (query,)).fetchall()
    ms = (time.perf_counter() - t0) * 1000
    if hits:
        record("router", f"dispatch '{query}' -> FTS5 (NO model call)", ms, f"-> {hits[0][0][:40]}")
    else:
        record("router", f"dispatch '{query}' -> escalate to 7B", ms, "miss path")
    conn.close()
    os.remove(db)

def model_layer_test(model, prompt):
    """Layer 4: live 7B generate via ollama API."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate", data=payload,
        headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as resp:
        out = json.loads(resp.read().decode())
    ms = (time.perf_counter() - t0) * 1000
    text = out.get("response", "").strip().splitlines()[0] if out.get("response") else "(empty)"
    record("model", f"{model} generate", ms, f"tokens={out.get('eval_count','?')} -> \"{text[:50]}\"")
    return out

def main():
    print("  [superlinear-test] layer-by-layer:")
    ftlayer_test()
    cache_layer_test()
    router_layer_test()
    model_layer_test("qwen2.5-coder:7b", "Reply with exactly: 7B BUILDER ALIVE. Then state the FTS5 cache triad in one line.")
    model_layer_test("qwen2.5:3b", "Reply with exactly: 3B GRADER ALIVE.")

    report = {
        "canary": "STACKTESTV1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "author": "Jesse McMillen Ray",
        "results": RESULTS,
        "subsecond_layers": sum(1 for r in RESULTS if r["ms"] < 1000),
        "total_tests": len(RESULTS),
    }
    out = DATA / f"stack_test_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"  [banked] report -> {out.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
