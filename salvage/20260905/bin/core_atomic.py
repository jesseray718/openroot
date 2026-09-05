#!/usr/bin/env python3
"""
core_atomic.py v1.2
OpenRoot Framework: Atomic Computation Units
Principles: Permaculture (Observe/Interact), Energy Efficiency, Modular Design
Author: Jesse Ray / OpenRoot LLC
License: AGPL-3.0
"""

import sys
import os
import json
import time
import hashlib
import random
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION AXIOMS ---
OPENROOT_ROOT = Path("/sdcard/openroot")
CONTEXT_DB = OPENROOT_ROOT / "storage" / "context.json"
LOG_DIR = OPENROOT_ROOT / "logs"
MEMBER_DB = OPENROOT_ROOT / "storage" / "members.json"

# Ensure directories exist (Catch & Store Energy)
for p in [CONTEXT_DB.parent, LOG_DIR]:
    p.mkdir(parents=True, exist_ok=True)

def log_event(event_type, data, duration_ms):
    """Append event to context bridge with energy timestamp."""
    record = {
        "ts": datetime.utcnow().isoformat(),
        "func": event_type,
        "duration_ms": duration_ms,
        "data_hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8],
        "payload": data
    }
    
    # Load existing context
    try:
        if CONTEXT_DB.exists():
            with open(CONTEXT_DB, 'r') as f:
                context = json.load(f)
        else:
            context = {"events": [], "state": "init"}
    except Exception:
        context = {"events": [], "state": "corrupted_recovery"}

    context["events"].append(record)
    context["last_update"] = record["ts"]
    
    # Persist (Atomic Write)
    temp_path = str(CONTEXT_DB) + ".tmp"
    with open(temp_path, 'w') as f:
        json.dump(context, f, indent=2)
    os.replace(temp_path, str(CONTEXT_DB))
    
    print(f"[SYNC] Context Bridge updated: {record['data_hash']}")

def f1_board_register(args):
    """Register & Verify Board Member. Returns verification hash."""
    start = time.perf_counter()
    if len(args) < 2:
        return {"error": "Usage: f1 <member_id> <role>", "code": 1}
    
    member_id, role = args[0], args[1]
    # Simulate cryptographic verification (Replace with actual sig check)
    salt = os.urandom(16).hex()
    ver_hash = hashlib.sha256(f"{member_id}:{role}:{salt}".encode()).hexdigest()
    
    result = {"status": "verified", "id": member_id, "role": role, "hash": ver_hash[:16]}
    duration = (time.perf_counter() - start) * 1000
    log_event("BOARD_REGISTER", result, duration)
    return result

def f2_crispr_frame(args):
    """Generate CRISPR-frame membership catalog schema."""
    start = time.perf_counter()
    version = args[0] if args else "v1.0"
    
    frame = {
        "schema_version": version,
        "target": "member_record",
        "guide_rna": ["id", "role", "energy_cost", "last_active"],
        "cut_sites": ["admin_override", "revocation_trigger"],
        "pam_sequence": "AGPL-3.0"
    }
    
    result = {"frame": frame, "ready": True}
    duration = (time.perf_counter() - start) * 1000
    log_event("CRISPR_FRAME", result, duration)
    return result

def f3_crud_member(args):
    """CRUD operations on member records. Args: [op, id, data_json]"""
    start = time.perf_counter()
    if len(args) < 2:
        return {"error": "Usage: f3 <create|read|update|delete> <id> [data]", "code": 1}
    
    op, uid = args[0], args[1]
    data = json.loads(args[2]) if len(args) > 2 else {}
    
    # Load DB
    db = {}
    if MEMBER_DB.exists():
        try:
            with open(MEMBER_DB) as f: db = json.load(f)
        except: pass
    
    if op == "create":
        if uid in db: return {"error": "Exists", "code": 1}
        db[uid] = {**data, "created": datetime.utcnow().isoformat()}
    elif op == "read":
        return db.get(uid, {"error": "Not Found"})
    elif op == "update":
        if uid not in db: return {"error": "Not Found", "code": 1}
        db[uid].update(data)
    elif op == "delete":
        if uid in db: del db[uid]
    
    # Save
    with open(MEMBER_DB, 'w') as f: json.dump(db, f, indent=2)
    
    result = {"op": op, "id": uid, "success": True}
    duration = (time.perf_counter() - start) * 1000
    log_event("CRUD_MEMBER", result, duration)
    return result

def f4_clerk_transition(args):
    """Check clerk state transition. Args: [current_state, target_state]"""
    start = time.perf_counter()
    if len(args) < 2: return {"error": "Usage: f4 <curr> <target>", "code": 1}
    
    curr, target = args[0], args[1]
    valid_transitions = {
        "idle": ["active", "sleep"],
        "active": ["processing", "idle"],
        "processing": ["complete", "error"],
        "error": ["reset", "idle"]
    }
    
    allowed = curr in valid_transitions and target in valid_transitions[curr]
    result = {"allowed": allowed, "from": curr, "to": target}
    
    duration = (time.perf_counter() - start) * 1000
    log_event("CLERK_TRANSITION", result, duration)
    return result

def f5_alphabet_check(args):
    """AI Memory Prime / Alphabet Check. Returns entropy score."""
    start = time.perf_counter()
    seed = args[0] if args else "default_seed"
    
    # Simulate memory priming entropy calculation
    entropy = hashlib.sha256(seed.encode()).digest()
    score = sum(entropy) / 255.0 # Normalized 0-1
    
    result = {"seed": seed, "entropy_score": round(score, 4), "prime": True}
    duration = (time.perf_counter() - start) * 1000
    log_event("ALPHABET_CHECK", result, duration)
    return result

def f6_eth_faucet(args):
    """Ethereum Faucet Balance Check (L1 Simulation)."""
    start = time.perf_counter()
    addr = args[0] if args else "0x0000...dead"
    
    # Simulate RPC call latency and random balance
    time.sleep(random.uniform(0.05, 0.15)) 
    balance = round(random.uniform(0.001, 0.5), 4)
    
    result = {"address": addr, "balance_eth": balance, "network": "L1_Mainnet"}
    duration = (time.perf_counter() - start) * 1000
    log_event("ETH_FAUCET", result, duration)
    return result

def f7_context_bridge_sync(args):
    """Force sync and integrity check of Context Bridge."""
    start = time.perf_counter()
    
    if not CONTEXT_DB.exists():
        return {"status": "empty", "message": "No context found"}
    
    try:
        with open(CONTEXT_DB) as f:
            data = json.load(f)
        count = len(data.get("events", []))
        last_ts = data.get("last_update", "unknown")
        
        result = {"status": "synced", "event_count": count, "last_ts": last_ts}
    except Exception as e:
        result = {"status": "error", "msg": str(e)}
    
    duration = (time.perf_counter() - start) * 1000
    log_event("CONTEXT_SYNC", result, duration)
    return result

# --- MAIN DISPATCHER ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nRun: python core_atomic.py f<N> [args]")
        sys.exit(0)

    func_map = {
        "f1": f1_board_register,
        "f2": f2_crispr_frame,
        "f3": f3_crud_member,
        "f4": f4_clerk_transition,
        "f5": f5_alphabet_check,
        "f6": f6_eth_faucet,
        "f7": f7_context_bridge_sync
    }

    cmd = sys.argv[1]
    if cmd not in func_map:
        print(f"Unknown function: {cmd}")
        sys.exit(1)

    args = sys.argv[2:]
    try:
        output = func_map[cmd](args)
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)
