#!/usr/bin/env python3
"""
NEWTON CHAIN ENGINE — Axiomatic Reasoning That Builds on Itself
"""

import json
import hashlib
import os
import sys
import uuid
import time
from copy import deepcopy
from datetime import datetime, timezone
from collections import defaultdict
from flask import Flask, request, render_template_string, jsonify

# PATHS
TERMUX_HOME = "/data/data/com.termux/files/home"
if os.path.exists(TERMUX_HOME):
    ROOT = os.path.join(TERMUX_HOME, "projects/openroot")
else:
    ROOT = os.path.expanduser("~/openroot")

LEDGER_PATH = os.path.join(ROOT, "acre/ledger.jsonl")
LEARNINGS_DB = os.path.join(ROOT, "learnings/newton_chain.json")
os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LEARNINGS_DB), exist_ok=True)

# ============================================================
# PART 1: UNIVERSAL AXIOMS
# ============================================================

AXIOMS = {
    # Physics
    "AX-001": {"statement": "Energy is neither created nor destroyed", "category": "physics", "source": "First Law of Thermodynamics", "immutable": True},
    "AX-002": {"statement": "Entropy of an isolated system never decreases", "category": "physics", "source": "Second Law of Thermodynamics", "immutable": True},
    "AX-003": {"statement": "Every action has an equal and opposite reaction", "category": "physics", "source": "Newton's Third Law", "immutable": True},
    "AX-004": {"statement": "Mass and energy are interchangeable (E=mc^2)", "category": "physics", "source": "Einstein", "immutable": True},
    "AX-005": {"statement": "The speed of light in vacuum is constant for all observers", "category": "physics", "source": "Einstein", "immutable": True},
    "AX-006": {"statement": "Information cannot travel faster than light", "category": "physics", "source": "Relativity", "immutable": True},
    # Mathematics
    "AX-007": {"statement": "The whole is greater than the part", "category": "mathematics", "source": "Euclid's Axioms", "immutable": True},
    "AX-008": {"statement": "Things equal to the same thing are equal to each other", "category": "mathematics", "source": "Euclid", "immutable": True},
    "AX-009": {"statement": "If equals are added to equals, the wholes are equal", "category": "mathematics", "source": "Euclid", "immutable": True},
    "AX-010": {"statement": "A straight line segment can be drawn joining any two points", "category": "mathematics", "source": "Euclid's Postulate 1", "immutable": True},
    "AX-011": {"statement": "Through any point not on a line, exactly one parallel line exists", "category": "mathematics", "source": "Euclid's Parallel Postulate", "immutable": True},
    "AX-012": {"statement": "Infinity exists as a concept but cannot be completed", "category": "mathematics", "source": "Hilbert/Cantor", "immutable": True},
    # Systems Theory
    "AX-013": {"statement": "The behavior of a system emerges from the interaction of its parts", "category": "systems", "source": "General Systems Theory", "immutable": True},
    "AX-014": {"statement": "A system is more than the sum of its parts", "category": "systems", "source": "Aristotle / Fuller", "immutable": True},
    "AX-015": {"statement": "Feedback loops determine system stability", "category": "systems", "source": "Cybernetics", "immutable": True},
    "AX-016": {"statement": "The component with the fewest connections limits the whole system", "category": "systems", "source": "Liebig's Law", "immutable": True},
    "AX-017": {"statement": "In complex systems, small changes can produce disproportionately large effects", "category": "systems", "source": "Chaos Theory", "immutable": True},
    # Computation
    "AX-018": {"statement": "Every bit of information erased costs at least kT*ln(2) joules", "category": "computation", "source": "Landauer's Principle", "immutable": True},
    "AX-019": {"statement": "Computation is a physical process constrained by physical laws", "category": "computation", "source": "Landauer / Feynman", "immutable": True},
    "AX-020": {"statement": "The universe computes; physics is computation", "category": "computation", "source": "Wheeler 'It from Bit'", "immutable": True},
    # Permaculture
    "AX-021": {"statement": "Greatest good for greatest number", "category": "ethics", "source": "Permaculture Ethics", "immutable": True},
    "AX-022": {"statement": "Observe before acting; interact with patience", "category": "permaculture", "source": "Permaculture Principle 1", "immutable": True},
    "AX-023": {"statement": "Capture and store energy when abundant", "category": "permaculture", "source": "Permaculture Principle 2", "immutable": True},
    "AX-024": {"statement": "Obtain a yield; ensure the system produces real value", "category": "permaculture", "source": "Permaculture Principle 3", "immutable": True},
    "AX-025": {"statement": "Apply self-regulation and accept feedback", "category": "permaculture", "source": "Permaculture Principle 4", "immutable": True},
    "AX-026": {"statement": "Use renewable resources over finite ones", "category": "permaculture", "source": "Permaculture Principle 5", "immutable": True},
    "AX-027": {"statement": "Produce no waste; all outputs become inputs", "category": "permaculture", "source": "Permaculture Principle 6", "immutable": True},
    "AX-028": {"statement": "Design from patterns to details", "category": "permaculture", "source": "Permaculture Principle 7", "immutable": True},
    "AX-029": {"statement": "Integrate rather than segregate", "category": "permaculture", "source": "Permaculture Principle 8", "immutable": True},
    "AX-030": {"statement": "Use small and slow solutions", "category": "permaculture", "source": "Permaculture Principle 9", "immutable": True},
    "AX-031": {"statement": "Value and use the edge; diversity happens at boundaries", "category": "permaculture", "source": "Permaculture Principle 10", "immutable": True},
    "AX-032": {"statement": "Creatively use and respond to change", "category": "permaculture", "source": "Permaculture Principle 11", "immutable": True},
    "AX-033": {"statement": "Use and value diversity", "category": "permaculture", "source": "Permaculture Principle 12", "immutable": True},
    # Theology
    "AX-034": {"statement": "Love your neighbor as yourself", "category": "theology", "source": "Matthew 22:39 NASB", "immutable": True},
    "AX-035": {"statement": "It is more blessed to give than to receive", "category": "theology", "source": "Acts 20:35 NASB", "immutable": True},
    "AX-036": {"statement": "Do to others as you would have them do to you", "category": "theology", "source": "Luke 6:31 NASB", "immutable": True},
    "AX-037": {"statement": "You shall know them by their fruits", "category": "theology", "source": "Matthew 7:16 NASB", "immutable": True},
    "AX-038": {"statement": "Seek first the kingdom and all else is added", "category": "theology", "source": "Matthew 6:33 NASB", "immutable": True},
    "AX-039": {"statement": "Ask, and it will be given; seek, and you will find; knock, and it will be opened", "category": "theology", "source": "Matthew 7:7 NASB", "immutable": True},
    # Blockchain
    "AX-040": {"statement": "Proof requires witness; truth demands verification", "category": "consensus", "source": "OpenRoot AX-019", "immutable": True},
    "AX-041": {"statement": "Immutability preserves truth across time", "category": "consensus", "source": "Blockchain principle", "immutable": True},
    # Strategy
    "AX-042": {"statement": "Know yourself and know your enemy; victory requires both", "category": "strategy", "source": "Sun Tzu", "immutable": True},
    "AX-043": {"statement": "All warfare is based on deception", "category": "strategy", "source": "Sun Tzu", "immutable": True},
    "AX-044": {"statement": "The supreme art is to subdue the enemy without fighting", "category": "strategy", "source": "Sun Tzu", "immutable": True},
}

