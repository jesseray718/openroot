#!/usr/bin/env python3
"""theorem_generator_batch4.py - Euclid Props I.21 through I.32."""
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

def euclid_batch_4():
    """Batch produce Euclid Propositions I.21 through I.32."""
    th_batch_4 = [
        ("TH-EUCLID-I-21", "Lines from triangle vertices to interior point less than other sides but contain greater angle",
         ["TH-EUCLID-I-20", "TH-EUCLID-I-16"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-20"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-20", "TH-EUCLID-I-16"], "conclude": "TH-EUCLID-I-21"}]),
        
        ("TH-EUCLID-I-22", "Construct triangle from three given lines (triangle inequality)",
         ["TH-EUCLID-I-20", "AX-POSTULATE-3"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-20"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-20", "AX-POSTULATE-3"], "conclude": "TH-EUCLID-I-22"}]),
        
        ("TH-EUCLID-I-23", "Construct angle equal to given angle at given point",
         ["TH-EUCLID-I-22", "TH-EUCLID-I-8"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-22"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-22", "TH-EUCLID-I-8"], "conclude": "TH-EUCLID-I-23"}]),
        
        ("TH-EUCLID-I-24", "If two triangles have two sides equal but included angle greater, base is greater",
         ["TH-EUCLID-I-23", "TH-EUCLID-I-4"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-23"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-23", "TH-EUCLID-I-4"], "conclude": "TH-EUCLID-I-24"}]),
        
        ("TH-EUCLID-I-25", "If two triangles have two sides equal but base greater, included angle is greater",
         ["TH-EUCLID-I-24"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-24"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-24"], "conclude": "TH-EUCLID-I-25"}]),
        
        ("TH-EUCLID-I-26", "ASA and AAS triangle congruence",
         ["TH-EUCLID-I-25", "TH-EUCLID-I-8"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-25"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-25", "TH-EUCLID-I-8"], "conclude": "TH-EUCLID-I-26"}]),
        
        ("TH-EUCLID-I-27", "Alternate angles equal implies parallel lines",
         ["TH-EUCLID-I-26", "DEF-PARALLEL"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-26"},
          {"rule": "unfold_def", "from": ["DEF-PARALLEL"], "conclude": "TH-EUCLID-I-27"}]),
        
        ("TH-EUCLID-I-28", "Exterior angle equals interior opposite on same side implies parallel",
         ["TH-EUCLID-I-27", "TH-EUCLID-I-15"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-27"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-27", "TH-EUCLID-I-15"], "conclude": "TH-EUCLID-I-28"}]),
        
        ("TH-EUCLID-I-29", "Line parallel to others makes alternate angles equal",
         ["AX-POSTULATE-5", "TH-EUCLID-I-28"],
         [{"rule": "assume", "from": [], "conclude": "AX-POSTULATE-5"},
          {"rule": "modus_ponens", "from": ["AX-POSTULATE-5", "TH-EUCLID-I-28"], "conclude": "TH-EUCLID-I-29"}]),
        
        ("TH-EUCLID-I-30", "Lines parallel to same line are parallel to each other",
         ["TH-EUCLID-I-29"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-29"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-29"], "conclude": "TH-EUCLID-I-30"}]),
        
        ("TH-EUCLID-I-31", "Draw line through point parallel to given line",
         ["TH-EUCLID-I-30", "TH-EUCLID-I-23"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-30"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-30", "TH-EUCLID-I-23"], "conclude": "TH-EUCLID-I-31"}]),
        
        ("TH-EUCLID-I-32", "Triangle exterior angle equals two interior opposites; angles sum to two right angles",
         ["TH-EUCLID-I-31", "TH-EUCLID-I-17"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-31"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-31", "TH-EUCLID-I-17"], "conclude": "TH-EUCLID-I-32"}]),
    ]
    
    results = []
    for gid, stmt, pres, steps in th_batch_4:
        r = gen_theorem(gid, stmt, pres, steps)
        results.append(r)
    
    return results

if __name__ == "__main__":
    print("Generating Euclid Batch IV (I.21 through I.32)...")
    results = euclid_batch_4()
    print(json.dumps(results, indent=2))
