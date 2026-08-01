#!/usr/bin/env python3
"""
OpenRoot Thermodynamic Instrumentation + Bottleneck Analysis
All measurements in WATTS (joules/second).
η = useful_watts / human_watts
Bottleneck = subsystem where human_watts > useful_watts (η < 1)
Replacement = swap human labor for computation where η < 1
"""

import json
import hashlib
import time
import os

LEDGER_PATH = "/sdcard/openroot/context_bridge/thermo_ledger.jsonl"
BOTTLENECK_PATH = "/sdcard/openroot/context_bridge/bottlenecks.jsonl"

# ── 12 ATOMIC FUNCTIONS (compact, measured in W) ──────────────

def f1_capture(data):
    """capture input data with timestamp"""
    return {"data": data, "ts": time.time(), "watts_in": 0}

def f2_hash(payload):
    """hash payload for integrity"""
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    payload["sha256"] = h
    return payload

def f3_aggregate(items):
    """collect results into unified structure"""
    return {"items": items, "count": len(items)}

def f4_pair(left, right):
    """bind two results together"""
    return {"left": left, "right": right}

def f5_commit(record):
    """commit result to permanent record"""
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record

def f6_verify(commit):
    """verify committed result"""
    expected = commit.get("sha256", "")
    recomputed = hashlib.sha256(
        json.dumps({k: v for k, v in commit.items() if k != "sha256"}, sort_keys=True).encode()
    ).hexdigest()
    return {"valid": expected == recomputed, "hash": recomputed}

def f7_landauer(cost_bits):
    """calculate thermodynamic energy cost in watts"""
    k = 1.380649e-23
    T = 300.0
    e_per_bit = k * T * 0.6931  # kT ln2
    # Convert to watts: energy_per_bit * bits_per_second
    # Assume cost_bits is bits processed this second
    return e_per_bit * cost_bits  # watts

def f8_observe(state):
    """monitor system state, return watts snapshot"""
    return {
        "subsystem": state.get("subsystem", "unknown"),
        "useful_watts": state.get("useful_watts", 0),
        "human_watts": state.get("human_watts", 0),
        "compute_watts": state.get("compute_watts", 0),
    }

def f9_store(data):
    """cache knowledge"""
    return {"cached": True, "key": hashlib.md5(str(data).encode()).hexdigest()[:8]}

def f10_yield(output):
    """produce output"""
    return {"yield": output}

def f11_adapt(data):
    """dynamically adjust — bottleneck detection"""
    useful = data.get("useful_watts", 0)
    human = data.get("human_watts", 0)
    compute = data.get("compute_watts", 0)
    
    eta = useful / human if human > 0 else float('inf')
    
    bottlenecks = []
    
    # Rule 1: Human labor exceeds useful output → replace with computation
    if eta < 1.0 and human > 0:
        bottlenecks.append({
            "subsystem": data.get("subsystem", "unknown"),
            "problem": "human_watts > useful_watts",
            "human_watts": human,
            "useful_watts": useful,
            "eta": round(eta, 4),
            "action": "REPLACE_WITH_COMPUTATION",
            "expected_compute_watts": compute,
            "eta_after_swap": round(useful / max(compute, 0.001), 4),
            "eta_gain": round((useful / max(compute, 0.001)) - eta, 4),
        })
    
    # Rule 2: Compute watts approaching Landauer limit
    landauer_w = f7_landauer(1e9)  # 1 billion bits/s baseline
    if compute > 0 and compute < landauer_w * 1e6:
        bottlenecks.append({
            "subsystem": data.get("subsystem", "unknown"),
            "problem": "near_landauer_floor",
            "compute_watts": compute,
            "landauer_floor_w": landauer_w,
            "action": "CANNOT_OPTIMIZE_FURTHER",
        })
    
    data["eta"] = round(eta, 4)
    data["bottlenecks"] = bottlenecks
    
    if bottlenecks:
        with open(BOTTLENECK_PATH, "a") as f:
            for b in bottlenecks:
                b["ts"] = time.time()
                f.write(json.dumps(b) + "\n")
    
    return data

def f12_sync(data):
    """synchronize across nodes — Merkle chain update"""
    prev_hash = "genesis"
    try:
        with open(LEDGER_PATH, "r") as f:
            lines = f.readlines()
            if lines:
                prev = json.loads(lines[-1])
                prev_hash = prev.get("merkle_hash", "genesis")
    except FileNotFoundError:
        pass
    
    current = json.dumps(data, sort_keys=True).encode()
    merkle_input = (prev_hash + hashlib.sha256(current).hexdigest()).encode()
    data["merkle_hash"] = hashlib.sha256(merkle_input).hexdigest()
    data["prev_hash"] = prev_hash
    return data

