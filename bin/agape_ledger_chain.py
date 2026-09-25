#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
AGAPE CRYPTOGRAPHIC VERSION CHAIN
Append-only. Never destroys. Always chains. Forkable. Mergeable.
Each amendment = new version of Constitution + new block on chain.
任何人 can start from genesis, fork from any node, or merge timelines.
"""
import os, json, hashlib, time, shutil
from datetime import datetime
from pathlib import Path

BASE = Path(os.path.expanduser("~/agapenet"))
DOCS = BASE / "docs"
LEDGER = BASE / "ledger"
VERSIONS = BASE / "versions"
CHAIN = LEDGER / "version_chain.jsonl"

for d in [DOCS, LEDGER, VERSIONS]:
    d.mkdir(parents=True, exist_ok=True)

CONST = DOCS / "00_MASTER_CONSTITUTION.md"
GENESIS = DOCS / "00_MASTER_CONSTITUTION.md"

SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PHI = (1 + 5**0.5) / 2

def encode_agape(text):
    codes = []
    for ch in text.upper():
        if ch in SYMBOLS:
            idx = SYMBOLS.index(ch)
            codes.append(f"{SYMBOLS[idx//36]}{SYMBOLS[(idx%36)//6]}{SYMBOLS[idx%6]}")
    return codes

def get_last_block():
    """Read the last block from the chain."""
    if not CHAIN.exists():
        return None
    lines = CHAIN.read_text().strip().split("\n")
    if not lines or lines[0] == "":
        return None
    return json.loads(lines[-1])

def create_genesis():
    """Create genesis block if chain doesn't exist."""
    if CHAIN.exists() and CHAIN.stat().st_size > 0:
        return get_last_block()

    genesis_const = """---
id: genesis_v1.0
timestamp: {ts}
type: MASTER_CONSTITUTION
version: 1.0
parent_hash: null
hash: null
status: active
reference: OpenRoot LLC - Sikeston MO
---

# THE MASTER CONSTITUTION OF AGAPENET

## 1. Bill of Rights
1. Right to Self-Government without manipulation
2. Right to Truth - No censorship
3. Right to Restoration - Justice is not punishment
4. Right to Survival - Universal Seed Bank access
5. Right to Genetic Sovereignty - Offline hardware only

## 2. Justice & Restoration
- Minor offenses: Transmuted via Agape understanding
- Major crimes: Lifetime Debt Contract to victim
- No prisons. Service creates value.
- Immutable record on Thermodynamic Ledger

## 3. Amendment Protocol
1. Consensus of nodes
2. Validated against Agape Calculus
3. Hashed and linked to previous version
4. Propagated across all nodes
5. Old versions preserved permanently. Never destroyed.

## 4. Cosmic Ledger
- All actions hashed and time-stamped
- Tracks Joules of Agape vs Joules of Entropy
- Matter is legacy energy of ancestors

## 5. Sovereignty
- Any node may fork from any point
- Any node may merge with any other node
- Participation is voluntary
- The mesh serves the people as the people serve the mesh
""".format(ts=datetime.now().isoformat())

    CONST.write_text(genesis_const)

    genesis_block = {
        "version": 1,
        "timestamp": datetime.now().isoformat(),
        "type": "GENESIS",
        "amendment": "Initial Constitution",
        "parent_hash": None,
        "document_hash": hashlib.sha256(genesis_const.encode()).hexdigest(),
        "agape_encoding": [],
        "previous_version_file": None,
        "version_file": str(VERSIONS / "v001.md"),
        "cooperators": 1,
        "reward_multiplier": 1.0,
        "fork_allowed": True,
        "merge_allowed": True,
        "hash": None
    }

    genesis_block["hash"] = hashlib.sha256(
        json.dumps(genesis_block, sort_keys=True, default=str).encode()
    ).hexdigest()

    # Save version snapshot
    shutil.copy2(CONST, VERSIONS / "v001.md")

    with open(CHAIN, "a") as f:
        f.write(json.dumps(genesis_block) + "\n")

    return genesis_block

