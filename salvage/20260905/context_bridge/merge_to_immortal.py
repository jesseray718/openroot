#!/usr/bin/env python3
"""Merge working context + eta_ledger into immortal_context.json and lock new Merkle."""
import json, hashlib, datetime, os

BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
IMMORTAL = os.path.join(BRIDGE_DIR, "immortal_context.json")
WORKING  = os.path.join(BRIDGE_DIR, "context.json")
LEDGER   = os.path.join(os.path.dirname(BRIDGE_DIR), "seed-core", "ledger", "eta_ledger.jsonl")

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# Load files
with open(IMMORTAL) as f:
    immortal = json.load(f)

working = {}
if os.path.exists(WORKING):
    with open(WORKING) as f:
        working = json.load(f)

# Read eta_ledger entries
ledger_entries = []
if os.path.exists(LEDGER):
    with open(LEDGER) as f:
        for line in f:
            line = line.strip()
            if line:
                ledger_entries.append(json.loads(line))

# Update living_context from working bridge
living = immortal.setdefault("living_context", {})
sys_state = living.setdefault("system_state", {})

# Pull newest status and pending tasks
if working.get("system_state"):
    sys_state["status"] = working["system_state"].get("status", sys_state.get("status", "thermal_swarm_ledger_active"))
    sys_state["last_session"] = working["system_state"].get("last_session", now[:10])
    if working["system_state"].get("pending_tasks"):
        sys_state["pending_tasks"] = working["system_state"]["pending_tasks"]

# Record the ACRE-0001 verification if present
acre_entry = None
for e in ledger_entries:
    if "ACRE-0001" in str(e.get("action_or_claim", "")):
        acre_entry = e
        break

if acre_entry:
    living.setdefault("claims", {})["ACRE-0001"] = {
        "verified_at": acre_entry.get("timestamp"),
        "lattice_order": "12^12",
        "claim_packet_hash": acre_entry.get("claim_packet_hash"),
        "verification_merkle": acre_entry.get("verification_merkle"),
        "level": acre_entry.get("level")
    }

# Append a short absorption record
history = living.setdefault("conversation_history", [])
history.append({
    "ts": now,
    "type": "merge_to_immortal",
    "source": "merge_to_immortal.py",
    "note": "Folded working context.json + eta_ledger into immortal. ACRE-0001 at 12^12 carried forward."
})

# Update top-level fields
immortal["status"] = sys_state.get("status", "thermal_swarm_ledger_active")
immortal["last_absorb"] = now
immortal["chunk_count"] = immortal.get("chunk_count", 0) + 1

# Compute new Merkle over key state
merkle_payload = {
    "status": immortal["status"],
    "last_absorb": immortal["last_absorb"],
    "chunk_count": immortal["chunk_count"],
    "pending_tasks": sys_state.get("pending_tasks", []),
    "acre_0001": living.get("claims", {}).get("ACRE-0001"),
    "ledger_count": len(ledger_entries)
}
merkle_bytes = json.dumps(merkle_payload, sort_keys=True, separators=(",", ":")).encode()
new_root = hashlib.sha256(merkle_bytes).hexdigest()

immortal["merkle"] = {
    "root": new_root,
    "locked_at": now,
    "note": "Merged working bridge + eta_ledger (ACRE-0001 12^12) on 2026-08-01"
}

# Write back
with open(IMMORTAL, "w") as f:
    json.dump(immortal, f, indent=2)

print("=== MERGE COMPLETE ===")
print("New Merkle root:", new_root)
print("chunk_count:", immortal["chunk_count"])
print("status:", immortal["status"])
print("ACRE-0001 carried:", bool(acre_entry))
print("Written:", IMMORTAL)
