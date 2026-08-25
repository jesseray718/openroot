#!/data/data/com.termux/files/usr/bin/python3
import os, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

SDCARD = Path("/sdcard/openroot")
SEED_DIR = SDCARD / "session_seeds"
SEED_DIR.mkdir(parents=True, exist_ok=True)

ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
seed = {
    "ts": ts,
    "device": "A15",
    "R": 1.0,
    "coordination_cost": 0.0,
    "openroot_exists": (Path("/data/data/com.termux/files/home/openroot")).exists(),
    "agape_kb_exists": (SDCARD / "agape_kb").exists(),
}
path = SEED_DIR / f"offline_a15_{ts}.json"
path.write_text(json.dumps(seed, indent=2))
print(f"Seed written → {path}")
print(json.dumps(seed, indent=2))
