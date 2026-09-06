#!/usr/bin/env python3
"""
Reversible Gate Simulator — models energy savings of swapping
irreversible gates (NAND/AND/OR) for reversible gates (Toffoli/Fredkin/CNOT).

Landauer: irreversible ops cost >= kT*ln(2) per bit erased
Reversible ops: 0 bits erased, cost approaches 0 asymptotically

Usage: python3 bin/reversible_sim.py <bits> <energy_joules>
"""
import sys
import math

K_B = 1.380649e-23
T = 298  # room temp
LANDAUER = K_B * T * math.log(2)  # J per bit erased

# Gate profiles: (name, input_bits, output_bits, bits_erased)
GATES = {
    "NAND":    {"in": 2, "out": 1, "erased": 1},
    "AND":     {"in": 2, "out": 1, "erased": 1},
    "OR":      {"in": 2, "out": 1, "erased": 1},
    "XOR":     {"in": 2, "out": 1, "erased": 1},
    "NOT":     {"in": 1, "out": 1, "erased": 0},  # already reversible
    "CNOT":    {"in": 2, "out": 2, "erased": 0},  # reversible
    "Toffoli": {"in": 3, "out": 3, "erased": 0},  # reversible
    "Fredkin": {"in": 3, "out": 3, "erased": 0},  # reversible
}

def simulate(bits, actual_energy_j):
    """Simulate energy for same computation using reversible gates."""
    # Assume typical circuit: 70% NAND, 15% AND, 10% OR, 5% NOT
    # Each gate processes ~2 input bits, produces ~1 output (irreversible)
    # Reversible equivalent: same logic with Toffoli/Fredkin (0 bits erased)

    # Irreversible energy (Landauer floor)
    irreversible_bits_erased = int(bits * 0.85)  # 85% of bits get erased
    irr_floor = irreversible_bits_erased * LANDAUER

    # Reversible: 0 bits erased, only adiabatic dissipation
    # Real reversible circuits still dissipate ~1000x above Landauer (not 0)
    # but that's 10^12x better than irreversible
    reversible_floor = 0  # theoretical
    reversible_practical = bits * LANDAUER * 1e-3  # 1000x above floor (adiabatic)

    # Energy savings
    savings_irr = actual_energy_j - irr_floor
    savings_rev = actual_energy_j - reversible_practical
    recovery_fraction = 1.0 - (reversible_practical / actual_energy_j)

    # ACRE savings
    acre_saved = savings_rev / 1000  # 1000 J = 1 ACRE

    print(f"=== REVERSIBLE GATE SIMULATION ===")
    print(f"Input: {bits} bits | Actual: {actual_energy_j} J")
    print(f"")
    print(f"IRREVERSIBLE (current CMOS):")
    print(f"  Bits erased: {irreversible_bits_erased}")
    print(f"  Landauer floor: {irr_floor:.6e} J")
    print(f"  Wasted energy: {savings_irr:.4f} J")
    print(f"")
    print(f"REVERSIBLE (Toffoli/Fredkin/CNOT):")
    print(f"  Bits erased: 0")
    print(f"  Theoretical floor: {reversible_floor:.6e} J")
    print(f"  Practical (adiabatic): {reversible_practical:.6e} J")
    print(f"  Energy saved: {savings_rev:.4f} J ({recovery_fraction*100:.6f}%)")
    print(f"  ACRE credit: {acre_saved:.8f}")
    print(f"")
    print(f"GATE SUBSTITUTION MAP:")
    print(f"  NAND  → Toffoli (2→1 becomes 3→3, 0 bits erased)")
    print(f"  AND   → Toffoli (2→1 becomes 3→3, 0 bits erased)")
    print(f"  OR    → Fredkin (2→1 becomes 3→3, 0 bits erased)")
    print(f"  XOR   → CNOT    (2→1 becomes 2→2, 0 bits erased)")
    print(f"  NOT   → NOT     (already reversible, unchanged)")
    print(f"")

    # Gate-by-gate comparison
    print(f"PER-GATE ENERGY COMPARISON (per operation):")
    for name, g in GATES.items():
        erased = g["erased"]
        cost = erased * LANDAUER
        tag = "REVERSIBLE" if erased == 0 else "irreversible"
        print(f"  {name:10s} ({tag:12s}): {cost:.6e} J  (erases {erased} bit)")

    return {
        "bits": bits,
        "actual_j": actual_energy_j,
        "irreversible_floor": irr_floor,
        "reversible_practical": reversible_practical,
        "energy_saved_j": savings_rev,
        "acre_credit": acre_saved,
        "recovery_fraction": recovery_fraction,
    }

if __name__ == "__main__":
    bits = int(sys.argv[1]) if len(sys.argv) > 1 else 12280
    energy = float(sys.argv[2]) if len(sys.argv) > 2 else 10.315
    result = simulate(bits, energy)

    # Output JSON for ledger integration
    print("---")
    import json
    print(json.dumps(result, indent=2))