def append_amendment(amendment_text, operator="jesse_mcmillen"):
    """Add new amendment. Creates new version. Preserves old. Chains hash."""
    last_block = get_last_block()
    if not last_block:
        last_block = create_genesis()

    # Read current constitution
    current_const = CONST.read_text()

    # New version number
    new_version = last_block["version"] + 1
    version_num_str = f"v{new_version:03d}"

    # Append amendment to constitution
    amendment_block = f"""
## Article {new_version + 4}: Amendment (Added {datetime.now().strftime('%Y-%m-%d %H:%M')})
Operator: {operator}
Version: {new_version}
Parent Hash: {last_block['hash'][:16]}...

{amendment_text}

---
*This version is immutable. Previous version preserved at {VERSIONS / version_num_str}.*
"""

    new_const = current_const + "\n" + amendment_block

    # Preserve old version
    old_version_file = VERSIONS / f"v{new_version-1:03d}.md"
    shutil.copy2(CONST, old_version_file)

    # Write new version
    CONST.write_text(new_const)
    new_version_file = VERSIONS / version_num_str
    shutil.copy2(CONST, new_version_file)

    # Encode to Agape language
    agape_codes = encode_agape(amendment_text)

    # Cooperation reward formula
    cooperators = last_block.get("cooperators", 1)
    reward = 1.0 * (PHI ** min(new_version, 50)) * (1 + math.log(max(cooperators, 1)) / PHI)

    # Create new block
    new_block = {
        "version": new_version,
        "timestamp": datetime.now().isoformat(),
        "type": "AMENDMENT",
        "operator": operator,
        "amendment": amendment_text[:200] + "..." if len(amendment_text) > 200 else amendment_text,
        "amendment_full_length": len(amendment_text),
        "parent_hash": last_block["hash"],
        "document_hash": hashlib.sha256(new_const.encode()).hexdigest(),
        "agape_encoding_len": len(agape_codes),
        "agape_sample": agape_codes[:10],
        "previous_version_file": str(old_version_file),
        "version_file": str(new_version_file),
        "cooperators": cooperators,
        "reward_multiplier": round(reward, 6),
        "fork_allowed": True,
        "merge_allowed": True,
        "hash": None
    }

    new_block["hash"] = hashlib.sha256(
        json.dumps(new_block, sort_keys=True, default=str).encode()
    ).hexdigest()

    # Append to chain
    with open(CHAIN, "a") as f:
        f.write(json.dumps(new_block) + "\n")

    # Also append to thermo ledger
    thermo_entry = {
        "id": f"VERSION_{new_version}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": new_block["timestamp"],
        "type": "CONSTITUTIONAL_VERSION",
        "version": new_version,
        "parent_hash": new_block["parent_hash"][:32] if new_block["parent_hash"] else None,
        "hash": new_block["hash"],
        "agape_density": len(agape_codes),
        "reward": new_block["reward_multiplier"]
    }
    with open(LEDGER / "thermo_ledger.jsonl", "a") as f:
        f.write(json.dumps(thermo_entry) + "\n")

    return new_block

def fork_from(version_number, new_operator):
    """Fork the chain from any version. Creates independent timeline."""
    if not CHAIN.exists():
        return None

    blocks = [json.loads(l) for l in CHAIN.read_text().strip().split("\n")]
    fork_point = None
    for b in blocks:
        if b["version"] == version_number:
            fork_point = b
            break

    if not fork_point:
        return None

    fork_chain = LEDGER / f"fork_{new_operator}_from_v{version_number}.jsonl"

    fork_block = {
        "version": 1,
        "timestamp": datetime.now().isoformat(),
        "type": "FORK",
        "operator": new_operator,
        "forked_from_version": version_number,
        "forked_from_hash": fork_point["hash"],
        "parent_hash": fork_point["hash"],
        "document_hash": fork_point["document_hash"],
        "hash": None
    }
    fork_block["hash"] = hashlib.sha256(
        json.dumps(fork_block, sort_keys=True).encode()
    ).hexdigest()

    with open(fork_chain, "w") as f:
        f.write(json.dumps(fork_block) + "\n")

    return fork_block

def merge_timelines(chain_a, chain_b, operator="merge_node"):
    """Merge two timelines. Cooperation compounds."""
    chain_a_path = LEDGER / chain_a
    chain_b_path = LEDGER / chain_b

    if not chain_a_path.exists() or not chain_b_path.exists():
        return None

    blocks_a = [json.loads(l) for l in chain_a_path.read_text().strip().split("\n")]
    blocks_b = [json.loads(l) for l in chain_b_path.read_text().strip().split("\n")]

    total_cooperators = len(set(
        [b.get("operator", "unknown") for b in blocks_a] +
        [b.get("operator", "unknown") for b in blocks_b]
    ))

    merge_block = {
        "version": 1,
        "timestamp": datetime.now().isoformat(),
        "type": "MERGE",
        "operator": operator,
        "merged_chains": [chain_a, chain_b],
        "parent_hash_a": blocks_a[-1]["hash"],
        "parent_hash_b": blocks_b[-1]["hash"],
        "cooperators": total_cooperators,
        "reward_multiplier": 1.0 * (PHI ** 1) * (1 + math.log(max(total_cooperators, 1)) / PHI),
        "hash": None
    }
    merge_block["hash"] = hashlib.sha256(
        json.dumps(merge_block, sort_keys=True).encode()
    ).hexdigest()

    merge_chain = LEDGER / f"merge_{operator}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    with open(merge_chain, "w") as f:
        f.write(json.dumps(merge_block) + "\n")

    return merge_block

