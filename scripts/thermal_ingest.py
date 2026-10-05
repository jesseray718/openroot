#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime, timezone

OPENROOT_HOME = os.getenv("OPENROOT_HOME", os.path.expanduser("~/openroot"))
THERMAL_DIR = os.path.join(OPENROOT_HOME, "data", "thermal_logs")
LEDGER_SCRIPT = os.path.join(OPENROOT_HOME, "scripts", "ledger.py")

def log_thermal_run(run_id, inlet_temp_c, outlet_temp_c, flow_rate_lpm, notes=""):
    os.makedirs(THERMAL_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Calculate temperature delta and approximate thermal power output (Water baseline: ~4.184 kJ/L·°C)
    delta_t = outlet_temp_c - inlet_temp_c
    # Power in kW = (Flow L/min / 60) * 4.184 kJ/L·°C * Delta T (°C)
    power_kw = (flow_rate_lpm / 60.0) * 4.184 * delta_t if delta_t > 0 else 0.0
    
    run_data = {
        "run_id": run_id,
        "timestamp": timestamp,
        "device": "Aero-Disc Volumetric Heat Exchanger",
        "metrics": {
            "inlet_temp_c": inlet_temp_c,
            "outlet_temp_c": outlet_temp_c,
            "delta_t_c": delta_t,
            "flow_rate_lpm": flow_rate_lpm,
            "estimated_power_kw": round(power_kw, 3)
        },
        "notes": notes
    }
    
    # Save individual thermal run JSON artifact
    run_filename = f"{run_id}.json"
    run_path = os.path.join(THERMAL_DIR, run_filename)
    with open(run_path, "w", encoding="utf-8") as f:
        json.dump(run_data, f, indent=2)
        
    print(f"Logged Aero-Disc thermal run artifact: {run_path}")
    
    # Commit run into the main knowledge ledger
    if os.path.exists(LEDGER_SCRIPT):
        ledger_content = f"Aero-Disc Run [{run_id}]: DeltaT={delta_t:.2f}C, Flow={flow_rate_lpm} LPM, Power={power_kw:.3f} kW | {notes}"
        subprocess.run(["python3", LEDGER_SCRIPT, "append", ledger_content, "thermal,aero-disc,exchanger"])

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python thermal_ingest.py [run_id] [inlet_temp_c] [outlet_temp_c] [flow_rate_lpm] [notes]")
        print("Example: python thermal_ingest.py RUN-001 22.5 48.0 3.5 'Passive solar absorption test'")
        sys.exit(1)
        
    run_id = sys.argv[1]
    inlet_temp_c = float(sys.argv[2])
    outlet_temp_c = float(sys.argv[3])
    flow_rate_lpm = float(sys.argv[4])
    notes = sys.argv[5] if len(sys.argv) > 5 else ""
    
    log_thermal_run(run_id, inlet_temp_c, outlet_temp_c, flow_rate_lpm, notes)
