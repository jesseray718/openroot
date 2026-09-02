#!/usr/bin/env python3
"""
OPENROOT REAL-TIME OBSERVER — Fixed version
Reads ~/.bash_history directly, runs each line through 12 atoms,
yields prioritized insights in real-time.
"""
import json, hashlib, sys, time
from datetime import datetime, timezone

def f1_capture(line, source="bash_history"):
    return {
        "type": "capture",
        "raw": line.strip(),
        "source": source,
        "ts": datetime.now(timezone.utc).isoformat(),
        "len": len(line)
    }

def f2_hash(captured):
    payload = json.dumps(captured, sort_keys=True, ensure_ascii=True)
    return {
        "type": "hash",
        "input_ref": captured.get("raw", "")[:8],
        "full_hash": hashlib.sha256(payload.encode()).hexdigest(),
        "algorithm": "sha256"
    }

def f3_aggregate(captured):
    line = captured["raw"].lower()
    patterns = []
    if "python3" in line: patterns.append(("cmd_python", line))
    if "error" in line or "exception" in line: patterns.append(("err_detected", line))
    if "success" in line or "complete" in line: patterns.append(("succ_detected", line))
    if "agape" in line: patterns.append(("agape_key", line))
    if "ledger" in line or "proof" in line: patterns.append(("proof_key", line))
    if "fractal" in line or "swarm" in line: patterns.append(("fractal_sys", line))
    if "observer" in line or "monitor" in line: patterns.append(("obs_sys", line))
    if "chmod" in line or "mkdir" in line or " cd " in line: patterns.append(("fs_op", line))
    if "print" in line: patterns.append(("out_print", line))
    if "infer" in line or "llama" in line: patterns.append(("inference", line))
    return {"type": "aggregate", "patterns": patterns, "count": len(patterns)}

def f4_pair(prev, curr):
    return {
        "type": "pair",
        "left": prev,
        "right": curr,
        "link_hash": hashlib.sha256(f"{prev}|{curr}".encode()).hexdigest()[:16]
    }

def f5_commit(data):
    block_id = hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=True).encode()
    ).hexdigest()[:8]
    return {"type": "commit", "record": data, "block_id": block_id,
            "ts": datetime.now(timezone.utc).isoformat()}

def f6_verify(commit):
    return {"type": "verify", "valid": True,
            "commit_ref": commit["block_id"], "method": "self_consistency"}

def f7_landauer(ops):
    k_B, T = 1.380649e-23, 300
    return {"type": "landauer", "ops": ops,
            "min_joules": k_B * T * ops * 0.693}

def f8_observe(state):
    return {"type": "observe", "state": state, "health": "nominal"}

def f9_store(item):
    key = hashlib.sha256(
        json.dumps(item, sort_keys=True, ensure_ascii=True).encode()
    ).hexdigest()[:12]
    return {"type": "store", "key": key}

def f10_yield(insight):
    priority = min(
        sum(1 for kw in ["agape","theorem","proof","success","inference"]
            if kw in str(insight).lower()), 5)
    return {"type": "yield", "insight": insight, "priority": priority, "ready": True}

def f11_adapt(feedback):
    delta = +0.1 if feedback.get("success") else -0.1
    weight = feedback.get("weight", 0.0) + delta
    return {"type": "adapt", "pattern": feedback.get("pattern"),
            "new_weight": weight}

def f12_sync(data):
    return {
        "type": "sync",
        "packet_hash": hashlib.sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=True).encode()
        ).hexdigest()[:16],
        "peers": ["optiplex", "syncthing"]
    }

ATOMS = [f1_capture, f2_hash, f3_aggregate, f4_pair, f5_commit, f6_verify,
         f7_landauer, f8_observe, f9_store, f10_yield, f11_adapt, f12_sync]

def observe_file(filepath, limit=None):
    """Read a file directly (no subprocess)."""
    prev_pattern = None
    ops = 0
    lines_read = 0
    
    try:
        with open(filepath, "r", errors="ignore") as f:
            for raw_line in f:
                lines_read += 1
                line = raw_line.strip()
                if not line:
                    continue
                
                ops += 1
                cap  = ATOMS[0](line, filepath)
                hsh  = ATOMS[1](cap)
                agg  = ATOMS[2](cap)
                
                if agg["patterns"]:
                    pair = ATOMS[3](prev_pattern, agg["patterns"][0][0])
                    prev_pattern = agg["patterns"][0][0]
                else:
                    pair = {"type": "pair", "left": prev_pattern, "right": None, "link_hash": ""}
                
                commit = ATOMS[4]({"pattern": agg["patterns"][0][0] if agg["patterns"] else "none",
                                   "line": line[:100], "file": filepath})
                verify = ATOMS[5](commit)
                land   = ATOMS[6](ops)
                obs    = ATOMS[7]({"ops": ops, "lines_read": lines_read})
                store  = ATOMS[8]({"pattern": agg["patterns"][0][0] if agg["patterns"] else "none"})
                
                if agg["patterns"]:
                    yield_out = ATOMS[9]({"pattern": agg["patterns"][0][0], "line": line[:50]})
                    adapt = ATOMS[10]({"pattern": agg["patterns"][0][0], "success": True})
                else:
                    yield_out = None
                    adapt = {"type": "adapt", "pattern": None, "new_weight": 0}
                
                sync = ATOMS[11](cap)
                
                # Emit significant findings
                if yield_out and yield_out["priority"] > 0:
                    print(f"\n[YIELD priority={yield_out['priority']}]")
                    print(json.dumps(yield_out, indent=2))
                    print(f"  commit: {commit['block_id']}  landauer: {land['min_joules']:.2e} J")
                
                if ops % 100 == 0:
                    print(f"  ... {ops} lines processed, {lines_read} total", end="\r")
                
                if limit and ops >= limit:
                    break
    except FileNotFoundError:
        print(f"File not found: {filepath}", file=sys.stderr)
        return
    
    print(f"\n\nDone. {ops} lines processed.")

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "/home/jesse/.bash_history"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print(f"Observing: {filepath}")
    observe_file(filepath, limit=limit)
