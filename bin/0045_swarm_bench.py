#!/usr/bin/env python3
"""OpenRoot Fractal Swarm - HONEST throughput benchmark. One-shot, idempotent."""
import gc, hashlib, json, os, time

ROOT = "/sdcard/openroot"
CTX  = os.path.join(ROOT, "context_bridge")
AUDIT = os.path.join(CTX, "swarm_bench_audit.jsonl")
LEDGER = os.path.join(CTX, "thermo_ledger.jsonl")
os.makedirs(CTX, exist_ok=True)
gc.disable()

print("[capture] swarm bench start", flush=True)

# ---------- the 12 atoms ----------
def f1_capture(p):  p["ts"] = time.time(); return p
def f2_hash(p):     p["h"] = hashlib.sha256(repr(p.get("d")).encode()).hexdigest()[:16]; return p
def f3_aggregate(p):p["d"] = p["d"] if isinstance(p["d"], list) else [p["d"]]; return p
def f4_pair(p):     p["d"] = (p["d"], p["d"]); return p
def f5_commit(p):   p["c"] = p.get("h"); return p
def f6_verify(p):   p["v"] = (p.get("c") == p.get("h")); return p
def f7_landauer(p): p["E"] = 2.87e-21; return p
def f8_observe(p):  p["o"] = True; return p
def f9_store(p):    p["s"] = str(p.get("d"))[:16]; return p
def f10_yield(p):   p["y"] = p.get("v"); return p
def f11_adapt(p):   p["a"] = (p.get("a", 0) + 1) % 7; return p
def f12_sync(p):    p["n"] = "node0"; return p

ATOMS = [f1_capture, f2_hash, f3_aggregate, f4_pair, f5_commit, f6_verify,
         f7_landauer, f8_observe, f9_store, f10_yield, f11_adapt, f12_sync]

def leaf():
    p = {"d": 1}
    for f in ATOMS:
        p = f(p)
    return p

def build(n, depth):
    fn = leaf
    for _ in range(depth):
        children = [fn] * n
        def runner(children=children):
            r = None
            for c in children:
                r = c()
            return r
        fn = runner
    return fn

def bench(n, depth, budget_s=2.0):
    fn = build(n, depth)
    r = fn()
    assert r.get("v") is True, "[held] verify failed - chain broken"
    atom_calls_per_cycle = len(ATOMS) * (n ** depth)
    cycles = 0
    t0 = time.perf_counter()
    while True:
        for _ in range(16):
            fn()
        cycles += 16
        if time.perf_counter() - t0 >= budget_s:
            break
    dt = time.perf_counter() - t0
    cyc_rate = cycles / dt
    atom_rate = atom_calls_per_cycle * cyc_rate
    return atom_calls_per_cycle, cyc_rate, atom_rate, dt

rows = []
print(f"{'N':>3} {'L':>2} {'atom-ops/cycle':>16} {'cycles/s':>10} {'MEASURED atom-ops/s':>21}", flush=True)
for n, d in [(3, 4), (3, 5), (3, 7), (12, 5), (12, 6)]:
    ops, cr, ar, dt = bench(n, d)
    rows.append({"n": n, "l": d, "atom_ops_per_cycle": ops,
                 "cycles_per_s": round(cr, 2), "measured_atom_ops_s": round(ar, 1)})
    print(f"{n:>3} {d:>2} {ops:>16,} {cr:>10.2f} {ar:>21,.0f}", flush=True)

peak = max(r["measured_atom_ops_s"] for r in rows)
claim = 6_131_462_173
print("-" * 60, flush=True)
print(f"[verify] MEASURED peak : {peak:,.0f} atom-ops/s", flush=True)
print(f"[verify] CLAIMED peak  : {claim:,.0f} atom-ops/s", flush=True)
print(f"[verify] claim/actual  : {claim/peak:,.0f}x  -> "
      f"{'CONFIRMED' if 0.5 <= claim/peak <= 2.0 else 'REFUTED'}", flush=True)
print(f"[verify] ns per atom-op: {1e9/peak:.1f} ns (CPython call floor ~50-100ns)", flush=True)

entry = {
    "id": "swarm_bench_" + hashlib.sha256(str(rows).encode()).hexdigest()[:12],
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "type": "fractal_swarm_benchmark",
    "method": "wall-clock closure execution, gc disabled, verify-gated",
    "peak_measured_atom_ops_s": peak,
    "claim_6.13B_refuted": claim/peak > 2.0,
    "rows": rows,
    "hash": hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16],
    "status": "MEASURED",
}
with open(AUDIT, "a") as f:
    f.write(json.dumps(entry) + "\n")
with open(LEDGER, "a") as f:
    f.write(json.dumps({"type": "swarm_bench",
                        "peak_atom_ops_s": peak,
                        "hash": entry["hash"],
                        "status": "MEASURED"}) + "\n")

print(f"[banked] audit -> {AUDIT}", flush=True)
print(f"[banked] ledger measurement appended -> {LEDGER}", flush=True)
print("[exit=0]", flush=True)
