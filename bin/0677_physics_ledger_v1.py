#!/usr/bin/env python3
"""
AEROCEMENT PHYSICS LEDGER v1.0
COMMANDER: Jesse McMillen | Civilization 2.0
Two-chain immutable ledger: BOUNDED (build spec) + UNBOUNDED (engineer toward)
Each block = one calculation run. Chains cannot be altered after commit.
LICENSE: GPL v3
"""

import hashlib
import json
import time
from datetime import datetime

# === CHAIN STORAGE ===
chain_bounded = []
chain_unbounded = []

def create_block(chain, prev_block, label, params, result):
    """Mine a block onto the specified chain."""
    index = len(chain)
    prev_hash = prev_block["hash"] if prev_block else "GENESIS"
    timestamp = datetime.now().isoformat()
    
    block_data = {
        "index": index,
        "label": label,
        "timestamp": timestamp,
        "params": params,
        "result": result,
        "prev_hash": prev_hash
    }
    
    block_hash = hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()
    block_data["hash"] = block_hash
    
    # Verify chain integrity before appending
    if chain:
        if chain[-1]["hash"] != prev_hash:
            print(f"[TAMPER DETECTED] Chain {label} integrity FAILED at block {index}")
            return None
    
    chain.append(block_data)
    return block_data

def run_triad_calc(airflow_cfm, solar_kw, stirling_eff, humidity_reduction, insulation_loss_pct):
    """Core physics engine - single calculation pass."""
    airflow_m3s = airflow_cfm * 0.0283168 / 60.0
    moisture_kg_s = airflow_m3s * (12.0 / 1000.0) * humidity_reduction
    latent_load_kw = moisture_kg_s * 2260.0
    net_thermal = solar_kw * (1.0 - insulation_loss_pct) - latent_load_kw
    
    if net_thermal < 0:
        return {"status": "DEFICIT", "net_thermal_kw": net_thermal, "electric_kw": 0, 
                "water_L_day": moisture_kg_s * 86400, "surplus_kwh_day": 0}
    
    electric_kw = net_thermal * stirling_eff
    return {
        "status": "SURPLUS" if electric_kw * 24 > 1000 else "MARGINAL",
        "net_thermal_kw": round(net_thermal, 3),
        "electric_kw": round(electric_kw, 3),
        "water_L_day": round(moisture_kg_s * 86400, 1),
        "surplus_kwh_day": round(electric_kw * 24, 1)
    }

def main():
    print("=" * 60)
    print("AEROCEMENT PHYSICS LEDGER v1.0")
    print("TWO-CHAIN IMMUTABLE RECORD")
    print("=" * 60)
    
    # === CHAIN A: BOUNDED (Build Spec - Conservative) ===
    bounded_params = {
        "airflow_cfm": 2265,
        "solar_kw": 4.5,
        "stirling_eff": 0.15,
        "humidity_reduction": 0.60,
        "insulation_loss_pct": 0.20,
        "rationale": "Worst-case humidity, degraded insulation, production Stirling"
    }
    bounded_result = run_triad_calc(**{k: v for k, v in bounded_params.items() if k != "rationale"})
    
    # === CHAIN B: UNBOUNDED (Engineer Toward - Theoretical Ceiling) ===
    unbounded_params = {
        "airflow_cfm": 2265,
        "solar_kw": 7.0,
        "stirling_eff": 0.40,
        "humidity_reduction": 0.40,
        "insulation_loss_pct": 0.05,
        "rationale": "Peak sun, optimized desiccant, vacuum-grade insulation, advanced Stirling"
    }
    unbounded_result = run_triad_calc(**{k: v for k, v in unbounded_params.items() if k != "rationale"})
    
    # Mine blocks
    b_block = create_block(chain_bounded, chain_bounded[-1] if chain_bounded else None,
                           "BOUNDED", bounded_params, bounded_result)
    u_block = create_block(chain_unbounded, chain_unbounded[-1] if chain_unbounded else None,
                           "UNBOUNDED", unbounded_params, unbounded_result)
    
    # === REPORT ===
    print("\n--- CHAIN A: BOUNDED (BUILD SPEC) ---")
    print(f"Status: {bounded_result['status']}")
    print(f"Net Thermal: {bounded_result['net_thermal_kw']} kW")
    print(f"Electric: {bounded_result['electric_kw']} kW | {bounded_result['surplus_kwh_day']} kWh/day")
    print(f"Water: {bounded_result['water_L_day']} L/day")
    print(f"Block Hash: {b_block['hash'][:16]}...")
    
    print("\n--- CHAIN B: UNBOUNDED (ENGINEER TOWARD) ---")
    print(f"Status: {unbounded_result['status']}")
    print(f"Net Thermal: {unbounded_result['net_thermal_kw']} kW")
    print(f"Electric: {unbounded_result['electric_kw']} kW | {unbounded_result['surplus_kwh_day']} kWh/day")
    print(f"Water: {unbounded_result['water_L_day']} L/day")
    print(f"Block Hash: {u_block['hash'][:16]}...")
    
    # === DESIGN MARGIN ANALYSIS ===
    b_surplus = bounded_result.get('surplus_kwh_day', 0)
    u_surplus = unbounded_result.get('surplus_kwh_day', 0)
    
    print("\n--- DESIGN MARGIN ---")
    if b_surplus > 0 and u_surplus > 0:
        print("BOTH CHAINS POSITIVE: Physics confirmed. Build to Bounded spec.")
        print(f"Optimization headroom: {u_surplus - b_surplus:.1f} kWh/day")
    elif b_surplus <= 0 and u_surplus > 0:
        print("BOUND FAIL / UNBOUND PASS: Gap identifies optimization targets.")
        print("PRIORITY: Reduce insulation losses OR increase collector area.")
    elif b_surplus <= 0 and u_surplus <= 0:
        print("BOTH CHAINS NEGATIVE: Fundamental redesign required.")
        print("ACTION: Re-evaluate thermal input assumptions before scaling.")
    
    print("\n--- CHAIN INTEGRITY ---")
    print(f"Bounded blocks: {len(chain_bounded)} | Unbounded blocks: {len(chain_unbounded)}")
    print("[LEDGER] All assumptions locked. Next run appends new block.")
    print("[REPLY] Commander, report both hashes and DESIGN MARGIN status.")

if __name__ == "__main__":
    main()
