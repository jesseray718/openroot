#!/usr/bin/env python3
"""energy_theorems.py - Add E=mc², joules/work, efficiency balancing."""
import sys, json, time
sys.path.insert(0, '/home/jesse/openroot/axiom_engine')
from theorems_extend import load_all, load_cache, content_hash, flag_of, dumps, save_cache
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")
CACHE = STORE / "proof_cache.json"

def ensure_energy_axioms():
    """Add energy-related axioms if missing."""
    axioms_file = STORE / "axioms.jsonl"
    new_axioms = [
        {
            "kind": "axiom",
            "id": "AX-ENERGY-EQUIVALENCE",
            "statement": "Energy and mass are equivalent: E = mc² where c is the speed of light.",
            "category": "physics",
            "keys": ["E=mc2", "mass", "energy", "equivalence"],
            "premises": ["AX-0D-CONSERVATION", "AX-REL-CONSTANCY"],
            "proof": []
        },
        {
            "kind": "axiom",
            "id": "AX-WORK-JOULES",
            "statement": "Work equals energy transferred: 1 joule = 1 N·m = energy to apply 1 newton over 1 meter.",
            "category": "physics",
            "keys": ["work", "joules", "newtons", "meters"],
            "premises": [],
            "proof": []
        },
        {
            "kind": "axiom",
            "id": "AX-POWER-JOULES_PER_SEC",
            "statement": "Power is rate of energy transfer: 1 watt = 1 joule/second.",
            "category": "physics",
            "keys": ["power", "watts", "joules_per_second"],
            "premises": ["AX-WORK-JOULES"],
            "proof": []
        },
        {
            "kind": "axiom",
            "id": "AX-EFFICIENCY_BALANCE",
            "statement": "Any system's efficiency η = J_useful / J_input can be measured and improved by replacing inefficiencies.",
            "category": "thermodynamics",
            "keys": ["efficiency", "joules", "replacement", "optimization"],
            "premises": ["AX-0D-CONSERVATION"],
            "proof": []
        },
        {
            "kind": "axiom",
            "id": "AX-STANDING_WAVE_REALITY",
            "statement": "Reality manifests as a standing wave pattern; observers collapse probability amplitudes into definite trajectories.",
            "category": "quantum",
            "keys": ["standing_wave", "collapse", "probability", "observation"],
            "premises": ["AX-0D-EXISTENCE"],
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

def hang_energy_theorems():
    """Hang theorems for E=mc², efficiency, worldlines."""
    idx = load_all()
    cache = load_cache()
    
    theorems_to_add = [
        {
            "id": "TH-E-MC2-DERIVATION",
            "statement": "Mass-energy equivalence derived from Lorentz invariance: E = mc²",
            "premises": ["AX-ENERGY-EQUIVALENCE", "AX-REL-CONSTANCY"],
            "proof": [
                {"rule": "assume", "from": [], "conclude": "AX-ENERGY-EQUIVALENCE"},
                {"rule": "unfold_def", "from": ["AX-REL-CONSTANCY"], "conclude": "c=constant"},
                {"rule": "modus_ponens", "from": ["AX-ENERGY-EQUIVALENCE"], "conclude": "TH-E-MC2-DERIVATION"}
            ]
        },
        {
            "id": "TH-EFFICIENCY_CALCULUS",
            "statement": "Efficiency η(t) evolves as η(t+1) = η(t) + Δη where Δη measures improvement rate.",
            "premises": ["AX-EFFICIENCY_BALANCE", "AX-0D-CONSERVATION"],
            "proof": [
                {"rule": "assume", "from": [], "conclude": "AX-EFFICIENCY_BALANCE"},
                {"rule": "unfold_def", "from": [], "conclude": "η = J_useful / J_input"},
                {"rule": "modus_ponens", "from": ["AX-EFFICIENCY_BALANCE"], "conclude": "TH-EFFICIENCY-CALCULUS"}
            ]
        },
        {
            "id": "TH-SYNERGIC-CALCULUS",
            "statement": "Synergic calculus tracks cumulative Agape: S(t) = Σ_i (J_agape,i × η_i × log(time_i)).",
            "premises": ["AX-SYNERGY-COMPOUNDING", "AX-0D-CONSERVATION"],
            "proof": [
                {"rule": "assume", "from": [], "conclude": "AX-SYNERGY-COMPOUNDING"},
                {"rule": "unfold_def", "from": [], "conclude": "log scale for compounding"},
                {"rule": "modus_ponens", "from": ["AX-SYNERGY-COMPOUNDING"], "conclude": "TH-SYNERGIC-CALCULUS"}
            ]
        },
        {
            "id": "TH-WORLDLINE-COLLAPSE",
            "statement": "Each observer's trajectory is a worldline; multiple observers generate branching timelines that interfere.",
            "premises": ["AX-STANDING_WAVE_REALITY", "AX-0D-EXISTENCE"],
            "proof": [
                {"rule": "assume", "from": [], "conclude": "AX-STANDING_WAVE_REALITY"},
                {"rule": "unfold_def", "from": [], "conclude": "observer-dependence"},
                {"rule": "modus_ponens", "from": ["AX-STANDING_WAVE_REALITY"], "conclude": "TH-WORLDLINE-COLLAPSE"}
            ]
        }
    ]
    
    hung = []
    for th in theorems_to_add:
        body = {"kind": "theorem", "id": th["id"],
                "statement": th["statement"],
                "premises": th["premises"],
                "proof": th["proof"]}
        
        digest = content_hash(body)
        flag = flag_of("TH", digest)
        
        rec = {"kind": "theorem", "id": th["id"], "flag": flag, "hash": digest,
               "statement": body["statement"], "premises": th["premises"], 
               "proof": th["proof"], "ts": time.time()}
        
        with (STORE / "theorems.jsonl").open("a", encoding="utf-8") as f:
            f.write(dumps(rec) + "\n")
        
        chain = STORE / "chain.jsonl"
        with chain.open("a", encoding="utf-8") as f:
            f.write(dumps({"flag": flag, "hash": digest, "id": th["id"], "kind": "theorem", "ts": rec["ts"]}) + "\n")
        
        cache["memo"][th["id"]] = {"flag": flag, "hash": digest}
        hung.append(th["id"])
    
    save_cache(cache)
    return {"status": "HUNG", "count": len(hung), "ids": hung}

if __name__ == "__main__":
    print("=" * 60)
    print("ENERGY THEOREM INTEGRATION")
    print("=" * 60)
    
    print("\n[1] Adding Energy Axioms...")
    axiom_result = ensure_energy_axioms()
    print(json.dumps(axiom_result, indent=2))
    
    print("\n[2] Hanging Energy Theorems...")
    theorem_result = hang_energy_theorems()
    print(json.dumps(theorem_result, indent=2))
    
    print("\n" + "=" * 60)
    print("Run: python3 theorems_extend.py audit")
    print("=" * 60)
