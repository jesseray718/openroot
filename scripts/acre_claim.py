#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime, timezone

OPENROOT_HOME = os.getenv("OPENROOT_HOME", os.path.expanduser("~/openroot"))
CLAIMS_DIR = os.path.join(OPENROOT_HOME, "data", "claims")
LEDGER_SCRIPT = os.path.join(OPENROOT_HOME, "scripts", "ledger.py")

def create_claim(claim_id, metric_type, value, unit, notes=""):
    os.makedirs(CLAIMS_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    claim_data = {
        "claim_id": claim_id,
        "timestamp": timestamp,
        "metric_type": metric_type,
        "value": value,
        "unit": unit,
        "notes": notes
    }
    
    # Save individual JSON claim artifact
    claim_filename = f"{claim_id}.json"
    claim_path = os.path.join(CLAIMS_DIR, claim_filename)
    with open(claim_path, "w", encoding="utf-8") as f:
        json.dump(claim_data, f, indent=2)
        
    print(f"Created physical work claim artifact: {claim_path}")
    
    # Commit claim into the main knowledge ledger
    if os.path.exists(LEDGER_SCRIPT):
        ledger_content = f"PoPW Claim [{claim_id}]: {metric_type} = {value} {unit} | {notes}"
        subprocess.run(["python3", LEDGER_SCRIPT, "append", ledger_content, f"popw,claim,{metric_type}"])

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python acre_claim.py [claim_id] [metric_type] [value] [unit] [notes]")
        print("Example: python acre_claim.py ACRE-0002 thermal_energy 1250.5 joules 'Aero-Disc test run'")
        sys.exit(1)
        
    claim_id = sys.argv[1]
    metric_type = sys.argv[2]
    value = sys.argv[3]
    unit = sys.argv[4]
    notes = sys.argv[5] if len(sys.argv) > 5 else ""
    
    create_claim(claim_id, metric_type, value, unit, notes)
