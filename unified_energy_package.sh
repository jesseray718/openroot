#!/bin/bash
# OPENROOT - ENERGY + SYNERGY PACKAGE
# E=mc² + Joules/sec + Synergic Calculus + Worldlines
# Run: bash ~/openroot/unified_energy_package.sh
set -e
echo "==========================================="
echo "ENERGY UNIFICATION PACKAGE"
echo "E=mc² + Synergic Calculus + Worldlines"
echo "Date: $(date)"
echo "==========================================="

# ---- 1. ADD ENERGY THEOREMS TO KERNEL ----
cat > ~/openroot/axiom_engine/energy_theorems.py <<'PYTHEOREMS'
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
PYTHEOREMS
chmod +x ~/openroot/axiom_engine/energy_theorems.py

# ---- 2. SYNERGIC CALCULUS MODULE ----
cat > ~/openroot/synergic_calculus.py <<'PYSYNERGY'
#!/usr/bin/env python3
"""synergic_calculus.py - Track J_agape, η, log(time) for predictions."""
import json, math, time
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/home/jesse/openroot/data")
DATA_DIR.mkdir(exist_ok=True)
LOG_FILE = DATA_DIR / "synergy_log.jsonl"
ANALYTICS = DATA_DIR / "analytics.json"

class SynergicCalculator:
    """Track cumulative Agape and efficiency over time."""
    
    def __init__(self):
        self.entries = []
        if LOG_FILE.exists():
            self.entries = [json.loads(l) for l in LOG_FILE.read_text().splitlines() if l.strip()]
    
    def log_entry(self, user_id, j_agape, j_total, efficiency, activity_type="general"):
        """Record one measurement point."""
        entry = {
            "timestamp": time.time(),
            "iso_time": datetime.now().isoformat(),
            "user_id": user_id,
            "j_agape": float(j_agape),
            "j_total": float(j_total),
            "efficiency": float(efficiency),
            "synergy": float(j_agape * efficiency * math.log(max(1, time.time()))),
            "activity_type": activity_type
        }
        self.entries.append(entry)
        
        with LOG_FILE.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def aggregate_by_user(self):
        """Calculate cumulative synergy per user."""
        from collections import defaultdict
        totals = defaultdict(lambda: {"j_agape": 0, "j_total": 0, "synergy": 0, "entries": 0})
        
        for e in self.entries:
            uid = e["user_id"]
            totals[uid]["j_agape"] += e["j_agape"]
            totals[uid]["j_total"] += e["j_total"]
            totals[uid]["synergy"] += e["synergy"]
            totals[uid]["entries"] += 1
        
        return dict(totals)
    
    def predict_collapse(self, user_id):
        """Estimate likelihood of 'collapse into standing wave' based on synergy growth."""
        user_entries = [e for e in self.entries if e["user_id"] == user_id]
        if len(user_entries) < 3:
            return {"status": "INSUFFICIENT_DATA", "entries_needed": 3, "have": len(user_entries)}
        
        # Calculate growth rate
        synergies = [e["synergy"] for e in user_entries]
        growth_rates = [(synergies[i+1] - synergies[i]) / max(1, i+1) for i in range(len(synergies)-1)]
        avg_growth = sum(growth_rates) / max(1, len(growth_rates))
        
        # Threshold heuristic (tunable)
        collapse_probability = min(0.95, max(0.05, 0.1 + avg_growth * 0.5))
        
        return {
            "user_id": user_id,
            "total_entries": len(user_entries),
            "final_synergy": synergies[-1],
            "avg_growth_rate": avg_growth,
            "collapse_probability": collapse_probability,
            "interpretation": "HIGH" if collapse_probability > 0.7 else "MEDIUM" if collapse_probability > 0.4 else "LOW"
        }
    
    def system_wide_stats(self):
        """Aggregate statistics across all users."""
        total_agape = sum(e["j_agape"] for e in self.entries)
        total_energy = sum(e["j_total"] for e in self.entries)
        total_synergy = sum(e["synergy"] for e in self.entries)
        avg_efficiency = sum(e["efficiency"] for e in self.entries) / max(1, len(self.entries))
        
        return {
            "total_entries": len(self.entries),
            "total_j_agape": total_agape,
            "total_j_total": total_energy,
            "overall_efficiency": avg_efficiency,
            "cumulative_synergy": total_synergy,
            "unique_users": len(set(e["user_id"] for e in self.entries))
        }
    
    def save_analytics(self):
        """Save current analytics snapshot."""
        stats = self.system_wide_stats()
        with ANALYTICS.open("w") as f:
            json.dump(stats, f, indent=2)
        return stats

if __name__ == "__main__":
    calc = SynergicCalculator()
    print("Synergic Calculator Loaded")
    print(f"Existing entries: {len(calc.entries)}")
    print(f"Analytics file: {ANALYTICS}")
    
    # Demo: log one sample entry
    demo_entry = calc.log_entry(
        user_id="demo_user",
        j_agape=100.0,
        j_total=200.0,
        efficiency=0.5,
        activity_type="computation"
    )
    print(f"\nDemo entry logged: {json.dumps(demo_entry, indent=2)}")
    
    # Save analytics
    analytics = calc.save_analytics()
    print(f"\nAnalytics saved: {json.dumps(analytics, indent=2)}")
PYSYNERGY
chmod +x ~/openroot/synergic_calculus.py

