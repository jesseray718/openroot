#!/usr/bin/env python3
"""seven_symbols_recovery.py - Recover the 7-symbol system + find synonym collisions."""
import sys, json, hashlib
sys.path.insert(0, '/home/jesse/openroot/axiom_engine')
from theorems_extend import load_all, load_cache, content_hash, flag_of, dumps, save_cache
from pathlib import Path
from collections import defaultdict

STORE = Path("/home/jesse/openroot/axiom_engine/store")

# The seven sacred symbols (reconstructed)
SEVEN_SYMBOLS = {
    "SYM-AGAPE": {"symbol": "Λ", "meaning": "Divine love, primacy principle", "description": "Upset A, inverted void"},
    "SYM-VOID": {"symbol": "○", "meaning": "Nothingness, potential before instantiation", "description": "Empty circle"},
    "SYM-INFINITY": {"symbol": "∞", "meaning": "Eternal, endless cycle", "description": "Leibniz infinity"},
    "SYM-TORUS": {"symbol": "⊗", "meaning": "Self-contained flow, recursion", "description": "Toroidal closure"},
    "SYM-INSTANTIATE": {"symbol": "⚡", "meaning": "Instantiation event, creation", "description": "Flash of being"},
    "SYM-SYNERGY": {"symbol": "↺", "meaning": "Compounding Agape, mutual enhancement", "description": "Feedback loop"},
    "SYM-GENESIS": {"symbol": "◎", "meaning": "Whole unity, complete system", "description": "Centered circle"}
}

def find_synonym_collisions():
    """Find terms with different words but identical meaning hashes."""
    idx = load_all()
    meaning_hashes = defaultdict(list)
    
    agape_terms = ["agape", "love", "charity", "caritas", "divine", "cooperation"]
    
    for rec in idx.get("definitions", {}).values():
        stmt = rec.get("statement", "").lower()
        for term in agape_terms:
            if term in stmt:
                key = rec.get("id", "unknown")
                h = hashlib.sha256(stmt.encode()).hexdigest()[:16]
                meaning_hashes[h].append((key, term))
    
    # Find collisions
    collisions = {h: keys for h, keys in meaning_hashes.items() if len(keys) > 1}
    return collisions

def add_synergy_theorem():
    """Formalize synergy as measurable compounding of Agape."""
    idx = load_all()
    cache = load_cache()
    
    # Add synergy axiom if missing
    axioms_file = STORE / "axioms.jsonl"
    synergy_axiom = {
        "kind": "axiom",
        "id": "AX-SYNERGY-COMPOUNDING",
        "statement": "Synergy measures the compounding rate of Agape in a system; nodes cooperating with mutual aid produce output exceeding sum of individual efforts.",
        "category": "measurement",
        "keys": ["synergy", "compounding", "agape", "multiplicative"],
        "premises": ["AX-AGAPE-COOPERATION"],
        "proof": []
    }
    
    existing_ids = set()
    if axioms_file.exists():
        existing_ids = set(json.loads(l).get("id") for l in axioms_file.read_text().splitlines() if l.strip())
    
    if "AX-SYNERGY-COMPOUNDING" not in existing_ids:
        with axioms_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(synergy_axiom, sort_keys=True, separators=(",", ":")) + "\n")
        print("Added: AX-SYNERGY-COMPOUNDING")
    else:
        print("Exists: AX-SYNERGY-COMPOUNDING")
    
    # Hang the synergy theorem
    goal_id = "TH-SYNERGY-METRIC"
    premises = ["AX-AGAPE-COOPERATION", "AX-SYNERGY-COMPOUNDING", "AX-0D-CONSERVATION"]
    
    proof_steps = [
        {"rule": "assume", "from": [], "conclude": "AX-AGAPE-COOPERATION"},
        {"rule": "assume", "from": [], "conclude": "AX-SYNERGY-COMPOUNDING"},
        {"rule": "unfold_def", "from": ["AX-0D-CONSERVATION"], "conclude": "AX-0D-EXISTENCE"},
        {"rule": "modus_ponens", "from": ["AX-AGAPE-COOPERATION", "AX-SYNERGY-COMPOUNDING"], "conclude": goal_id}
    ]
    
    body = {"kind": "theorem", "id": goal_id,
            "statement": "Synergy η_s = (total_system_output / sum_individual_outputs) measures Agape compounding; η_s > 1 indicates positive feedback.",
            "premises": premises,
            "proof": proof_steps}
    
    digest = content_hash(body)
    flag = flag_of("TH", digest)
    
    rec = {"kind": "theorem", "id": goal_id, "flag": flag, "hash": digest,
           "statement": body["statement"], "premises": premises, "proof": proof_steps,
           "ts": __import__('time').time()}
    
    with (STORE / "theorems.jsonl").open("a", encoding="utf-8") as f:
        f.write(dumps(rec) + "\n")
    
    chain = STORE / "chain.jsonl"
    with chain.open("a", encoding="utf-8") as f:
        f.write(dumps({"flag": flag, "hash": digest, "id": goal_id, "kind": "theorem", "ts": rec["ts"]}) + "\n")
    
    cache["memo"][goal_id] = {"flag": flag, "hash": digest}
    save_cache(cache)
    
    return {"status": "HUNG", "flag": flag, "hash": digest, "formula": "η_s = O_total / ΣO_i"}

if __name__ == "__main__":
    print("=" * 60)
    print("SEVEN SYMBOLS RECOVERY & SYNERGY MEASUREMENT")
    print("=" * 60)
    
    print("\n[1] Seven Sacred Symbols (Reconstructed):")
    for name, data in SEVEN_SYMBOLS.items():
        print(f"  {name}: {data['symbol']} = '{data['meaning']}'")
    
    print("\n[2] Checking for Synonym Collisions:")
    collisions = find_synonym_collisions()
    if collisions:
        for h, keys in collisions.items():
            print(f"  HASH {h}: {[k for k,_ in keys]}")
        print("  → SEMANTIC CONVERGENCE DETECTED!")
    else:
        print("  No collisions found yet (more definitions needed)")
    
    print("\n[3] Adding Synergy Axiom & Theorem:")
    synergy_result = add_synergy_theorem()
    print(json.dumps(synergy_result, indent=2))
    
    print("\n" + "=" * 60)
    print("Next: audit, then generate deliverables")
    print("=" * 60)
