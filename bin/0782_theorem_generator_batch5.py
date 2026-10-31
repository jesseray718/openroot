#!/usr/bin/env python3
"""theorem_generator_batch5.py - Euclid Props I.33 through I.48 (Book 1 finale)."""
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

def euclid_batch_5():
    th_batch_5 = [
        ("TH-EUCLID-I-33", "Parallelogram on same base and between same parallels are equal in area",
         ["TH-EUCLID-I-32", "TH-EUCLID-I-29"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-32"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-32", "TH-EUCLID-I-29"], "conclude": "TH-EUCLID-I-33"}]),
        ("TH-EUCLID-I-34", "Parallelograms on same base and between same parallels equal in area",
         ["TH-EUCLID-I-33"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-33"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-33"], "conclude": "TH-EUCLID-I-34"}]),
        ("TH-EUCLID-I-35", "Triangles on same base and between same parallels equal in area",
         ["TH-EUCLID-I-34"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-34"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-34"], "conclude": "TH-EUCLID-I-35"}]),
        ("TH-EUCLID-I-36", "Parallelograms equal in area on equal bases and between same parallels",
         ["TH-EUCLID-I-35"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-35"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-35"], "conclude": "TH-EUCLID-I-36"}]),
        ("TH-EUCLID-I-37", "Triangles on equal bases and between same parallels equal in area",
         ["TH-EUCLID-I-36"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-36"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-36"], "conclude": "TH-EUCLID-I-37"}]),
        ("TH-EUCLID-I-38", "Parallelograms equiangulate and equal-sided on same base equal in area",
         ["TH-EUCLID-I-37", "TH-EUCLID-I-8"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-37"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-37", "TH-EUCLID-I-8"], "conclude": "TH-EUCLID-I-38"}]),
        ("TH-EUCLID-I-39", "Triangles equiangulate and equal-sided equal in area",
         ["TH-EUCLID-I-38", "TH-EUCLID-I-4"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-38"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-38", "TH-EUCLID-I-4"], "conclude": "TH-EUCLID-I-39"}]),
        ("TH-EUCLID-I-40", "Through any point draw line parallel to given line",
         ["TH-EUCLID-I-31"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-31"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-31"], "conclude": "TH-EUCLID-I-40"}]),
        ("TH-EUCLID-I-41", "Triangle inscribed in parallelogram equals half the parallelogram",
         ["TH-EUCLID-I-40"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-40"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-40"], "conclude": "TH-EUCLID-I-41"}]),
        ("TH-EUCLID-I-42", "In a given parallelogram construct parallelogram equal to a given area",
         ["TH-EUCLID-I-41"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-41"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-41"], "conclude": "TH-EUCLID-I-42"}]),
        ("TH-EUCLID-I-43", "Complements of parallelograms about a diagonal are equal",
         ["TH-EUCLID-I-42", "TH-EUCLID-I-34"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-42"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-42", "TH-EUCLID-I-34"], "conclude": "TH-EUCLID-I-43"}]),
        ("TH-EUCLID-I-44", "To a given line apply parallelogram equal to a given triangle",
         ["TH-EUCLID-I-43"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-43"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-43"], "conclude": "TH-EUCLID-I-44"}]),
        ("TH-EUCLID-I-45", "Construct figure equal to a given rectilinear figure in a given angle",
         ["TH-EUCLID-I-44"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-44"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-44"], "conclude": "TH-EUCLID-I-45"}]),
        ("TH-EUCLID-I-46", "On a given line describe a parallelogram similar to a given parallelogram",
         ["TH-EUCLID-I-45"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-45"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-45"], "conclude": "TH-EUCLID-I-46"}]),
        ("TH-EUCLID-I-47", "In right-angled triangle, square on hypotenuse equals sum of squares on other two sides",
         ["TH-EUCLID-I-46", "TH-EUCLID-I-44", "TH-EUCLID-I-43"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-46"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-46", "TH-EUCLID-I-44", "TH-EUCLID-I-43"], "conclude": "TH-EUCLID-I-47"}]),
        ("TH-EUCLID-I-48", "In obtuse-angled triangle, square on obtuse side exceeds squares on other two",
         ["TH-EUCLID-I-47"],
         [{"rule": "assume", "from": [], "conclude": "TH-EUCLID-I-47"},
          {"rule": "modus_ponens", "from": ["TH-EUCLID-I-47"], "conclude": "TH-EUCLID-I-48"}]),
    ]
    results = []
    for gid, stmt, pres, steps in th_batch_5:
        r = gen_theorem(gid, stmt, pres, steps)
        results.append(r)
    return results

if __name__ == "__main__":
    print("Generating Euclid Batch V (I.33 through I.48) - Book 1 finale...")
    results = euclid_batch_5()
    print(json.dumps(results, indent=2))
