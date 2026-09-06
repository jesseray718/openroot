#!/usr/bin/env python3
"""Dynamic Efficiency Coefficient v0.1 — permaculture-weighted priority formula.
   Usage: python3 bin/efficiency_coefficient.py --benefit 9 --urgency 8 --compounding 1.5
   Integrates H-003 thermal, ACRE PoPW tagging, UNE registries, kai9000 workflows."""
import argparse, json
from pathlib import Path

def efficiency_coefficient(benefit: float = 5.0, urgency: float = 5.0, slump: float = 0.0,
                           compounding: float = 1.0, cost: float = 1.0, effort: float = 1.0,
                           verification: float = 1.0) -> float:
    """Efficiency = (Benefit × Urgency × (1-Slump) × Compounding) / (Cost × Effort × Verification)
    Scales: benefit/urgency/compounding 0-10 (higher=better); slump/cost/effort/verif 0-10 (higher=worse).
    Use permaculture (Obtain Yield, Value Marginal, Self-Regulate, Integrate) to assign values.
    Higher score = move system forward with least human effort + max compounding infrastructure."""
    return (benefit * urgency * (1 - slump) * compounding) / max(cost * effort * verification, 0.0001)

def demo_openroot_priorities():
    print("=== OpenRoot Efficiency Coefficient Demo (current state) ===")
    tasks = {
        "A: Make acre_tagger dynamically load une/symbol_registry.json + AXIOM_REGISTRY.md": {
            "benefit": 9, "urgency": 8, "slump": 0.1, "compounding": 1.6,
            "cost": 2, "effort": 3, "verification": 2,
            "why": "Enables every future H-003/ACRE claim to auto-tag with real UNE/AX; compounds lookup + DAO integrity"
        },
        "B: Propose + 2-validator AX-041 (new axiom)": {
            "benefit": 6, "urgency": 4, "slump": 0.2, "compounding": 1.2,
            "cost": 3, "effort": 4, "verification": 3,
            "why": "Good but lower leverage until core tagging + registry load is dynamic"
        },
        "C: Publish first tagged H-003 PoPW claim to Appropedia + Zenodo": {
            "benefit": 7, "urgency": 6, "slump": 0.15, "compounding": 1.3,
            "cost": 2, "effort": 3, "verification": 2,
            "why": "Falsifiability + publish path; solid but secondary to making tagging infrastructure dynamic"
        }
    }
    scored = []
    for name, p in tasks.items():
        score = efficiency_coefficient(**{k: p[k] for k in ["benefit","urgency","slump","compounding","cost","effort","verification"]})
        scored.append((score, name, p["why"]))
    scored.sort(reverse=True)
    for score, name, why in scored:
        print(f"{score:6.2f} | {name}\n       → {why}")
    print(f"\n>>> HIGHEST: {scored[0][1]}")
    print(">>> Recommended next atomic action: implement dynamic UNE load in acre_tagger.py (then re-tag all claims)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Efficiency Coefficient for any OpenRoot task")
    parser.add_argument("--benefit", type=float, default=5.0)
    parser.add_argument("--urgency", type=float, default=5.0)
    parser.add_argument("--slump", type=float, default=0.0)
    parser.add_argument("--compounding", type=float, default=1.0)
    parser.add_argument("--cost", type=float, default=1.0)
    parser.add_argument("--effort", type=float, default=1.0)
    parser.add_argument("--verification", type=float, default=1.0)
    args = parser.parse_args()
    if any(getattr(args, k) != parser.get_default(k) for k in ["benefit","urgency","slump","compounding","cost","effort","verification"]):
        score = efficiency_coefficient(args.benefit, args.urgency, args.slump, args.compounding,
                                       args.cost, args.effort, args.verification)
        print(f"Efficiency Coefficient: {score:.2f}")
    else:
        demo_openroot_priorities()
