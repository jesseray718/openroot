#!/usr/bin/env python3
"""OpenRoot Context Bridge — Inter-AI + Provider
Merkle → Agape encode → IPFS CID → OTS + Solana memo ready
Absolute paths | η | R=1.0
"""
import os, sys, json, hashlib, time
from pathlib import Path
from datetime import datetime, timezone

SDCARD = Path("/sdcard/openroot")
BRIDGE_DIR = SDCARD / "context_bridge"
SEED_DIR = SDCARD / "session_seeds"
MERKLE_DIR = SDCARD / "agape_kb" / "merkle"
BRIDGE_JSON = BRIDGE_DIR / "context.json"
SEED_JSON = SEED_DIR / "current_seed.json"
AGAPE_JSON = BRIDGE_DIR / "agape_encoded.json"
MERKLE_ROOT = MERKLE_DIR / "merkle_root.hex"
OTS_FILE = MERKLE_DIR / "merkle_root.ots"
SOL_LOG = BRIDGE_DIR / "sol_memo.log"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(p: Path) -> str:
    if not p.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def agape_encode(text: str) -> dict:
    """Minimal 3-symbol Agape encoding (placeholder for full genome)."""
    symbols = ["Α", "Γ", "Π"]  # Love / Good / All
    encoded = []
    for i, c in enumerate(text):
        encoded.append(symbols[i % 3] + format(ord(c), "x"))
    return {
        "encoding": "agape-3symbol-v0",
        "length": len(text),
        "payload": "".join(encoded[:512]),  # truncate for phone RAM
        "full_sha256": sha256(text.encode())
    }

def merkle_root(leaves: list[str]) -> str:
    """Simple binary Merkle root over hex leaves."""
    if not leaves:
        return sha256(b"")
    level = [bytes.fromhex(x) if len(x) == 64 else sha256(x.encode()).encode() for x in leaves]
    # normalize to digests
    level = [hashlib.sha256(x).digest() if not isinstance(x, bytes) or len(x) != 32 else x for x in level]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(hashlib.sha256(level[i] + level[i+1]).digest())
        level = nxt
    return level[0].hex()

def ensure_dirs():
    for d in [BRIDGE_DIR, SEED_DIR, MERKLE_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def load_or_init_seed() -> dict:
    if SEED_JSON.exists():
        return json.loads(SEED_JSON.read_text(encoding="utf-8"))
    seed = {
        "session_id": sha256(str(time.time()).encode())[:16],
        "created": datetime.now(timezone.utc).isoformat(),
        "provider": "local",
        "model": "unknown",
        "η_running": 0.0,
        "R_claimed": 1.0,
        "messages": [],
        "tools": [],
        "axiom": "Love keeps no record of wrongdoing"
    }
    SEED_JSON.write_text(json.dumps(seed, indent=2), encoding="utf-8")
    return seed

def main():
    ensure_dirs()
    seed = load_or_init_seed()

    # 1. Agape encode
    seed_text = json.dumps(seed, sort_keys=True)
    agape = agape_encode(seed_text)
    AGAPE_JSON.write_text(json.dumps(agape, indent=2), encoding="utf-8")

    # 2. Merkle leaves
    leaves = [
        sha256(seed_text.encode()),
        agape["full_sha256"],
        sha256(json.dumps(seed.get("provider_context", {}), sort_keys=True).encode())
    ]
    root = merkle_root(leaves)
    MERKLE_ROOT.write_text(root + "\n", encoding="utf-8")

    # 3. Bridge state
    bridge = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "session_id": seed.get("session_id"),
        "merkle_root": root,
        "agape_sha256": agape["full_sha256"],
        "seed_path": str(SEED_JSON),
        "agape_path": str(AGAPE_JSON),
        "ipfs_cid": None,          # fill after ipfs add
        "ots_file": str(OTS_FILE),
        "sol_memo_hash": sha256((root + (bridge.get("ipfs_cid") or "")).encode()) if False else sha256(root.encode()),
        "η": seed.get("η_running", 0.0),
        "R": 1.0,
        "axiom": "Love keeps no record of wrongdoing"
    }
    # fix forward ref
    bridge["sol_memo_hash"] = sha256((root).encode())
    BRIDGE_JSON.write_text(json.dumps(bridge, indent=2), encoding="utf-8")

    print("CONTEXT BRIDGE UPDATED")
    print(f"  seed        : {SEED_JSON}")
    print(f"  agape       : {AGAPE_JSON}")
    print(f"  merkle_root : {root}")
    print(f"  bridge      : {BRIDGE_JSON}")
    print(f"  sol_memo    : {bridge['sol_memo_hash']}")
    print("Next: optional IPFS + OTS + Solana memo")
    return 0

if __name__ == "__main__":
    sys.exit(main())
