#!/data/data/com.termux/files/usr/bin/python3
"""MOBILE_TO_OPTIPLEX_UNIFIER v2.0 — canary [unify-v2-ok]"""
import json, hashlib, time, subprocess, pathlib, sys
from datetime import datetime, timezone

MOBILE_BASE = pathlib.Path("/sdcard/openroot")
OPTIPLEX_USER = "jesse"
OPTIPLEX_HOST = "192.168.1.193"
OPTIPLEX_BASE = f"/home/{OPTIPLEX_USER}/openroot"

MOBILE_LEDGERS = [
    MOBILE_BASE / "thermo_ledger/eta_moves.jsonl",
    MOBILE_BASE / "parallel_analysis/ledger/ideas.jsonl",
    MOBILE_BASE / "ledger/experiments/linux_command_persistence.jsonl",
]

OPTIPLEX_TARGETS = {
    "eta_moves.jsonl": "data/oracle_etha_ledger.jsonl",
    "ideas.jsonl": "data/parallel_ideas.jsonl",
    "linux_command_persistence.jsonl": "ledger/experiments/linux_command_persistence.jsonl",
}

def _hash(prev, payload):
    blob = prev + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()

def compute_file_hash(path):
    if not path.exists():
        return "0" * 64
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def last_ledger_hash(ledger_path):
    if not ledger_path.exists() or ledger_path.stat().st_size == 0:
        return "0" * 64
    with open(ledger_path, "rb") as f:
        f.seek(max(0, ledger_path.stat().st_size - 4096))
        lines = f.read().decode(errors="replace").strip().splitlines()
    if not lines:
        return "0" * 64
    try:
        return json.loads(lines[-1]).get("hash", "0" * 64)
    except Exception:
        return "0" * 64

def sync_to_optiplex(local_path, remote_target):
    result = {"local": str(local_path), "remote": remote_target, "status": "skipped", "reason": ""}
    if not local_path.exists():
        result["reason"] = "local file missing"
        return result
    rsync_cmd = [
        "rsync", "-avz",
        str(local_path),
        f"{OPTIPLEX_USER}@{OPTIPLEX_HOST}:{OPTIPLEX_BASE}/{remote_target}"
    ]
    try:
        proc = subprocess.run(rsync_cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode == 0:
            result["status"] = "synced"
            result["local_hash"] = compute_file_hash(local_path)
        else:
            result["status"] = "error"
            result["reason"] = proc.stderr.strip()[:200]
    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)[:200]
    return result

def trigger_refinery_advance(optiplex_conn):
    result = {"status": "skipped", "reason": ""}
    if not optiplex_conn:
        result["reason"] = "optiplex unreachable"
        return result
    cmd = (
        f"ssh -o BatchMode=yes {OPTIPLEX_USER}@{OPTIPLEX_HOST} "
        f"'cd {OPTIPLEX_BASE} && if [ -x bin/refine_next.sh ] || [ -f bin/refine_next.sh ]; "
        f"then bash bin/refine_next.sh 2>&1 | tail -20; else echo REFINERY_NOT_READY; fi'"
    )
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if "REFINERY_NOT_READY" in proc.stdout:
            result["reason"] = "refinery worker not deployed"
        elif proc.returncode == 0:
            result["status"] = "triggered"
            result["output"] = proc.stdout.strip()[:400]
        else:
            result["status"] = "error"
            result["reason"] = proc.stderr.strip()[:200]
    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)[:200]
    return result

def main():
    start = time.time()
    print("=== MOBILE TO OPTIPLEX UNIFIER STARTED ===")
    print(datetime.now(timezone.utc).isoformat())

    print("[1/4] Checking SSH connectivity...")
    ssh_check = subprocess.run(
        f"ssh -o BatchMode=yes -o ConnectTimeout=10 {OPTIPLEX_USER}@{OPTIPLEX_HOST} 'echo OK'",
        shell=True, capture_output=True, text=True, timeout=20
    )
    optiplex_conn = ssh_check.returncode == 0
    print("OptiPlex:", "reachable" if optiplex_conn else "unreachable")

    print("[2/4] Syncing ledgers...")
    sync_results = []
    for mobile_ledger in MOBILE_LEDGERS:
        target = OPTIPLEX_TARGETS.get(mobile_ledger.name, f"data/{mobile_ledger.name}")
        r = sync_to_optiplex(mobile_ledger, target)
        sync_results.append(r)
        print(" ", mobile_ledger.name, "->", r["status"], r.get("reason", "")[:60])

    print("[3/4] Compiling sync metadata into ideas ledger...")
    ideas_ledger = MOBILE_BASE / "parallel_analysis/ledger/ideas.jsonl"
    ideas_ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "source": "sync_autocompile",
        "event": "mobile_to_optiplex_sync",
        "ts": time.time(),
        "optiplex_reachable": optiplex_conn,
        "ledgers_synced": sum(1 for r in sync_results if r["status"] == "synced"),
        "ledgers_attempted": len(MOBILE_LEDGERS),
        "details": sync_results,
    }
    prev = last_ledger_hash(ideas_ledger)
    entry["prev"] = prev
    entry["hash"] = _hash(prev, entry)
    with open(ideas_ledger, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    print("  appended hash=", entry["hash"][:12])

    print("[4/4] Triggering refinery (if connected)...")
    refinery_result = trigger_refinery_advance(optiplex_conn)
    print("  Refinery:", refinery_result["status"], refinery_result.get("reason", "")[:60])

    elapsed = round(time.time() - start, 2)
    print("=== UNIFICATION COMPLETE ===")
    print("Duration:", elapsed, "s")
    print("canary [unify-v2-ok]")
    return {
        "status": "complete",
        "duration_s": elapsed,
        "optiplex_reachable": optiplex_conn,
        "ledgers": sync_results,
        "refinery": refinery_result,
        "ledger_hash": entry["hash"],
    }

if __name__ == "__main__":
    print(json.dumps(main(), separators=(",", ":")))