# ============================================================
# PART 2: POSTULATES
# ============================================================

def make_p001(): return {"rule": "Insufficient observation reduces system quality", "derives_from": ["AX-022"], "condition": lambda p: p.get("observation_days", 0) < 7, "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 15, "recommendations": p.get("recommendations", []) + ["Extend observation to 7+ days"]}), "depth": 1}
def make_p002(): return {"rule": "Finite energy sources carry systemic debt", "derives_from": ["AX-026", "AX-002"], "condition": lambda p: p.get("primary_energy_source", "grid").lower() not in ["solar", "wind", "geothermal", "hydro", "biomass", "renewable"], "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 30, "recommendations": p.get("recommendations", []) + ["Migrate to renewable energy source"]}), "depth": 2}
def make_p003(): return {"rule": "Thermal gradients without recovery waste energy", "derives_from": ["AX-001", "AX-023"], "condition": lambda p: p.get("thermal_gradient") and not p.get("waste_heat_recovery"), "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 25, "recommendations": p.get("recommendations", []) + ["Install heat exchanger"]}), "depth": 2}
def make_p004(): return {"rule": "Systems without feedback loops are fragile", "derives_from": ["AX-015", "AX-025"], "condition": lambda p: not p.get("feedback_mechanism"), "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 20, "recommendations": p.get("recommendations", []) + ["Implement feedback monitoring"]}), "depth": 2}
def make_p005(): return {"rule": "Single-pathway systems have single points of failure", "derives_from": ["AX-033", "AX-017"], "condition": lambda p: p.get("pathway_alternatives", 1) < 2, "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 15, "recommendations": p.get("recommendations", []) + ["Add backup pathways"]}), "depth": 2}
def make_p006(): return {"rule": "Waste outputs indicate incomplete design", "derives_from": ["AX-027", "AX-007"], "condition": lambda p: any(o.get("disposition") == "waste" for o in p.get("outputs", [])), "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 20, "recommendations": p.get("recommendations", []) + ["Circulate waste as input"]}), "depth": 2}
def make_p007(): return {"rule": "Long payback indicates poor energy ROI", "derives_from": ["AX-024", "AX-023"], "condition": lambda p: p.get("payback_days", 999) > 365, "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 20, "recommendations": p.get("recommendations", []) + ["Reduce payback below 1 year"]}), "depth": 2}
def make_p008(): return {"rule": "High human input violates least effort principle", "derives_from": ["AX-021", "AX-030"], "condition": lambda p: p.get("human_input", 1) > 10, "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 15, "recommendations": p.get("recommendations", []) + ["Automate to reduce human effort"]}), "depth": 2}
def make_p009(): return {"rule": "Monolithic deployments risk catastrophic failure", "derives_from": ["AX-030", "AX-017"], "condition": lambda p: not p.get("incremental_rollout") and p.get("module_size", 0) > 500, "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 10, "recommendations": p.get("recommendations", []) + ["Phase incremental rollout"]}), "depth": 2}
def make_p010(): return {"rule": "Systems lacking versioning cannot adapt", "derives_from": ["AX-032", "AX-041"], "condition": lambda p: not p.get("change_management"), "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 10, "recommendations": p.get("recommendations", []) + ["Implement version control"]}), "depth": 2}

INITIAL_POSTULATES = {
    "P-001": make_p001(), "P-002": make_p002(), "P-003": make_p003(), "P-004": make_p004(),
    "P-005": make_p005(), "P-006": make_p006(), "P-007": make_p007(), "P-008": make_p008(),
    "P-009": make_p009(), "P-010": make_p010(),
    "P-020": {"rule": "Unobserved high-effort systems are ethically questionable", "derives_from": ["AX-022", "AX-021", "P-001", "P-008"], "condition": lambda p: p.get("observation_days", 0) == 0 and p.get("human_input", 0) > 5, "effect": lambda p: p.update({"acre_eligible": False, "efficiency_penalty": p.get("efficiency_penalty", 0) + 25, "recommendations": p.get("recommendations", []) + ["HALT: Restart with observation phase"]}), "depth": 4},
    "P-021": {"rule": "Finite-energy systems without feedback are doubly unsustainable", "derives_from": ["AX-002", "AX-026", "AX-015", "P-002", "P-004"], "condition": lambda p: p.get("primary_energy_source", "grid").lower() not in ["solar", "wind", "geothermal", "hydro", "biomass", "renewable"] and not p.get("feedback_mechanism"), "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 20, "recommendations": p.get("recommendations", []) + ["Add renewable migration AND feedback"]}), "depth": 5},
    "P-022": {"rule": "Knowledge preserved immutably enables future builders", "derives_from": ["AX-041", "AX-013", "AX-014"], "condition": lambda p: p.get("immutable_record", False) == False, "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 10, "recommendations": p.get("recommendations", []) + ["Anchor to immutable ledger"]}), "depth": 3},
    "P-023": {"rule": "Systems that serve themselves over others violate agape principle", "derives_from": ["AX-034", "AX-035", "AX-021"], "condition": lambda p: p.get("self_serving", False), "effect": lambda p: p.update({"acre_eligible": False, "efficiency_penalty": p.get("efficiency_penalty", 0) + 40, "recommendations": p.get("recommendations", []) + ["Redesign to benefit others"]}), "depth": 3},
    "P-024": {"rule": "Computational work without energy accounting is incomplete", "derives_from": ["AX-018", "AX-019", "AX-001"], "condition": lambda p: p.get("compute_joules", 0) == 0 and p.get("involves_computation", False), "effect": lambda p: p.update({"efficiency_penalty": p.get("efficiency_penalty", 0) + 15, "recommendations": p.get("recommendations", []) + ["Calculate Landauer limit cost"]}), "depth": 3},
}

# ============================================================
# PART 3: ENGINE CLASS
# ============================================================

class NewtonChainEngine:
    def __init__(self, axioms, postulates):
        self.axioms = axioms
        self.postulates = dict(postulates)
        self.proof_chains = []
        self.new_postulates_generated = []
        self.loop_count = 0

    def get_last_hash(self):
        if os.path.exists(LEDGER_PATH):
            try:
                with open(LEDGER_PATH, 'r') as f:
                    lines = [l.strip() for l in f if l.strip()]
                    if lines:
                        return json.loads(lines[-1]).get("hash", "genesis")
            except:
                pass
        return "genesis"

    def apply_all_postulates(self, problem, depth_limit=99):
        problem = deepcopy(problem)
        problem.setdefault("recommendations", [])
        problem.setdefault("efficiency_penalty", 0)
        problem.setdefault("efficiency_bonus", 0)
        problem.setdefault("proof_chain", [])
        problem.setdefault("acre_eligible", True)
        fired = []
        for p_key, p_def in self.postulates.items():
            if p_def["depth"] > depth_limit:
                continue
            try:
                if p_def["condition"](problem):
                    p_def["effect"](problem)
                    problem["proof_chain"].append({"postulate": p_key, "rule": p_def["rule"], "derives_from": p_def["derives_from"], "depth": p_def["depth"]})
                    fired.append(p_key)
            except Exception:
                pass
        return problem, fired

    def detect_novel_combinations(self, fired_sets):
        combo_counts = defaultdict(int)
        for fired in fired_sets:
            if len(fired) >= 2:
                combo = tuple(sorted(fired))
                combo_counts[combo] += 1
        new_postulates = []
        for combo, count in combo_counts.items():
            if count >= 2:
                existing = any(set(p_def.get("combines", [])) == set(combo) for p_def in self.postulates.values())
                if not existing:
                    new_key = f"NP-{len(self.new_postulates_generated)+1:03d}"
                    derives = []
                    for p_key in combo:
                        derives.extend(self.postulates[p_key]["derives_from"])
                    derives = list(set(derives))
                    new_postulate = {
                        "rule": f"Compound pattern: {' + '.join(combo)} fire together",
                        "derives_from": derives, "combines": list(combo),
                        "condition": lambda p, keys=set(combo): all(self.postulates[k]["condition"](p) for k in keys),
                        "effect": lambda p, keys=list(combo): p.update({"efficiency_bonus": p.get("efficiency_bonus", 0) + 5, "recommendations": p.get("recommendations", []) + [f"SYSTEMIC PATTERN: {', '.join(keys)}"]}),
                        "depth": max(self.postulates[k]["depth"] for k in combo) + 1,
                        "auto_generated": True
                    }
                    self.postulates[new_key] = new_postulate
                    self.new_postulates_generated.append(new_key)
                    new_postulates.append(new_key)
        return new_postulates

    def calculate_efficiency(self, problem):
        base = problem.get("base_efficiency", 50.0)
        penalty = problem.get("efficiency_penalty", 0)
        bonus = problem.get("efficiency_bonus", 0)
        return max(0.0, min(100.0, base + bonus - penalty))

    def verify_proof_chain(self, problem):
        chain = problem.get("proof_chain", [])
        for step in chain:
            for source in step.get("derives_from", []):
                if source not in self.axioms and source not in self.postulates:
                    return False, f"Broken chain: {source}"
        return True, f"Valid: {len(chain)} steps traced"

    def run_newton_chain(self, problem, max_loops=6):
        all_results = []
        fired_history = []
        current = deepcopy(problem)
        for loop in range(max_loops):
            self.loop_count = loop + 1
            depth_limit = (loop + 1) * 2
            current, fired = self.apply_all_postulates(current, depth_limit)
            score = self.calculate_efficiency(current)
            fired_history.append(fired)
            all_results.append({"loop": loop + 1, "depth_limit": depth_limit, "postulates_fired": fired, "fired_count": len(fired), "efficiency": score, "total_postulates": len(self.postulates)})
            if len(all_results) >= 2:
                delta = abs(all_results[-1]["efficiency"] - all_results[-2]["efficiency"])
                if delta < 0.5 and len(fired) == len(all_results[-2]["postulates_fired"]):
                    break
        new_posts = self.detect_novel_combinations(fired_history)
        if new_posts and self.loop_count < max_loops:
            current, fired = self.apply_all_postulates(current, 99)
            final_score = self.calculate_efficiency(current)
            all_results.append({"loop": self.loop_count + 1, "depth_limit": 99, "postulates_fired": fired, "fired_count": len(fired), "efficiency": final_score, "total_postulates": len(self.postulates), "new_postulates_active": len(new_posts)})
        valid, verify_msg = self.verify_proof_chain(current)
        return {"loops_executed": len(all_results), "loop_history": all_results, "final_efficiency": all_results[-1]["efficiency"], "initial_efficiency": all_results[0]["efficiency"], "improvement": all_results[-1]["efficiency"] - all_results[0]["efficiency"], "final_problem": current, "recommendations": current.get("recommendations", []), "proof_chain": current.get("proof_chain", []), "proof_valid": valid, "verify_msg": verify_msg, "new_postulates_generated": self.new_postulates_generated, "total_postulates": len(self.postulates), "total_axioms": len(self.axioms)}

    def log_to_acre(self, question, result):
        prev_hash = self.get_last_hash()
        entry = {"timestamp": datetime.now(datetime.UTC).isoformat() + "Z", "type": "newton_chain_proof", "question_hash": hashlib.sha256(question.encode()).hexdigest()[:16], "loops": result["loops_executed"], "final_efficiency": result["final_efficiency"], "improvement": result["improvement"], "proof_chain_length": len(result["proof_chain"]), "proof_valid": result["proof_valid"], "new_postulates": result["new_postulates_generated"], "total_axioms": result["total_axioms"], "total_postulates": result["total_postulates"], "recommendations": result["recommendations"][:5], "prev_hash": prev_hash, "verified": False}
        entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        with open(LEDGER_PATH, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def save_learnings(self, question, result):
        learnings = {"sessions": [], "generated_postulates": {}}
        if os.path.exists(LEARNINGS_DB):
            try:
                with open(LEARNINGS_DB, 'r') as f:
                    learnings = json.load(f)
            except:
                pass
        for p_key in result.get("new_postulates_generated", []):
            p_def = self.postulates.get(p_key, {})
            learnings["generated_postulates"][p_key] = {"rule": p_def.get("rule", ""), "derives_from": p_def.get("derives_from", []), "combines": p_def.get("combines", []), "depth": p_def.get("depth", 0), "created_at": datetime.now(datetime.UTC).isoformat() + "Z"}
        learnings["sessions"].append({"timestamp": datetime.now(datetime.UTC).isoformat() + "Z", "question_hash": hashlib.sha256(question.encode()).hexdigest()[:16], "loops": result["loops_executed"], "final_efficiency": result["final_efficiency"], "proof_valid": result["proof_valid"]})
        with open(LEARNINGS_DB, 'w') as f:
            json.dump(learnings, f, indent=2)

# ============================================================
# PART 4: PARSER
# ============================================================

def parse_question(question):
    q = question.lower()
    base_eff = 50.0
    focus = "decision"
    energy = "grid"
    recs = []
    if "github" in q or "repo" in q:
        base_eff = 80.0
        focus = "automation"
        energy = "solar"
        recs.extend(["[GITHUB] Add README.md", "[GITHUB] Add LICENSE (AGPL-3.0)", "[GITHUB] Create .github/workflows/", "[GITHUB] Add CONTRIBUTING.md"])
    if "thermal" in q or "solar" in q or "heat" in q:
        base_eff = max(base_eff, 75.0)
        focus = "thermal"
        energy = "solar"
    if "automate" in q:
        base_eff = max(base_eff, 70.0)
        focus = "automation"
    return {"id": str(uuid.uuid4()), "original_question": question, "base_efficiency": base_eff, "primary_focus": focus, "primary_energy_source": energy, "observations": [], "observation_days": 0, "seasonal_coverage": False, "energy_streams": [], "waste_heat_recovery": "heat" in q or "thermal" in q, "thermal_gradient": "heat" in q or "thermal" in q, "immediate_output": 0, "projected_output": 100, "payback_days": 365, "feedback_mechanism": "auto" in q, "safety_cutoff": False, "error_margin": 0.5, "materials": [], "outputs": [], "reuse_percentage": 80 if "recycle" in q else 50, "reference_pattern": None, "component_count": 5, "multi_use_component_count": 1, "interface_count": 3, "module_size": 500, "scalability_documented": False, "incremental_rollout": "phase" in q, "edge_optimized": False, "interface_zone_count": 1, "adaptability_rating": 0.5, "change_management": False, "redundancy_factor": 2.0 if "backup" in q else 1.0, "pathway_alternatives": 3 if "backup" in q else 1, "diversity_index": 0.3, "human_input": 8, "involves_computation": "compute" in q or "code" in q, "compute_joules": 0, "immutable_record": "blockchain" in q or "ledger" in q, "self_serving": False, "recommendations": recs, "efficiency_penalty": 0, "efficiency_bonus": 0}

# ============================================================
# PART 5: FLASK APP
# ============================================================

app = Flask(__name__)
ENGINE = NewtonChainEngine(AXIOMS, INITIAL_POSTULATES)

INDEX_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Newton Chain</title>
<style>body{font-family:monospace;background:#0f0f1a;color:#6d4aff;padding:20px}.container{max-width:900px;margin:0 auto}h1{border-bottom:2px solid #6d4aff}textarea{width:100%;height:120px;padding:15px;background:#1a1a2e;border:1px solid #6d4aff;color:#fff;font-family:monospace;box-sizing:border-box}button{background:#6d4aff;color:#fff;border:none;padding:15px 30px;font-size:16px;cursor:pointer;margin-top:10px}.stats{display:flex;gap:15px;margin:15px 0;flex-wrap:wrap}.stat{background:#1a1a2e;padding:15px;border-radius:8px;text-align:center;flex:1;min-width:120px}.stat-val{font-size:28px;color:#6d4aff}.rec-list{list-style:none;padding:0}.rec-list li{padding:8px 0;border-bottom:1px solid #333}.rec-list li:before{content:"→ ";color:#6d4aff}.badge{display:inline-block;padding:5px 15px;border-radius:15px;font-size:12px;margin:5px 0}.badge.ok{background:#0a0;color:#000}.badge.fail{background:#300;color:#f88}table{width:100%;border-collapse:collapse;margin:10px 0}th{text-align:left;padding:8px;border-bottom:2px solid #6d4aff}td{padding:8px;border-bottom:1px solid #222}</style></head>
<body><div class="container">
<h1>🔭 Newton Chain Engine</h1>
<p>{{ axiom_count }} axioms · {{ postulate_count }} postulates · Self-expanding reasoner</p>
<p style="color:#4af;font-style:italic">"If I have seen further it is by standing on the shoulders of giants." — Newton</p>
{% if error %}<div style="background:#300;color:#f88;padding:15px;margin:10px 0">{{ error }}</div>{% endif %}
{% if result %}
<div style="background:#1a1a2e;padding:15px;margin:15px 0;border-radius:8px">
<strong>Question:</strong> {{ question }}<br>
<span class="badge {{ 'ok' if result.proof_valid else 'fail' }}">Proof: {{ 'VALID' if result.proof_valid else 'INVALID' }}</span>
{% if result.new_postulates_generated %}<span class="badge" style="background:#4a0;color:#fff">{{ result.new_postulates_generated|length }} NEW postulates!</span>{% endif %}
</div>
<div class="stats">
<div class="stat"><div class="stat-val">{{ "%.1f"|format(result.final_efficiency) }}%</div><div class="stat-label">Final Efficiency</div></div>
<div class="stat"><div class="stat-val">{{ result.loops_executed }}</div><div class="stat-label">Loops</div></div>
<div class="stat"><div class="stat-val">{{ result.proof_chain|length }}</div><div class="stat-label">Proof Steps</div></div>
<div class="stat"><div class="stat-val">{{ result.total_postulates }}</div><div class="stat-label">Postulates</div></div>
</div>
<table><tr><th>Loop</th><th>Depth</th><th>Fired</th><th>Effic.</th></tr>
{% for entry in result.loop_history %}<tr><td>{{ entry.loop }}</td><td>{{ entry.depth_limit }}</td><td>{{ entry.fired_count }}</td><td>{{ "%.1f"|format(entry.efficiency) }}%</td></tr>{% endfor %}
</table>
<div style="background:#1a1a2e;padding:15px;margin:10px 0">
<h3>Proof Chain ({{ result.proof_chain|length }})</h3>
{% for step in result.proof_chain %}<div style="padding:5px 0;border-bottom:1px solid #333;font-size:13px"><strong>{{ step.postulate }}</strong>: {{ step.rule }} <span style="color:#4af">← {{ step.derives_from|join(', ') }}</span></div>{% endfor %}
</div>
{% if result.new_postulates_generated %}
<div style="background:#1a2e1a;padding:10px;margin:5px 0;border-left:3px solid #4a0"><h3>🌟 New Postulates</h3>
{% for np in result.new_postulates_generated %}<div><strong>{{ np }}</strong> (auto-generated)</div>{% endfor %}
</div>{% endif %}
<div style="background:#1a1a2e;padding:10px;margin:10px 0"><h3>Recommendations</h3><ul class="rec-list">{% for rec in result.recommendations[:8] %}<li>{{ rec }}</li>{% endfor %}</ul></div>
<div style="background:#1a1a2e;padding:10px;font-size:10px;color:#888;word-break:break-all"><strong>ACRE Ledger:</strong> {{ acre_hash }}</div>
{% endif %}
<form method="post" action="/reason">
<textarea name="question" placeholder="Ask anything. Engine chains axioms → postulates → theorems.">{{ question or '' }}</textarea>
<button type="submit">🔭 Run Newton Chain</button>
</form>
<p style="margin-top:30px"><a href="/axioms" style="color:#6d4aff">Axioms</a> · <a href="/postulates" style="color:#6d4aff">Postulates</a> · <a href="/health" style="color:#6d4aff">Health</a></p>
</div></body></html>'''

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, result=None, question="", error=None, axiom_count=len(ENGINE.axioms), postulate_count=len(ENGINE.postulates), acre_hash="")

@app.route("/reason", methods=["POST"])
def reason():
    question = request.form.get("question", "")
    if not question:
        return render_template_string(INDEX_HTML, result=None, question="", error="Enter a question", axiom_count=len(ENGINE.axioms), postulate_count=len(ENGINE.postulates), acre_hash="")
    problem = parse_question(question)
    result = ENGINE.run_newton_chain(problem, max_loops=6)
    acre_entry = ENGINE.log_to_acre(question, result)
    ENGINE.save_learnings(question, result)
    return render_template_string(INDEX_HTML, result=result, question=question, error=None, axiom_count=len(ENGINE.axioms), postulate_count=len(ENGINE.postulates), acre_hash=acre_entry["hash"])

@app.route("/axioms")
def view_axioms():
    html = f"<h1>Axioms ({len(ENGINE.axioms)})</h1><table><tr><th>ID</th><th>Category</th><th>Statement</th></tr>"
    for k, v in sorted(ENGINE.axioms.items()):
        html += f"<tr><td>{k}</td><td>{v['category']}</td><td>{v['statement']}</td></tr>"
    html += "</table><br><a href='/' style='color:#6d4aff'>← Back</a>"
    return html

@app.route("/postulates")
def view_postulates():
    html = f"<h1>Postulates ({len(ENGINE.postulates)})</h1>"
    for k, v in sorted(ENGINE.postulates.items()):
        auto = " 🌟 AUTO" if v.get("auto_generated") else ""
        combines = f" [Combines: {', '.join(v['combines'])}]" if v.get("combines") else ""
        html += f"<div style='background:#1a1a2e;color:#ddd;padding:10px;margin:5px 0'><strong>{k}</strong> (depth {v['depth']}){auto}{combines}<br>{v['rule']}<br><small style='color:#6d4aff'>From: {', '.join(v['derives_from'])}</small></div>"
    html += "<br><a href='/' style='color:#6d4aff'>← Back</a>"
    return html

@app.route("/health")
def health():
    return jsonify({"status": "ok", "axioms": len(ENGINE.axioms), "postulates": len(ENGINE.postulates), "new_generated": len(ENGINE.new_postulates_generated)})

@app.route("/api/v1/reason", methods=["POST"])
def api_reason():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Missing question"}), 400
    problem = parse_question(question)
    result = ENGINE.run_newton_chain(problem, max_loops=6)
    acre = ENGINE.log_to_acre(question, result)
    ENGINE.save_learnings(question, result)
    return jsonify({"success": True, "loops": result["loops_executed"], "efficiency": result["final_efficiency"], "proof_valid": result["proof_valid"], "new_postulates": result["new_postulates_generated"], "recommendations": result["recommendations"][:5], "acre_hash": acre["hash"]})

def run_batch(json_path):
    with open(json_path, 'r') as f:
        ctx = json.load(f)
    items = ctx if isinstance(ctx, list) else ctx.get("tasks", [ctx])
    print(f"\n{'='*72}\n  NEWTON CHAIN BATCH — {len(items)} ITEMS\n{'='*72}\n")
    for item in items:
        q = item.get("name", item.get("task", str(item)[:80])) if isinstance(item, dict) else str(item)
        problem = parse_question(q)
        result = ENGINE.run_newton_chain(problem, max_loops=6)
        ENGINE.log_to_acre(q, result)
        ENGINE.save_learnings(q, result)
        print(f"Q: {q[:60]}\nEffic: {result['final_efficiency']:.1f}% | Loops: {result['loops_executed']} | Proof: {'VALID' if result['proof_valid'] else 'INVALID'}")
        if result['new_postulates_generated']:
            print(f"🌟 NEW: {result['new_postulates_generated']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        batch_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "computational_flow/tasks/pow_log.json")
        run_batch(batch_file)
    else:
        print(f"\n  🔭 NEWTON CHAIN ENGINE\n  {len(AXIOMS)} axioms · {len(INITIAL_POSTULATES)} postulates\n  Web: http://127.0.0.1:5002\n  Batch: python3 newton_chain_fixed.py --batch file.json\n")
        app.run(host="127.0.0.1", port=5002, debug=False, use_reloader=False)
