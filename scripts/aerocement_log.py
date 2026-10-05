#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime, timezone

OPENROOT_HOME = os.getenv("OPENROOT_HOME", os.path.expanduser("~/openroot"))
MIX_DIR = os.path.join(OPENROOT_HOME, "data", "mix_logs")
LEDGER_SCRIPT = os.path.join(OPENROOT_HOME, "scripts", "ledger.py")

def log_aerocement_batch(batch_id, cement_kg, slurry_liters, surfactant_ml, fiber_type, fiber_grams, notes=""):
    os.makedirs(MIX_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    batch_data = {
        "batch_id": batch_id,
        "timestamp": timestamp,
        "material": "Aerocement 2.0",
        "components": {
            "portland_cement_kg": cement_kg,
            "xanthan_alcohol_slurry_liters": slurry_liters,
            "surfactant_dawn_ml": surfactant_ml,
            "fiber_reinforcement": {
                "type": fiber_type,
                "amount_grams": fiber_grams
            }
        },
        "notes": notes
    }
    
    # Save individual batch JSON artifact
    batch_filename = f"{batch_id}.json"
    batch_path = os.path.join(MIX_DIR, batch_filename)
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, indent=2)
        
    print(f"Logged Aerocement 2.0 batch artifact: {batch_path}")
    
    # Commit batch into the main knowledge ledger
    if os.path.exists(LEDGER_SCRIPT):
        ledger_content = f"Aerocement 2.0 Batch [{batch_id}]: Cement={cement_kg}kg, Slurry={slurry_liters}L, Surfactant={surfactant_ml}ml, Fiber={fiber_grams}g {fiber_type} | {notes}"
        subprocess.run(["python3", LEDGER_SCRIPT, "append", ledger_content, "material,aerocement,mix"])

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python aerocement_log.py [batch_id] [cement_kg] [slurry_liters] [surfactant_ml] [fiber_type] [fiber_grams] [notes]")
        print("Example: python aerocement_log.py BATCH-001 50.0 12.5 15.0 hemp 250 'Stator motor mixed control batch'")
        sys.exit(1)
        
    batch_id = sys.argv[1]
    cement_kg = float(sys.argv[2])
    slurry_liters = float(sys.argv[3])
    surfactant_ml = float(sys.argv[4])
    fiber_type = sys.argv[5]
    fiber_grams = float(sys.argv[6])
    notes = sys.argv[7] if len(sys.argv) > 7 else ""
    
    log_aerocement_batch(batch_id, cement_kg, slurry_liters, surfactant_ml, fiber_type, fiber_grams, notes)
