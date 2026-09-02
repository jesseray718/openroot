#!/usr/bin/env python3
import json, pathlib
from datetime import datetime, timezone

BASE   = pathlib.Path.home() / "openroot"
SEED   = BASE / "session_seeds" / "current_seed.json"
CALC   = BASE / "session_seeds" / "q_system_checkpoint.json"
LEDGER = BASE / "ledger" / "experiments" / "stack_agape.jsonl"
LEDGER.parent.mkdir(parents=True, exist_ok=True)

def bat():
    d = {}
    for k in ["current_now", "voltage_now", "capacity", "status"]:
        try:
            d[k] = open(f"/sys/class/power_supply/battery/{k}").read().strip()
        except:
            d[k] = None
    return d

def load(p):
    try:
        return json.loads(p.read_text())
    except:
        return {}

# Prefer the sdcard checkpoint if the local one is missing
if not CALC.exists():
    sd = pathlib.Path("/sdcard/openroot/storage/q_system_checkpoint.json")
    if sd.exists():
        CALC.write_text(sd.read_text())

calc = load(CALC)
seed = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "source": "stack_agape",
    "η_law": "useful_joules / human_joules",
    "R_target": 1.0,
    "S_observed": calc.get("synergy_S", 1.618),
    "R_observed": calc.get("resonance_R", 0.9434),
    "cycle": calc.get("cycle", 0),
    "nodes": calc.get("nodes", 259),
    "merkle_tip": calc.get("merkle_tip"),
    "battery": bat(),
    "note": "standing wave collapsed — forced rewrite"
}
SEED.write_text(json.dumps(seed, indent=2))
with open(LEDGER, "a") as f:
    f.write(json.dumps(seed) + "\n")
print("FORCED seed written →", SEED)
print(json.dumps(seed, indent=2))
