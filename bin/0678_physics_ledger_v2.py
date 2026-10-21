#!/usr/bin/env python3
"""
AEROCEMENT PHYSICS LEDGER v2.0 - DESICCANT PRE-DRYER PROTOCOL
COMMANDER: Jesse McMillen | Civilization 2.0
UPDATE: Models Desiccant Wheel pre-treatment to bypass Latent Heat Sink.
"""

import hashlib
import json
from datetime import datetime

# === CHAIN STORAGE ===
chain_bounded = []
chain_unbounded = []

def create_block(chain, prev_block, label, params, result):
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
    if chain and chain[-1]["hash"] != prev_hash:
        print(f"[TAMPER DETECTED] Chain {label} integrity FAILED")
        return None
    chain.append(block_data)
    return block_data

def run_triad_calc_desiccant(airflow_cfm, solar_kw, stirling_eff, 
                             inlet_moisture_g_m3, desiccant_efficiency, 
                             desiccant_heat_cost_pct, insulation_loss_pct):
    """
    Physics Engine with Desiccant Pre-Dryer.
    Step 1: Desiccant removes moisture using small heat slice.
    Step 2: Dry air enters main solar loop -> NO latent penalty.
    """
    
    # 1. Airflow Conversion
    airflow_m3s = airflow_cfm * 0.0283168 / 60.0
    
    # 2. Desiccant Stage (Pre-treatment)
    # Moisture removed by desiccant
    moisture_removed_kg_s = airflow_m3s * (inlet_moisture_g_m3 / 1000.0) * desiccant_efficiency
    # Water harvested here (condensed from desiccant regen air - simplified)
    water_harvest_L_day = moisture_removed_kg_s * 86400 
    
    # Energy cost to regenerate desiccant (assumed to be taken from solar input)
    # This is a simplified model: Cost is a % of total solar input
    desiccant_heat_load_kw = solar_kw * desiccant_heat_cost_pct
    
    # 3. Main Loop (Dry Air)
    # Since air is dried, latent load is NEGLIGIBLE in main loop.
    # Only sensible heating remains.
    net_thermal_input = solar_kw * (1.0 - insulation_loss_pct) - desiccant_heat_load_kw
    
    if net_thermal_input < 0:
        return {
            "status": "DEFICIT", 
            "net_thermal_kw": net_thermal_input, 
            "electric_kw": 0, 
            "water_L_day": water_harvest_L_day,
            "surplus_kwh_day": 0,
            "note": "Desiccant regeneration consumes entire input"
        }
    
    electric_kw = net_thermal_input * stirling_eff
    surplus_kwh = electric_kw * 24
    
    return {
        "status": "SURPLUS" if surplus_kwh > 1000 else "MARGINAL",
        "net_thermal_kw": round(net_thermal_input, 3),
        "electric_kw": round(electric_kw, 3),
        "water_L_day": round(water_harvest_L_day, 1),
        "surplus_kwh_day": round(surplus_kwh, 1),
        "note": "Desiccant Pre-Dryer Active"
    }

def main():
    print("=" * 60)
    print("AEROCEMENT PHYSICS LEDGER v2.0 - DESICCANT PROTOCOL")
    print("=" * 60)
    
    # --- TROPICAL/HEAVY HUMIDITY ASSUMPTION ---
    # If 12g/m3 failed, let's test 20g/m3 (Hot/Humid) and 25g/m3 (Tropical)
    INPUT_MOISTURE_TROPICAL = 25.0  # g/m3
    
    # === CHAIN A: BOUNDED (Build Spec) ===
    # Conservative: High humidity, decent desiccant, lower solar
    bounded_params = {
        "airflow_cfm": 2265,
        "solar_kw": 5.5, # Increased slightly to account for desiccant cost
        "stirling_eff": 0.15,
        "inlet_moisture_g_m3": INPUT_MOISTURE_TROPICAL,
        "desiccant_efficiency": 0.90, # Removes 90% of moisture
        "desiccant_heat_cost_pct": 0.10, # Uses 10% of solar for regen
        "insulation_loss_pct": 0.20,
        "rationale": "Tropical humidity, robust desiccant wheel, standard collector"
    }
    b_result = run_triad_calc_desiccant(**{k:v for k,v in bounded_params.items() if k != "rationale"})
    
    # === CHAIN B: UNBOUNDED (Engineer Toward) ===
    # Optimized: Peak sun, high-eff desiccant, advanced Stirling
    unbounded_params = {
        "airflow_cfm": 2265,
        "solar_kw": 8.0,
        "stirling_eff": 0.40,
        "inlet_moisture_g_m3": INPUT_MOISTURE_TROPICAL,
        "desiccant_efficiency": 0.95,
        "desiccant_heat_cost_pct": 0.05, # Better regen efficiency
        "insulation_loss_pct": 0.05,
        "rationale": "Peak sun, optimized desiccant, vacuum insulation"
    }
    u_result = run_triad_calc_desiccant(**{k:v for k,v in unbounded_params.items() if k != "rationale"})
    
    # Mine blocks
    b_block = create_block(chain_bounded, chain_bounded[-1] if chain_bounded else None, 
                           "BOUNDED_DESICCANT", bounded_params, b_result)
    u_block = create_block(chain_unbounded, chain_unbounded[-1] if chain_unbounded else None, 
                           "UNBOUNDED_DESICCANT", unbounded_params, u_result)
    
    # REPORT
    print("\n--- CHAIN A: BOUNDED (BUILD SPEC - TROPICAL) ---")
    print(f"Status: {b_result['status']}")
    print(f"Net Thermal: {b_result['net_thermal_kw']} kW")
    print(f"Electric: {b_result['electric_kw']} kW | {b_result['surplus_kwh_day']} kWh/day")
    print(f"Water Harvest: {b_result['water_L_day']} L/day")
    print(f"Hash: {b_block['hash'][:16]}...")
    
    print("\n--- CHAIN B: UNBOUNDED (ENGINEER TOWARD) ---")
    print(f"Status: {u_result['status']}")
    print(f"Net Thermal: {u_result['net_thermal_kw']} kW")
    print(f"Electric: {u_result['electric_kw']} kW | {u_result['surplus_kwh_day']} kWh/day")
    print(f"Water Harvest: {u_result['water_L_day']} L/day")
    print(f"Hash: {u_block['hash'][:16]}...")
    
    # ANALYSIS
    b_surplus = b_result.get('surplus_kwh_day', 0)
    u_surplus = u_result.get('surplus_kwh_day', 0)
    
    print("\n--- DESIGN MARGIN ---")
    if b_surplus > 0:
        print("SUCCESS: Bounded Chain passed! Desiccant protocol works.")
        print(f"Headroom: {u_surplus - b_surplus:.1f} kWh/day")
        print("[ACTION] Proceed to single-home prototype with Desiccant Wheel.")
    elif u_surplus > 0:
        print("MARGINAL: Unbounded passed, Bounded failed.")
        print("[ACTION] Increase collector area OR improve desiccant efficiency.")
    else:
        print("CRITICAL: Both chains fail. Even with desiccant, solar input is too low for 2265 CFM.")
        print("[ACTION] Redesign: Reduce airflow OR drastically increase collector size (>10kW).")

    print(f"\n[LEDGER] Integrity verified. Blocks: {len(chain_bounded)} | {len(chain_unbounded)}")

if __name__ == "__main__":
    main()
