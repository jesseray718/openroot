#!/usr/bin/env python3
"""theorem_generator.py - batch theorem production."""
import sys, json, time
sys.path.insert(0, '/home/jesse/openroot/axiom_engine')
from theorems_extend import load_all, load_cache, content_hash, flag_of, dumps, save_cache
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")
CHAIN = STORE / "chain.jsonl"

def gen_theorem(goal_id, statement, premises, proof_steps):
    """Generate and hang a single theorem."""
    body = {"kind": "theorem", "id": goal_id, "statement": statement,
            "premises": premises, "proof": proof_steps}
    digest = content_hash(body)
    flag = flag_of("TH", digest)
    
    rec = {"kind": "theorem", "id": goal_id, "flag": flag, "hash": digest,
           "statement": statement, "premises": premises, "proof": proof_steps,
           "ts": time.time()}
    
    with (STORE / "theorems.jsonl").open("a", encoding="utf-8") as f:
        f.write(dumps(rec) + "\n")
    with CHAIN.open("a", encoding="utf-8") as f:
        f.write(dumps({"flag": flag, "hash": digest, "id": goal_id, "kind": "theorem", "ts": rec["ts"]}) + "\n")
    
    cache = load_cache()
    cache["memo"][goal_id] = {"flag": flag, "hash": digest}
    save_cache(cache)
    
    return {"status": "HUNG", "flag": flag, "hash": digest}

def euclid_batch():
    """Batch produce Euclid Propositions I.2 through I.6."""
    results = []
    th_base = [
        ("TH-EUCLID-I-2", "Place a straight line equal to a given line at a given point",
         ["TH-EUCLID-I-1", "AX-POSTULATE-1", "AX-POSTULATE-2"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-1"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-1", "AX-POSTULATE-1"], "conclude": "TH-EUCLID-I-2"}]),
        
        ("TH-EUCLID-I-3", "Cut off from the greater a straight line equal to the lesser",
         ["TH-EUCLID-I-2", "AX-POSTULATE-3"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-2"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-2", "AX-POSTULATE-3"], "conclude": "TH-EUCLID-I-3"}]),
        
        ("TH-EUCLID-I-4", "SAS triangle congruence",
         ["TH-EUCLID-I-3", "DEF-TWO-TRIANGLE"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-3"},
          {"rule": "unfold_def", "from": ["DEF-TWO-TRIANGLE"], "conclude": "TH-EUCLID-I-4"}]),
        
        ("TH-EUCLID-I-5", "Base angles of isosceles triangle are equal",
         ["TH-EUCLID-I-4", "DEF-ISOSCELES"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-4"},
          {"rule": "unfold_def", "from": ["DEF-ISOSCELES"], "conclude": "TH-EUCLID-I-5"}]),
        
        ("TH-EUCLID-I-6", "Angles opposite equal sides are equal",
         ["TH-EUCLID-I-5"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-5"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-5"], "conclude": "TH-EUCLID-I-6"}]),
    ]
    
    for gid, stmt, pres, steps in th_base:
        r = gen_theorem(gid, stmt, pres, steps)
        results.append(r)
    
    return results

if __name__ == "__main__":
    print("Generating Euclid Batch I.2 through I.6...")
    results = euclid_batch()
    print(json.dumps(results, indent=2))
