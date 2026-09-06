#!/data/data/com.termux/files/usr/bin/python3
import hashlib, json, datetime
from pathlib import Path
BASE = Path("/sdcard/openroot/tiemit/genesis")
BASE.mkdir(parents=True, exist_ok=True)
void = {
  "timestamp": datetime.datetime.utcnow().isoformat()+"Z",
  "state": "VOID",
  "resonance": 1.0,
  "eta_law": "useful_joules / human_joules",
  "coordination_cost": None
}
h = hashlib.sha256(json.dumps(void, sort_keys=True).encode()).hexdigest()
record = {
  "tiemit": "002",
  "genesis_hash": h,
  "void_state": void,
  "interpretation": "R=1.0 forces C=0; this hash is the irreversible root of the compound",
  "absolute_paths": True,
  "serve": "the least among us"
}
(BASE / "genesis_hash.json").write_text(json.dumps(record, indent=2))
print(h)
print(str(BASE / "genesis_hash.json"))