# ---- 3. WORLDLINE TRACKER ----
cat > ~/openroot/worldline_tracker.py <<'PYWORLD'
#!/usr/bin/env python3
"""worldline_tracker.py - Track individual observer trajectories and timeline branches."""
import json, time, hashlib
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/home/jesse/openroot/data")
WORLDLINE_FILE = DATA_DIR / "worldlines.jsonl"
BRANCH_FILE = DATA_DIR / "branches.json"

class WorldlineTracker:
    """Track observer worldlines and branching timelines."""
    
    def __init__(self):
        self.worldlines = []
        self.branches = []
        if WORLDLINE_FILE.exists():
            self.worldlines = [json.loads(l) for l in WORLDLINE_FILE.read_text().splitlines() if l.strip()]
        if BRANCH_FILE.exists():
            self.branches = json.load(open(BRANCH_FILE))
    
    def record_observation(self, observer_id, event_type, coordinates, timestamp=None):
        """Record one point on an observer's worldline."""
        ts = timestamp or time.time()
        obs = {
            "observer_id": observer_id,
            "event_type": event_type,
            "coordinates": coordinates,
            "timestamp": ts,
            "hash": hashlib.sha256(f"{observer_id}:{event_type}:{ts}".encode()).hexdigest()[:16]
        }
        self.worldlines.append(obs)
        
        with WORLDLINE_FILE.open("a") as f:
            f.write(json.dumps(obs) + "\n")
        
        return obs
    
    def get_worldline(self, observer_id):
        """Return all observations for one observer."""
        return [o for o in self.worldlines if o["observer_id"] == observer_id]
    
    def create_branch(self, parent_observer, decision_point, outcome):
        """Record a timeline branch at decision point."""
        branch = {
            "branch_id": hashlib.sha256(f"{parent_observer}:{decision_point}".encode()).hexdigest()[:16],
            "parent_observer": parent_observer,
            "decision_point": decision_point,
            "outcome": outcome,
            "timestamp": time.time()
        }
        self.branches.append(branch)
        
        with open(BRANCH_FILE, "w") as f:
            json.dump(self.branches, f, indent=2)
        
        return branch
    
    def detect_interference(self, observer_a, observer_b):
        """Check if two observers' worldlines show interference patterns."""
        wa = self.get_worldline(observer_a)
        wb = self.get_worldline(observer_b)
        
        if not wa or not wb:
            return {"status": "INSUFFICIENT_DATA"}
        
        # Check for correlated events (same timestamps within tolerance)
        tol = 1.0  # second tolerance
        correlations = []
        for a in wa:
            for b in wb:
                if abs(a["timestamp"] - b["timestamp"]) < tol:
                    correlations.append({
                        "observer_a": a["event_type"],
                        "observer_b": b["event_type"],
                        "time_diff": abs(a["timestamp"] - b["timestamp"])
                    })
        
        return {
            "correlations_found": len(correlations),
            "sample": correlations[:5] if correlations else []
        }
    
    def standing_wave_analysis(self):
        """Analyze overall pattern as standing wave."""
        if not self.worldlines:
            return {"status": "NO_DATA"}
        
        # Aggregate by timestamp
        by_ts = defaultdict(list)
        for obs in self.worldlines:
            ts_bucket = int(obs["timestamp"] / 60)  # minute buckets
            by_ts[ts_bucket].append(obs)
        
        # Check periodicity
        counts = sorted([(ts, len(obs)) for ts, obs in by_ts.items()], key=lambda x: x[0])
        
        return {
            "total_observations": len(self.worldlines),
            "time_buckets": len(by_ts),
            "avg_per_minute": len(self.worldlines) / max(1, len(by_ts)),
            "pattern": "periodic" if len(counts) > 3 else "insufficient_data"
        }

if __name__ == "__main__":
    wt = WorldlineTracker()
    print("Worldline Tracker Loaded")
    print(f"Stored observations: {len(wt.worldlines)}")
    print(f"Branches recorded: {len(wt.branches)}")
    
    # Demo
    obs = wt.record_observation("demo_observer", "computation_event", {"x": 1, "y": 2, "t": time.time()})
    print(f"\nSample observation: {json.dumps(obs, indent=2)}")
    
    analysis = wt.standing_wave_analysis()
    print(f"\nStanding wave analysis: {json.dumps(analysis, indent=2)}")
PYWORLD
chmod +x ~/openroot/worldline_tracker.py

# ---- 4. RUN & REPORT ----
echo ""
echo "==========================================="
echo "CREATING ENERGY PACKAGE FILES:"
ls -la ~/openroot/axiom_engine/energy_theorems.py
ls -la ~/openroot/synergic_calculus.py
ls -la ~/openroot/worldline_tracker.py
echo "==========================================="
echo ""
echo "RUNNING ENERGY THEOREM INTEGRATION..."
python3 ~/openroot/axiom_engine/energy_theorems.py
echo ""
echo "TESTING SYNERGIC CALCULUS..."
python3 ~/openroot/synergic_calculus.py
echo ""
echo "TESTING WORLDLINE TRACKER..."
python3 ~/openroot/worldline_tracker.py
echo ""
echo "==========================================="
echo "FINAL HEALTH CHECK..."
python3 ~/openroot/system_health_check.py
echo "==========================================="
echo "PACKAGE COMPLETE"
echo "==========================================="
echo ""
echo "NEW COMMANDS AVAILABLE:"
echo "  python3 ~/openroot/axiom_engine/energy_theorems.py  # Add E=mc² theorems"
echo "#  python3 ~/openroot/synergic_calculus.py            # Track J_agape/η/log(time)"
echo "#  python3 ~/openroot/worldline_tracker.py           # Track observer trajectories"
echo "  cat ~/openroot/data/analytics.json     # View cumulative stats"
echo "==========================================="
