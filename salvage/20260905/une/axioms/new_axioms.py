#!/usr/bin/env python3
"""
OpenRoot Axiom Extensions — NA-011 through NA-015
Generated from cross-document analysis of 46,170 documents.
Consolidates 3 permutation candidates into unified axiom.
"""

# ── NA-011: Unified Computational Integrity Axiom ──────────────
AXIOM_NA_011 = {
    "id": "NA-011",
    "name": "Computational Integrity Convergence",
    "statement": (
        "Decentralized computation requires tamper-evident state integrity; "
        "blockchain provides the provenance layer; physical thermodynamic "
        "limits constrain all computational processes."
    ),
    "domains": ["computation", "systems", "blockchain"],
    "frequency": 23713,
    "subsumes": ["NA-011", "NA-012", "NA-013"],  # three rotations unified
    "derived_from": "cross_document_analysis_v0.6",
    "engine_mapping": "Knowledge ∩ Finance",
    "formal": {
        "provenance": "∀ op ∈ Ops: ∃ hash(op) ∈ Blockchain ⇒ tamper_evident(op)",
        "thermal_bound": "∀ op ∈ Ops: E_dissipated(op) ≥ k_B·T·ln(2)  [Landauer]",
        "integrity": "verify(system_state) ⇔ merkle_root(blockchain) == computed_root(state)",
    },
}

# ── NA-014: Thermodynamic Computation Boundary ────────────────
AXIOM_NA_014 = {
    "id": "NA-014",
    "name": "Thermal Computation Boundary",
    "statement": (
        "Every computational operation dissipates heat proportional to "
        "information entropy destroyed. System efficiency equals useful_work "
        "divided by total thermal dissipation."
    ),
    "domains": ["thermal", "computation", "systems"],
    "frequency": 9479,
    "engine_mapping": "Energy ∩ Knowledge",
    "formal": {
        "landauer_limit": "E_min = k_B · T · ln(2) ≈ 2.848e-21 J at T=300K",
        "system_efficiency": "η_sys = W_useful / Q_dissipated",
        "thermal_constraint": "∀ compute_node: Q_dissipated ≤ Q_max(material, T_ambient, k_thermal)",
    },
    "links": ["structure_enforcer.py:landauer_cost()", "arm_energy:estimate_inference_joules()"],
}

# ── NA-015: Material Substrate Constraint ─────────────────────
AXIOM_NA_015 = {
    "id": "NA-015",
    "name": "Material Substrate Constraint",
    "statement": (
        "Computational substrate material properties — thermal conductivity, "
        "specific heat, tensile strength — define upper bounds on system "
        "throughput and durability."
    ),
    "domains": ["materials", "computation", "systems"],
    "frequency": 9116,
    "engine_mapping": "Material ∩ Knowledge ∩ Energy",
    "formal": {
        "thermal_conductivity": "k_material → max_heat_flux → max_clock_frequency",
        "durability": "fatigue_cycles(material) → MTBF(compute_node)",
        "throughput_bound": "max_ops_per_second = f(k_thermal, c_p, ρ, T_operating)",
    },
    "links": ["aerocement/SPEC-H003.md", "AE-GFRC thermal properties"],
}

NEW_AXIOMS = [AXIOM_NA_011, AXIOM_NA_014, AXIOM_NA_015]


def merge_into_foundation(existing_path: str, new_axioms: list) -> dict:
    """Merge new axioms into foundation_of_axioms.json without clobbering."""
    import json, os
    
    if os.path.exists(existing_path):
        with open(existing_path, 'r') as f:
            foundation = json.load(f)
    else:
        foundation = {"version": "0.6", "axioms": [], "postulates": []}
    
    existing_ids = {a.get("id") for a in foundation.get("axioms", [])}
    
    for ax in new_axioms:
        if ax["id"] not in existing_ids:
            # Remove subsumed IDs from existing (NA-012, NA-013 absorbed into NA-011)
            if "subsumes" in ax:
                foundation["axioms"] = [
                    a for a in foundation.get("axioms", [])
                    if a.get("id") not in ax["subsumes"][1:]  # keep NA-011, remove 012/013
                ]
            foundation.setdefault("axioms", []).append(ax)
            print(f"  + Added {ax['id']}: {ax['name']}")
        else:
            print(f"  = {ax['id']} already present, skipping")
    
    # Update version
    foundation["version"] = "0.7-pre"
    foundation["axiom_count"] = len(foundation.get("axioms", []))
    
    with open(existing_path, 'w') as f:
        json.dump(foundation, f, indent=2, ensure_ascii=False)
    
    print(f"\n  Foundation updated: {foundation['axiom_count']} axioms at {existing_path}")
    return foundation


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    path = os.path.join(base, "foundation", "foundation_of_axioms.json")
    merge_into_foundation(path, NEW_AXIOMS)
