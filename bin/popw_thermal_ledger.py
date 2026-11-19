#!/usr/bin/env python3
"""PoPW Thermal Ledger — append-only hash-linked, Newton-tip aware."""
import json, hashlib, time, os, sys, pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(os.environ.get("OPENROOT_ROOT", "/home/jesse/openroot")).resolve()
LEDGER = ROOT / "ledger" / "popw_thermal.jsonl"
NEWTON = ROOT / "ledger" / "newton_chain.jsonl"

def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def tip(path):
    if not path.exists() or path.stat().st_size == 0:
        return None
    last = None
    with open(path) as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    return last

def init():
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER.exists() or LEDGER.stat().st_size == 0:
        g = {
            "id": "genesis",
            "ts": "2026-09-02T00:00:00Z",
            "type": "genesis",
            "prev": None,
            "payload": {"note": "PoPW thermal + Newton fusion", "eta_law": "useful_joules / human_joules"},
        }
        g["hash"] = sha({k: g[k] for k in ("id", "ts", "type", "prev", "payload")})
        with open(LEDGER, "w") as f:
            f.write(json.dumps(g) + "\n")
        print("initialized", LEDGER)
    if not NEWTON.exists():
        with open(NEWTON, "w") as f:
            f.write(json.dumps({"id": "newton-genesis", "ts": datetime.now(timezone.utc).isoformat(), "postulate": "N00-N16 locked", "prev": None}) + "\n")
        print("initialized", NEWTON)

def add(payload, human_joules=0.0, useful_joules=0.0):
    init()
    prev = tip(LEDGER)
    prev_hash = prev["hash"] if prev else None
    rec = {
        "id": f"popw-{int(time.time()*1000)}",
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": "thermal_cycle",
        "prev": prev_hash,
        "payload": {
            "cycle_id": payload.get("cycle_id"),
            "models": payload.get("models", []),
            "recall_hits": payload.get("recall_hits"),
            "questions": payload.get("questions"),
            "eta": round(useful_joules / human_joules, 6) if human_joules > 0 else None,
            "human_joules": human_joules,
            "useful_joules": useful_joules,
            "evidence": payload.get("evidence", []),
            "newton_tip": (tip(NEWTON) or {}).get("id"),
            "pod_root": payload.get("pod_root"),
            "db_used": payload.get("db_used"),
        },
    }
    rec["hash"] = sha({k: rec[k] for k in ("id", "ts", "type", "prev", "payload")})
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({"written": rec["id"], "hash": rec["hash"][:16], "eta": rec["payload"]["eta"]}))
    return rec

def verify():
    init()
    prev_hash = None
    count = 0
    with open(LEDGER) as f:
        for line in f:
            rec = json.loads(line)
            expected = sha({k: rec[k] for k in ("id", "ts", "type", "prev", "payload")})
            if rec["hash"] != expected or rec["prev"] != prev_hash:
                print("FAIL at", rec["id"])
                return False
            prev_hash = rec["hash"]
            count += 1
    print(f"OK {count} records tip={prev_hash[:16] if prev_hash else None}")
    return True

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tip"
    if cmd == "init":
        init()
    elif cmd == "add":
        payload = json.loads(sys.argv[2])
        hj = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        uj = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
        add(payload, hj, uj)
    elif cmd == "verify":
        sys.exit(0 if verify() else 1)
    elif cmd == "tip":
        t = tip(LEDGER)
        print(json.dumps(t, indent=2) if t else "empty")
    else:
        print("usage: init | add <json> [human_j] [useful_j] | verify | tip")