# ── LEDGER ENTRY SCHEMA ─────────────────────────────────────────
def create_entry(subsystem, useful_w, human_w, compute_w, notes=""):
    """
    All values in WATTS (joules/second).
    
    subsystem: name of the subsystem being measured
    useful_w: useful output power (W) — what the recipient receives
    human_w: human labor power input (W) — metabolic cost
    compute_w: computational power cost (W) — CPU/phone draw
    notes: free text annotation
    """
    entry = {
        "ts": time.time(),
        "subsystem": subsystem,
        "useful_watts": useful_w,
        "human_watts": human_w,
        "compute_watts": compute_w,
        "eta": round(useful_w / human_w, 4) if human_w > 0 else float('inf'),
        "eta_compute": round(useful_w / compute_w, 4) if compute_w > 0 else float('inf'),
        "notes": notes,
        "acre_ready": False,
    }
    return entry

# ── PRIMARY LOOP: measure → hash → adapt → commit → sync ───────
def run_measurement(entries):
    """
    Accept list of measurement dicts, run through atomic chain,
    detect bottlenecks, commit to ledger, sync Merkle chain.
    """
    results = []
    
    for e in entries:
        # f1: capture
        step = f1_capture(e)
        # f8: observe
        step = f8_observe(step["data"])
        # f11: adapt (bottleneck detection)
        step = f11_adapt(step)
        # f2: hash
        step = f2_hash(step)
        # f12: sync (Merkle chain)
        step = f12_sync(step)
        # f5: commit
        f5_commit(step)
        
        eta = step.get("eta", 0)
        acre_ready = eta > 1.0 and step["useful_watts"] > 0
        step["acre_ready"] = acre_ready
        
        results.append({
            "subsystem": step["subsystem"],
            "eta": eta,
            "eta_compute": step.get("eta_compute", 0),
            "bottlenecks": step.get("bottlenecks", []),
            "acre_ready": acre_ready,
            "merkle_hash": step["merkle_hash"][:16],
        })
    
    return results

# ── DEMO: First instrumentation measurements ───────────────────
if __name__ == "__main__":
    # Baseline measurements from immortal_context:
    # Passive ΔT Vehicle: 3930.1 W useful, 0 W human (passive)
    # Human metabolic labor: ~100W sustained, ~350W peak
    # Samsung A15 compute: ~3W sustained under load
    
    measurements = [
        create_entry(
            subsystem="phi_vortex_cascade",
            useful_w=3930.1,       # watts useful output (from locked model)
            human_w=0,             # passive — no human input once running
            compute_w=3.0,         # phone monitoring cost
            notes="φ-vortex baseline from locked model. Passive: human_w=0"
        ),
        create_entry(
            subsystem="stirling_extraction",
            useful_w=350.0,        # estimated shaft output
            human_w=100.0,          # 1 human maintenance hour equivalent
            compute_w=2.0,         # sensor monitoring
            notes="Stirling charge cycle: 5-8% tank capacity"
        ),
        create_entry(
            subsystem="cold_path_labyrinth",
            useful_w=800.0,        # cooling output
            human_w=350.0,         # peak labor: loading desiccant, water
            compute_w=1.5,         # temp logging
            notes="Desiccant + wet concrete + ground sink + radiative lid"
        ),
        create_entry(
            subsystem="manual_data_entry",
            useful_w=0.1,          # very little useful output
            human_w=100.0,         # human typing
            compute_w=0.5,        # phone screen
            notes="BOTTLENECK: human typing vs automated sensor capture"
        ),
        create_entry(
            subsystem="sensor_capture_auto",
            useful_w=5.0,          # useful data stream
            human_w=0,             # automated
            compute_w=1.0,         # ESP32 sensor node
            notes="Replacement for manual_data_entry: η jumps from 0.001 to 5.0"
        ),
    ]
    
    print("=" * 60)
    print("OPENROOT INSTRUMENTATION RUN")
    print("All measurements in WATTS (joules/second)")
    print("η = useful_watts / human_watts")
    print("=" * 60)
    
    results = run_measurement(measurements)
    
    for r in results:
        print(f"\nSubsystem: {r['subsystem']}")
        print(f"  η_human  = {r['eta']}")
        print(f"  η_compute = {r['eta_compute']}")
        print(f"  ACRE ready: {r['acre_ready']}")
        print(f"  Merkle: {r['merkle_hash']}")
        if r['bottlenecks']:
            for b in r['bottlenecks']:
                print(f"  ⚠ BOTTLENECK: {b['problem']}")
                print(f"    Action: {b['action']}")
                if 'eta_gain' in b:
                    print(f"    η gain from swap: +{b['eta_gain']}")
    
    print("\n" + "=" * 60)
    print(f"Ledger: {LEDGER_PATH}")
    print(f"Bottlenecks: {BOTTLENECK_PATH}")
    print("Run complete. Measure again after changes.")
    print("=" * 60)
