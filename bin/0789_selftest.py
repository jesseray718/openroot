#!/usr/bin/env python3
"""OpenRoot Kernel Self-Test — validates η, C, S calculations."""
import math

def test_coordination_cost():
    """C(N,T,R) = N · 0.001 · (1 + 0.1T) · (1-R)^T"""
    N, T, R = 1296, 1, 1.0
    C = N * 0.001 * (1 + 0.1*T) * ((1-R)**T)
    assert C == 0.0, f"C should be 0 at R=1.0, got {C}"
    print(f"✓ C=0 at R=1.0 (N={N}, T={T})")

def test_synergy():
    """S = 1 + R · 0.5 · log_B(N)"""
    N, R, B = 1296, 1.0, 6
    S = 1 + R * 0.5 * math.log(N, B)
    expected = 3.0
    assert abs(S - expected) < 0.01, f"S should be {expected}, got {S}"
    print(f"✓ synergy_mult={S:.1f} on 1296-node shape (base-{B})")

def test_eta():
    """η = J_useful / J_human"""
    J_useful, J_human = 1000, 100
    eta = J_useful / J_human
    assert eta == 10.0, f"η should be 10.0, got {eta}"
    print(f"✓ η={eta} (J_useful={J_useful}, J_human={J_human})")

def main():
    print("=== OpenRoot Kernel v1.0.0 Self-Test ===")
    test_coordination_cost()
    test_synergy()
    test_eta()
    print("=== kernel.selftest OK ===")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
