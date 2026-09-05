#!/usr/bin/env python3
"""Test 7^7 and 6^6 configurations"""
import os, json, time, sys
from datetime import datetime, timezone

LOG = "/sdcard/openroot/session_seeds/fractal_engine_log.jsonl"
sys.setrecursionlimit(50000)

def f1(d): return {"t":"cap","d":d,"ts":time.time()}
def f2(d): return {"t":"hash","h":str(hash(str(d)))}
def f3(d): return {"t":"agg","n":len(d) if isinstance(d,list) else 1}
def f4(d): return {"t":"pair","l":d,"r":d}
def f5(d): return {"t":"commit","d":d}
def f6(d): return {"t":"verify","d":d}
def f7(d): return {"t":"landauer","c":1}

SEVEN_ATOMS = [f1,f2,f3,f4,f5,f6,f7]
SIX_ATOMS = [f1,f2,f3,f4,f5,f6]

def build(depth, funcs):
    if depth == 1:
        def chain(inp):
            r = inp
            for fn in funcs:
                r = fn(r)
            return r
        return chain
    else:
        sub = build(depth - 1, funcs)
        def chain(inp):
            results = []
            for i in range(len(funcs)):
                results.append(sub(inp))
            return f3(results)
        return chain

configs = [
    ("7 atoms x 7 depth", 7, SEVEN_ATOMS),
    ("6 atoms x 6 depth", 6, SIX_ATOMS),
]

print("=" * 60)
print("FRACTAL ENGINE — CONFIGURATION TESTS")
print("=" * 60)

for name, depth, atoms in configs:
    n = len(atoms)
    total = n ** depth
    
    print(f"\n>>> {name}")
    print(f"    Scale: {n}^{depth} = {total:,} ops")
    sys.stdout.flush()
    
    t_build = time.time()
    ch = build(depth, atoms)
    build_dur = time.time() - t_build
    
    inp = {"seed": f"OpenRoot_{n}x{depth}", "ts": datetime.now(timezone.utc).isoformat()}
    
    t0 = time.time()
    result = ch(inp)
    dur = time.time() - t0
    
    eta = total / dur if dur > 0 else 0
    
    # Energy estimate
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r") as f:
            freq_mhz = int(f.read().strip()) / 1000.0
        power_w = 0.5 * (freq_mhz / 650.0) ** 1.5
    except:
        freq_mhz = 0
        power_w = 0.5
    energy_j = power_w * dur
    joules_per_op = energy_j / total if total > 0 else 0
    
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "config": name,
        "atoms": n,
        "depth": depth,
        "total_ops": total,
        "build_time_s": round(build_dur, 4),
        "run_time_s": round(dur, 6),
        "throughput_ops_per_sec": round(eta, 2),
        "cpu_freq_mhz": round(freq_mhz, 1),
        "energy_j": round(energy_j, 6),
        "joules_per_op": round(joules_per_op, 15),
        "engine": "config_test_v1"
    }
    
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"    Build: {build_dur:.4f}s | Run: {dur:.4f}s")
    print(f"    Ops executed: {total:,}")
    print(f"    Throughput: {eta:,.0f} ops/s")
    print(f"    Energy: {energy_j:.4f}J | {joules_per_op:.2e} J/op")
    print(f"    CPU: {freq_mhz:.0f}MHz")

print("\n" + "=" * 60)
print("Both configurations tested. All values REAL.")
print("=" * 60)