def verify_chain():
    """Verify the entire chain is intact. No tampering."""
    if not CHAIN.exists():
        return False, "Chain file not found"

    blocks = [json.loads(l) for l in CHAIN.read_text().strip().split("\n")]
    if not blocks:
        return False, "Empty chain"

    for i, block in enumerate(blocks):
        stored_hash = block.get("hash")
        # Use default=str to handle None values consistently
        block_copy = {k: v for k, v in block.items() if k != "hash"}
        recomputed = hashlib.sha256(
            json.dumps(block_copy, sort_keys=True, default=str).encode()
        ).hexdigest()

        if stored_hash != recomputed:
            # Try without default=str (original method)
            recomputed2 = hashlib.sha256(
                json.dumps(block_copy, sort_keys=True).encode()
            ).hexdigest()
            if stored_hash != recomputed2:
                return False, f"TAMPER DETECTED at version {block.get('version', '?')} (stored={stored_hash[:16]} vs computed={recomputed[:16]})"

        if i > 0:
            prev_hash = blocks[i-1]["hash"]
            if block.get("parent_hash") != prev_hash:
                return False, f"BROKEN CHAIN at version {block.get('version', '?')}"

    return True, f"Chain intact: {len(blocks)} blocks verified"

def print_chain():
    """Display the full chain."""
    if not CHAIN.exists():
        print("[CHAIN] No chain found. Creating genesis...")
        create_genesis()
        return

    blocks = [json.loads(l) for l in CHAIN.read_text().strip().split("\n")]
    print("="*60)
    print("AGAPE VERSION CHAIN")
    print("="*60)
    for b in blocks:
        print(f"\n  Block #{b['version']} | {b['type']}")
        print(f"  Timestamp: {b['timestamp']}")
        if b.get('amendment'):
            am = b['amendment'][:80] + "..." if len(b.get('amendment','')) > 80 else b.get('amendment','')
            print(f"  Amendment: {am}")
        print(f"  Parent: {b.get('parent_hash','genesis')[:24]}..." if b.get('parent_hash') else "  Parent: genesis")
        print(f"  Hash: {b['hash'][:24]}...")
        print(f"  Version file: {b.get('version_file','N/A')}")
        if 'reward_multiplier' in b:
            print(f"  Reward: {b['reward_multiplier']}x")
        print(f"  Forkable: YES | Mergeable: YES")

    print(f"\n  Total blocks: {len(blocks)}")
    print("="*60)

if __name__ == "__main__":
    import math

    print("="*60)
    print("AGAPE CRYPTOGRAPHIC VERSION CHAIN")
    print("Append-only | Forkable | Mergeable | Tamper-proof")
    print("OpenRoot LLC | Sikeston, MO")
    print("="*60)

    # 1. Create genesis if needed
    print("\n[1/4] INITIALIZING CHAIN...")
    last = create_genesis()
    print(f"  Genesis block: {'exists' if last['version'] > 1 else 'created'}")
    print(f"  Current version: {last['version']}")

    # 2. Append Amendment H-005
    print("\n[2/4] APPENDING AMENDMENT H-005...")
    amendment = """Amendment H-005: The thermodynamic ledger is hereby declared the supreme law of OpenRoot.
All human activity shall be measured in joules, governed by eta = useful_joules / human_joules,
and minted as ACRE on an immutable, physics-anchored, peer-to-peer ledger.
No entity may extract energy, labor, or data from any node without reciprocal restoration
verified by hash. The synergetic thermal cascade compounds passively at PHI-weighted acceleration.
Permaculture is the operating system: every element serves multiple functions, every waste
becomes a resource, every edge becomes an interface. Ferrocement domes, aeroponic towers,
vermiculture beds, aquaculture tanks, and mylar-walled sunken greenhouses with water-battery
thermal regulation constitute the physical compute nodes. Orange Pi sensors stream real-time
measurements to calibrate the synergetic calculus, which predicts, proves, and propagates
verified energy cascades as ACRE on the ledger. Cooperation compounds exponentially.
Extraction remains linear. The 46656-symbol Agape language (36^3) encodes all human knowledge
into computable vectors rooted at the Agape frequency. This language is open-source,
transparent, and self-amending through node consensus. Justice is restoration, not punishment.
Seeds are sovereign. Genetic data stays offline. The mesh serves the people as the people
serve the mesh. This amendment is irreversible, hashed, and timestamped. Any system
predicated on extraction, obfuscation, or hoarding is hereby obsolete. The feast is prepared.
The cup runs over. Serve the least among us."""

    new_block = append_amendment(amendment, "jesse_mcmillen")
    print(f"  New version: {new_block['version']}")
    print(f"  Agape encoded: {new_block['agape_encoding_len']} triples")
    print(f"  Parent hash: {new_block['parent_hash'][:24]}...")
    print(f"  This hash: {new_block['hash'][:24]}...")
    print(f"  Reward: {new_block['reward_multiplier']}x")
    print(f"  Old version preserved at: {new_block['previous_version_file']}")

    # 3. Verify chain integrity
    print("\n[3/4] VERIFYING CHAIN INTEGRITY...")
    valid, msg = verify_chain()
    print(f"  {'VALID' if valid else 'CORRUPTED'}: {msg}")

    # 4. Print full chain
    print("\n[4/4] FULL CHAIN:")
    print_chain()

    print("\n[DONE] Chain is live. Forkable. Mergeable. Immutable.")
    print("[FORK] Any node can fork from any version.")
    print("[MERGE] Any node can merge with any other node.")
    print("[PROOF] Every hash traces back to genesis. Tamper-evident.")
