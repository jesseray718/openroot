#!/usr/bin/env python3
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "storage" / "agape_node"
QUEUE_FILE = DATA_DIR / "queue.jsonl"
DEDUP_FILE = DATA_DIR / "dedup_index.json"
STATE_FILE = DATA_DIR / "state.json"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ensure():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DEDUP_FILE.exists():
        DEDUP_FILE.write_text("{}")
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({
            "created_at": now_iso(),
            "processed": 0,
            "duplicates": 0,
            "last_run": None
        }, indent=2))

def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2))

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def enqueue(payload: dict):
    ensure()
    raw = json.dumps(payload, sort_keys=True)
    h = sha256_text(raw)

    dedup = load_json(DEDUP_FILE, {})
    state = load_json(STATE_FILE, {})

    if h in dedup:
        state["duplicates"] = state.get("duplicates", 0) + 1
        save_json(STATE_FILE, state)
        return {"status": "duplicate", "hash": h, "ref": dedup[h]}

    event = {
        "id": h[:16],
        "hash": h,
        "payload": payload,
        "enqueued_at": now_iso(),
        "priority": quadratic_need_score(payload)
    }

    with QUEUE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    dedup[h] = {"id": event["id"], "first_seen": event["enqueued_at"]}
    save_json(DEDUP_FILE, dedup)

    return {"status": "enqueued", "id": event["id"], "hash": h, "priority": event["priority"]}

def quadratic_need_score(payload: dict) -> float:
    urgency = float(payload.get("urgency", 1))
    impact = float(payload.get("impact", 1))
    return (urgency ** 2) * impact

def read_queue():
    if not QUEUE_FILE.exists():
        return []
    rows = []
    for line in QUEUE_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def write_queue(rows):
    with QUEUE_FILE.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

def process(limit=10):
    ensure()
    rows = read_queue()
    rows.sort(key=lambda x: x.get("priority", 0), reverse=True)

    take = rows[:limit]
    rest = rows[limit:]

    state = load_json(STATE_FILE, {})
    for item in take:
        # placeholder for real work
        time.sleep(0.01)
        state["processed"] = state.get("processed", 0) + 1

    state["last_run"] = now_iso()
    save_json(STATE_FILE, state)
    write_queue(rest)

    return {"processed_now": len(take), "remaining": len(rest)}

def status():
    ensure()
    q = read_queue()
    dedup = load_json(DEDUP_FILE, {})
    state = load_json(STATE_FILE, {})
    return {
        "queue_size": len(q),
        "dedup_entries": len(dedup),
        "state": state
    }

def purge(confirm=False):
    if not confirm:
        return {"error": "refusing purge without confirm=True"}
    for p in [QUEUE_FILE, DEDUP_FILE, STATE_FILE]:
        if p.exists():
            p.unlink()
    return {"status": "purged"}

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Agape Node Offline Worker")
    sub = ap.add_subparsers(dest="cmd")

    e = sub.add_parser("enqueue")
    e.add_argument("--payload", required=True, help='JSON payload e.g. {"task":"x","urgency":2,"impact":3}')

    sub.add_parser("status")
    p = sub.add_parser("process")
    p.add_argument("--limit", type=int, default=10)

    g = sub.add_parser("purge")
    g.add_argument("--confirm", action="store_true")

    args = ap.parse_args()

    if args.cmd == "enqueue":
        print(json.dumps(enqueue(json.loads(args.payload)), indent=2))
    elif args.cmd == "status":
        print(json.dumps(status(), indent=2))
    elif args.cmd == "process":
        print(json.dumps(process(limit=args.limit), indent=2))
    elif args.cmd == "purge":
        print(json.dumps(purge(confirm=args.confirm), indent=2))
    else:
        ap.print_help()
