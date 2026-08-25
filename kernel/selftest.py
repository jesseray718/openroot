#!/usr/bin/env python3
"""OpenRoot Kernel Self-Test v1.0.3."""
import math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from kernel.eta import eta, eta_t, alpha_a
from kernel.coordination import coord_cost, resonance_holds
from kernel.synergy import synergy
from kernel.next_joule import score, hard_reject
from kernel.postulates import POSTULATES, count
from kernel.thermal_loop import loop_analysis, evaporative_cooling_power

def test_eta():
    assert eta(1000, 100) == 10.0
    assert eta_t(1000, 1296, 1.0, 100, 1.0) == 12960.0
    assert abs(alpha_a(10.0, 20.0, 1.0) - 10.0) < 1e-9
    print("  OK  eta, eta_t, alpha_a")

def test_coord():
    c = coord_cost(1296, 1, 1.0)
    assert c == 0.0, f"C={c}"
    assert resonance_holds(c)
    print("  OK  C=0 at R=1.0")

def test_synergy():
    s = synergy(1296, 1.0, 6)
    assert abs(s - 3.0) < 0.01, f"S={s}"
    print("  OK  synergy_mult=3.0")

def test_next_joule():
    sc = score(100, 10, 2.0, 1.0, 3.0, True, 10, 1.0)
    assert sc > 0
    assert hard_reject(0.9, False, False, False) is not None
    assert hard_reject(1.0, False, False, False) is None
    print("  OK  score + reject logic")

def test_postulates():
    n = count()
    assert n >= 5, f"expected >=5 postulates, got {n}"
    print(f"  OK  {n} postulates in Newton Chain")

def test_thermal_evap():
    r = loop_analysis(10, 10000.0, 100.0, 3.0, 55.0)
    assert r["total_cooling_watts"] > 0
    assert r["actual_outlet_f"] < r["inlet_temp_f"]
    print(f"  OK  evaporative cooling: {r['latent_cooling_watts']/1000:.1f} kW latent heat")

def main():
    print("=== OpenRoot Kernel v1.0.3 Self-Test ===")
    test_eta()
    test_coord()
    test_synergy()
    test_next_joule()
    test_postulates()
    test_thermal_evap()
    print("=== kernel.selftest OK ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
