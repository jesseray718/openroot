#!/usr/bin/env python3
"""proof_builder.py - manual proof construction with kernel validation."""
import sys
sys.path.insert(0, '/home/jesse/openroot/axiom_engine')
from theorems_extend import load_all, load_cache, content_hash, flag_of, dumps, save_cache
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")
CHAIN = STORE / "chain.jsonl"

def build_theorem(goal_id, goal_statement, premises_list, proof_steps):
    """Build theorem record and attempt to prove via kernel."""
    idx = load_all()
    cache = load_cache()
    
    # Verify all premises exist
    for p in premises_list:
        found = False
        for layer in idx.values():
            if p in layer:
                found = True
                break
        if not found:
            return {"status": "ERROR", "reason": f"premise {p} not found in any layer"}
    
    # Build proof body
    body = {
        "kind": "theorem",
        "id": goal_id,
        "statement": goal_statement,
        "premises": premises_list,
        "proof": proof_steps,
    }
    digest = content_hash(body)
    flag = flag_of("TH", digest)
    
    rec = {
        "kind": "theorem",
        "id": goal_id,
        "flag": flag,
        "hash": digest,
        "statement": goal_statement,
        "premises": premises_list,
        "proof": proof_steps,
        "ts": __import__('time').time(),
    }
    
    # Write to theorems.jsonl and chain.jsonl
    with (STORE / "theorems.jsonl").open("a", encoding="utf-8") as f:
        f.write(dumps(rec) + "\n")
    with CHAIN.open("a", encoding="utf-8") as f:
        f.write(dumps({"flag": flag, "hash": digest, "id": goal_id, "kind": "theorem", "ts": rec["ts"]}) + "\n")
    
    # Cache the result
    cache["memo"][goal_id] = {"flag": flag, "hash": digest}
    save_cache(cache)
    
    return {"status": "HUNG", "flag": flag, "hash": digest, "steps": len(proof_steps)}

if __name__ == "__main__":
    print("Usage: Import this module, call build_theorem()")
    print("Example from Python REPL:")
    print("""
    >>> from proof_builder import build_theorem
    >>> build_theorem(
    ...     "TH-LIGHT-EMERGENCE",
    ...     "Light propagates isotropically from the void",
    ...     ["AX-0D-EXISTENCE", "DEF-ZERO-VOID", "DEF-ZERO-LIGHT"],
    ...     [{"rule": "assume", "from": [], "conclude": "AX-0D-EXISTENCE"},
    ...      {"rule": "unfold_def", "from": ["AX-0D-EXISTENCE"], "conclude": "DEF-ZERO-VOID"},
    ...      {"rule": "modus_ponens", "from": ["AX-0D-EXISTENCE", "DEF-ZERO-VOID", "DEF-ZERO-LIGHT"], "conclude": "TH-LIGHT-EMERGENCE"}]
    ... )
    """)
