#!/usr/bin/env python3
import sys
import math

def calculate_synergy(base_values, synergy_matrix, alignment_factor=1.0, coordination_cost=0.0):
    """
    Computes the Synergetic Compoundability Index S:
    S = (sum of V_i) * product(1 + Psi(C_j, C_k)) * (R / (1 + c))
    """
    sum_v = sum(base_values)
    
    synergy_product = 1.0
    for psi in synergy_matrix:
        synergy_product *= (1.0 + psi)
        
    coordination_divisor = 1.0 + coordination_cost
    if coordination_divisor <= 0:
        coordination_divisor = 1.0 
        
    s_index = sum_v * synergy_product * (alignment_factor / coordination_divisor)
    return s_index

if __name__ == "__main__":
    # Example values for AeroCement 2.0 + Ferrocement Dome Pod integration
    v_modules = [10.0, 15.0, 12.5] # Base functional utility scores
    psi_pairs = [0.45, 0.30]       # Interoperability synergy coefficients
    
    # Agape practice resolves coordination cost to 0 (c = 0, R = 1)
    score = calculate_synergy(v_modules, psi_pairs, alignment_factor=1.0, coordination_cost=0.0)
    print(f"Synergetic Compoundability Index (S): {score:.4f}")
