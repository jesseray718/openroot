#!/usr/bin/env python3
"""
OpenRoot Thermodynamic Mint
Step = Contribution (Vector)
Work = Joules/Second (Scalar/Power)
"""
import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

LEDGER_PATH = Path("data/thermodynamics/power_ledger.jsonl")
STEP_PATH = Path("data/thermodynamics/contribution_ledger.jsonl")

def mint_step(node_id, action, goal_id):
    """Record a contribution step."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node": node_id,
        "action": action,
        "goal": goal_id,
        "type": "STEP"
    }
    _seal(record, STEP_PATH)
    print(f"[step] Contribution sealed for {node_id}: {action}")

def mint_work(node_id, joules, seconds):
    """Record thermodynamic work (Power = J/s)."""
    power = joules / seconds if seconds > 0 else 0
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node": node_id,
        "energy_j": joules,
        "time_s": seconds,
        "power_watts": power,
        "type": "WORK"
    }
    _seal(record, LEDGER_PATH)
    print(f"[work] Thermodynamic work sealed: {power:.4f} Watts")

def _seal(record, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Simple hash-chaining for the thermo-ledger
    raw_data = json.dumps(record, sort_keys=True).encode()
    record["hash"] = hashlib.sha256(raw_data).hexdigest()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: thermo_mint.py [step|work] [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "step":
        mint_step(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "work":
        mint_work(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
