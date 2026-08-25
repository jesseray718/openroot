import json
from pathlib import Path
from datetime import datetime
import time

DATA_DIR = Path("/sdcard/openroot/data")
EVENTS = DATA_DIR / "events.jsonl"

def ensure():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def append_event(event_dict):
    ensure()
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event_dict, ensure_ascii=False) + "\n")

def read_last_hash():
    if not EVENTS.exists():
        return None
    last = None
    with EVENTS.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line
    if not last:
        return None
    obj = json.loads(last)
    return obj.get("hash_current_event")

def utc_local_info():
    now_local = datetime.now().astimezone()
    local_iso = now_local.isoformat()
    offset = now_local.strftime("%z")
    if offset:
        offset = offset[:3] + ":" + offset[3:]
    return local_iso, offset

def monotonic_now():
    return time.monotonic()
