#!/usr/bin/env python3
"""
learn.py — simple epistemology logger
Records every lesson into a permanent ledger and updates the seed.
"""
import json, pathlib, sys
from datetime import datetime, timezone

BASE   = pathlib.Path.home() / "openroot"
LEDGER = BASE / "ledger" / "learning" / "lessons.jsonl"
SEED   = BASE / "session_seeds" / "current_seed.json"
LEDGER.parent.mkdir(parents=True, exist_ok=True)

def now():
    return datetime.now(timezone.utc).isoformat()

def load_seed():
    try:
        return json.loads(SEED.read_text())
    except:
        return {}

lesson = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "untitled lesson"

entry = {
    "ts": now(),
    "lesson": lesson,
    "note": "operator learning event"
}

with open(LEDGER, "a") as f:
    f.write(json.dumps(entry) + "\n")

seed = load_seed()
seed["last_lesson"] = entry
seed["ts"] = now()
SEED.write_text(json.dumps(seed, indent=2))

print("Lesson recorded →", LEDGER)
print("Seed updated with last_lesson")
print(json.dumps(entry, indent=2))
