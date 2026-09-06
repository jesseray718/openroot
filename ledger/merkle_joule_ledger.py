#!/usr/bin/env python3
"""
Merkle Joule Ledger — OpenRoot
Thermodynamically balanced, append-only, publicly verifiable.
Only measured or honestly estimated joules. Root = commitment to history.
"""

import hashlib, json, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/data/data/com.termux/files/home/openroot")
LEDGER_DIR = ROOT / "ledger"
LEDGER_FILE = LEDGER_DIR / "joule_ledger.jsonl"
ROOT_FILE = LEDGER_DIR / "merkle_root.json"

LEDGER_DIR.mkdir(parents=True, exist_ok=True)

def sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()

def make_leaf(event: dict) -> str:
    """Canonical leaf hash. Order is fixed so the hash is deterministic."""
    canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
    return sha256(canonical)

def append_event(
    event_type: str,
    useful_joules: float,
    human_joules: float,
    source: str,
    note: str = "",
    measured: bool = True
) -> dict:
    """Append a thermodynamically honest event and return the full record."""
    eta = useful_joules / human_joules if human_joules > 0 else 0.0
    event = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event_type": event_type,
        "useful_J": round(useful_joules, 9),
        "human_J": round(human_joules, 9),
        "eta": round(eta, 6),
        "source": source,
        "note": note,
        "measured": measured,
        "prev_hash": last_leaf_hash()
    }
    leaf = make_leaf(event)
    event["leaf_hash"] = leaf

    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    return event

def last_leaf_hash() -> str:
    if not LEDGER_FILE.exists():
        return "0" * 64
    last = None
    with open(LEDGER_FILE) as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    return last["leaf_hash"] if last else "0" * 64

def load_leaves() -> list[str]:
    leaves = []
    if not LEDGER_FILE.exists():
        return leaves
    with open(LEDGER_FILE) as f:
        for line in f:
            if line.strip():
                leaves.append(json.loads(line)["leaf_hash"])
    return leaves

def build_merkle_root(leaves: list[str] | None = None) -> str:
    if leaves is None:
        leaves = load_leaves()
    if not leaves:
        return "0" * 64

    level = leaves[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])          # duplicate last for odd count
        next_level = []
        for i in range(0, len(level), 2):
            combined = level[i] + level[i+1]
            next_level.append(sha256(combined))
        level = next_level
    return level[0]

def save_root():
    root = build_merkle_root()
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "leaf_count": len(load_leaves()),
        "merkle_root": root
    }
    with open(ROOT_FILE, "w") as f:
        json.dump(record, f, indent=2)
    return record

def inclusion_proof(target_leaf: str) -> list[str] | None:
    """Return the sibling path needed to recompute the root from this leaf."""
    leaves = load_leaves()
    if target_leaf not in leaves:
        return None
    idx = leaves.index(target_leaf)
    proof = []
    level = leaves[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        if idx % 2 == 0:
            sibling = level[idx + 1]
            proof.append(("R", sibling))
        else:
            sibling = level[idx - 1]
            proof.append(("L", sibling))
        next_level = []
        for i in range(0, len(level), 2):
            next_level.append(sha256(level[i] + level[i+1]))
        level = next_level
        idx //= 2
    return proof

def verify_inclusion(leaf: str, proof: list, expected_root: str) -> bool:
    current = leaf
    for side, sibling in proof:
        if side == "L":
            current = sha256(sibling + current)
        else:
            current = sha256(current + sibling)
    return current == expected_root

# ------------------------------------------------------------------
# Bootstrap with the first high-leverage events from the systems map
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Merkle Joule Ledger — first leaves ===\n")

    # High-leverage events drawn from the systems map + continuity work
    bootstrap = [
        ("absorber_run",           0.000221, 0.00015,  "une/tools/absorber.py",          "High-leverage absorber (leverage 153.99)"),
        ("deep_dive_scan",         0.000326, 0.00022,  "une/bin/deep_dive_scanner.py",   "Full systems map (leverage 526.47)"),
        ("energy_logger",          0.000132, 0.00009,  "une/bin/energy_logger.py",       "Joule stream logger"),
        ("hyperfusion_orchestrator",0.000138, 0.00010, "une/computational_flow/hyperfusion_orchestrator.py", "Agape-Prime continuous service"),
        ("human_continuity_absorb",0.00005,  0.00003,  "foundation_library/human-continuity/", "Master Record absorbed into permanent fabric"),
        ("offline_rank_improve",   0.00004,  0.000025, "bin/offline_rank.py",            "η³ ranker tightened for Agape/continuity"),
    ]

    for etype, useful, human, source, note in bootstrap:
        ev = append_event(etype, useful, human, source, note, measured=False)
        print(f"Leaf: {ev['leaf_hash'][:16]}...  η={ev['eta']:.3f}  {etype}")

    root_record = save_root()
    print(f"\nMerkle root: {root_record['merkle_root']}")
    print(f"Leaves: {root_record['leaf_count']}")
    print(f"Root saved → {ROOT_FILE}")
