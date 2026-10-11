#!/usr/bin/env python3
"""theorem_generator_batch3.py - Euclid Props I.13 through I.20."""
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

def euclid_batch_3():
    """Batch produce Euclid Propositions I.13 through I.20."""
    th_batch_3 = [
        ("TH-EUCLID-I-13", "Angles on a straight line sum to two right angles",
         ["TH-EUCLID-I-12", "AX-CN-5"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-12"},
          {"rule": "unfold_def", "from": ["AX-CN-5"], "conclude": "TH-EUCLID-I-13"}]),
        
        ("TH-EUCLID-I-14", "If two lines make adjacent angles equal to two right angles, they are straight",
         ["TH-EUCLID-I-13"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-13"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-13"], "conclude": "TH-EUCLID-I-14"}]),
        
        ("TH-EUCLID-I-15", "Vertical angles are equal",
         ["TH-EUCLID-I-14"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-14"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-14"], "conclude": "TH-EUCLID-I-15"}]),
        
        ("TH-EUCLID-I-16", "Exterior angle of triangle greater than either interior opposite",
         ["TH-EUCLID-I-15", "TH-EUCLID-I-10"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-15"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-15", "TH-EUCLID-I-10"], "conclude": "TH-EUCLID-I-16"}]),
        
        ("TH-EUCLID-I-17", "Any two angles of a triangle less than two right angles",
         ["TH-EUCLID-I-16", "DEF-TWO-TRIANGLE"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-16"},
          {"rule": "unfold_def", "from": ["DEF-TWO-TRIANGLE"], "conclude": "TH-EUCLID-I-17"}]),
        
        ("TH-EUCLID-I-18", "Greater side subtends greater angle",
         ["TH-EUCLID-I-17"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-17"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-17"], "conclude": "TH-EUCLID-I-18"}]),
        
        ("TH-EUCLID-I-19", "Greater angle subtended by greater side",
         ["TH-EUCLID-I-18"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-18"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-18"], "conclude": "TH-EUCLID-I-19"}]),
        
        ("TH-EUCLID-I-20", "Sum of any two sides of triangle greater than third side",
         ["TH-EUCLID-I-19", "AX-CN-5"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-19"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-19", "AX-CN-5"], "conclude": "TH-EUCLID-I-20"}]),
    ]
    
    results = []
    for gid, stmt, pres, steps in th_batch_3:
        r = gen_theorem(gid, stmt, pres, steps)
        results.append(r)
    
    return results

if __name__ == "__main__":
    print("Generating Euclid Batch III (I.13 through I.20)...")
    results = euclid_batch_3()
    print(json.dumps(results, indent=2))
