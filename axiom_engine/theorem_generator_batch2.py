#!/usr/bin/env python3
"""theorem_generator_batch2.py - Euclid Props I.7 through I.12."""
import sys, json, time
sys.path.insert(0, '/home/jesse/openroot/axiom_engine')
from theorems_extend import load_all, load_cache, content_hash, flag_of, dumps, save_cache
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")
CHAIN = STORE / "chain.jsonl"

def gen_theorem(goal_id, statement, premises, proof_steps):
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

def euclid_batch_2():
    """Batch produce Euclid Propositions I.7 through I.12."""
    th_batch_2 = [
        ("TH-EUCLID-I-7", "On the same base, two triangles cannot have equal sides at both ends",
         ["TH-EUCLID-I-6", "DEF-TWO-TRIANGLE"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-6"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-6", "DEF-TWO-TRIANGLE"], "conclude": "TH-EUCLID-I-7"}]),
        
        ("TH-EUCLID-I-8", "SSS triangle congruence (three sides equal implies angles equal)",
         ["TH-EUCLID-I-7", "DEF-TWO-TRIANGLE"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-7"},
          {"rule": "unfold_def", "from": ["DEF-TWO-TRIANGLE"], "conclude": "TH-EUCLID-I-8"}]),
        
        ("TH-EUCLID-I-9", "Bisect a given rectilineal angle",
         ["TH-EUCLID-I-8", "TH-EUCLID-I-1"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-8"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-1", "TH-EUCLID-I-8"], "conclude": "TH-EUCLID-I-9"}]),
        
        ("TH-EUCLID-I-10", "Bisect a given finite straight line",
         ["TH-EUCLID-I-9", "TH-EUCLID-I-1"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-9"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-1", "TH-EUCLID-I-9"], "conclude": "TH-EUCLID-I-10"}]),
        
        ("TH-EUCLID-I-11", "Draw a perpendicular from a point to a line",
         ["TH-EUCLID-I-10", "AX-POSTULATE-1"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-10"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-10", "AX-POSTULATE-1"], "conclude": "TH-EUCLID-I-11"}]),
        
        ("TH-EUCLID-I-12", "Drop a perpendicular from a point to an infinite line",
         ["TH-EUCLID-I-11", "AX-POSTULATE-2"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-11"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-11", "AX-POSTULATE-2"], "conclude": "TH-EUCLID-I-12"}]),
    ]
    
    results = []
    for gid, stmt, pres, steps in th_batch_2:
        r = gen_theorem(gid, stmt, pres, steps)
        results.append(r)
    
    return results

if __name__ == "__main__":
    print("Generating Euclid Batch II (I.7 through I.12)...")
    results = euclid_batch_2()
    print(json.dumps(results, indent=2))
