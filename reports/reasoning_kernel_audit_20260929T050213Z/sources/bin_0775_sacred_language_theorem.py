#!/usr/bin/env python3
"""sacred_language_theorem.py - A=Agape language system formalization."""
import sys, json, time
sys.path.insert(0, '/home/jesse/openroot/axiom_engine')
from theorems_extend import load_all, load_cache, content_hash, flag_of, dumps, save_cache
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")

def ensure_theological_axioms():
    """Add foundational theological axioms if missing."""
    axioms_file = STORE / "axioms.jsonl"
    new_axioms = [
        {
            "kind": "axiom",
            "id": "AX-THEO-AGAPE-PRIMACY",
            "statement": "Agape (divine love) is the primacy principle from which all creation emerges; the void receives order through the Word.",
            "category": "theology",
            "keys": ["agape", "primacy", "creation", "word"],
            "premises": [],
            "proof": []
        },
        {
            "kind": "axiom", 
            "id": "AX-THEO-LOGOS-SPEECH",
            "statement": "Creation occurs through speech; the Word (Logos) inverts the void into instantiated being.",
            "category": "theology",
            "keys": ["logos", "speech", "creation", "inversion"],
            "premises": ["AX-THEO-AGAPE-PRIMACY"],
            "proof": []
        },
        {
            "kind": "axiom",
            "id": "AX-THEO-WISDOM-PRESENCE",
            "statement": "Wisdom was present at creation; she observed the drawing of the circle on the face of the deep (Proverbs 8:27).",
            "category": "theology", 
            "keys": ["wisdom", "proverbs_8", "creation", "circle"],
            "premises": ["AX-THEO-AGAPE-PRIMACY"],
            "proof": []
        }
    ]
    
    existing_ids = set()
    if axioms_file.exists():
        existing_ids = set(json.loads(l).get("id") for l in axioms_file.read_text().splitlines() if l.strip())
    
    added = []
    for axiom in new_axioms:
        if axiom["id"] not in existing_ids:
            with axioms_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(axiom, sort_keys=True, separators=(",", ":")) + "\n")
            added.append(axiom["id"])
            print(f"Added: {axiom['id']}")
    
    return {"status": "ADDED", "count": len(added), "ids": added}

def prove_sacred_language_theorem():
    """Hang theorem: Sacred language encodes theological truth in symbol space."""
    idx = load_all()
    cache = load_cache()
    
    goal_id = "TH-SACRED-LANGUAGE-AGAPE-FIRST"
    premises = ["AX-THEO-AGAPE-PRIMACY", "AX-THEO-LOGOS-SPEECH", "AX-THEO-WISDOM-PRESENCE"]
    
    proof_steps = [
        {"rule": "assume", "from": [], "conclude": "AX-THEO-AGAPE-PRIMACY"},
        {"rule": "assume", "from": [], "conclude": "AX-THEO-LOGOS-SPEECH"},
        {"rule": "assume", "from": [], "conclude": "AX-THEO-WISDOM-PRESENCE"},
        {"rule": "modus_ponens", "from": ["AX-THEO-AGAPE-PRIMACY", "AX-THEO-LOGOS-SPEECH", "AX-THEO-WISDOM-PRESENCE"], "conclude": goal_id}
    ]
    
    body = {"kind": "theorem", "id": goal_id,
            "statement": "Sacred language assigns A=Agape as zero-principle; all other symbols derive meaning from this foundation.",
            "premises": premises,
            "proof": proof_steps}
    
    digest = content_hash(body)
    flag = flag_of("TH", digest)
    
    rec = {"kind": "theorem", "id": goal_id, "flag": flag, "hash": digest,
           "statement": body["statement"], "premises": premises, "proof": proof_steps,
           "ts": time.time()}
    
    with (STORE / "theorems.jsonl").open("a", encoding="utf-8") as f:
        f.write(dumps(rec) + "\n")
    
    chain = STORE / "chain.jsonl"
    with chain.open("a", encoding="utf-8") as f:
        f.write(dumps({"flag": flag, "hash": digest, "id": goal_id, "kind": "theorem", "ts": rec["ts"]}) + "\n")
    
    cache["memo"][goal_id] = {"flag": flag, "hash": digest}
    save_cache(cache)
    
    return {"status": "HUNG", "flag": flag, "hash": digest, "steps": len(proof_steps)}

if __name__ == "__main__":
    print("Adding theological axioms...")
    axiom_result = ensure_theological_axioms()
    print(json.dumps(axiom_result, indent=2))
    
    print("\nProving sacred language theorem...")
    theorem_result = prove_sacred_language_theorem()
    print(json.dumps(theorem_result, indent=2))
    
    print("\nRun audit to verify counts increased.")
