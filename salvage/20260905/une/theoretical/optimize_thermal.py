#!/data/data/com.termux/files/usr/bin/python3
"""
Pure theoretical thermal cascade optimizer.
No sensors. Only mathematics and physics.
Goal: maximum energy capture and storage per kg of air.
Single-person, modular, decentralized.
"""

import json, math
from copy import deepcopy

# Physical constants
CP_AIR = 1005.0          # J/(kg·K)
SIGMA = 5.670374419e-8   # Stefan-Boltzmann
T_SKY = 255.0            # K, typical clear-sky effective temperature
T_AMB = 305.0            # K, hot day ambient

def carnot(Th, Tc):
    if Th <= Tc:
        return 0.0
    return 1.0 - (Tc / Th)

def radiative_power(area, T_surf, eps=0.95, T_sky=T_SKY):
    """Net power rejected to sky (positive = heat leaving the surface)"""
    return eps * SIGMA * area * (T_surf**4 - T_sky**4)

def evaluate(system):
    """Compute all theoretical flows in J/s and return scores"""
    m = system["mass_flow_kg_s"]
    Th = system["T_hot_K"]
    Tc = system["T_cold_K"]
    eps_regen = system["regen_effectiveness"]
    area_disc = system["area_disc_m2"]
    area_sky = system["area_sky_m2"]
    eps_sky = system["eps_sky"]

    # Available enthalpy stream
    available = m * CP_AIR * (Th - Tc)

    # Regenerative recovery
    recovered = available * eps_regen
    net_to_engine = available - recovered

    # Carnot limit on the net stream
    eta_c = carnot(Th, Tc)
    work = net_to_engine * eta_c * system.get("engine_fraction", 0.4)  # realistic fraction of Carnot

    # Sky rejection (helps keep Tc low)
    Q_sky = radiative_power(area_sky, Tc, eps_sky)

    # Simple score: work per kg of air
    work_per_kg = work / m if m > 0 else 0.0

    return {
        "available_J_s": available,
        "recovered_J_s": recovered,
        "net_to_engine_J_s": net_to_engine,
        "work_J_s": work,
        "sky_reject_J_s": Q_sky,
        "work_per_kg": work_per_kg,
        "eta_carnot": eta_c,
        "eta_system": work / available if available > 0 else 0.0
    }

def find_bottleneck(scores, system):
    """Identify the single highest-leverage theoretical bottleneck"""
    candidates = []

    if system["regen_effectiveness"] < 0.95:
        candidates.append(("regen_effectiveness", 0.95 - system["regen_effectiveness"], "Raise regenerative effectiveness toward 0.95 via counter-flow geometry and surface area"))

    if system["T_cold_K"] > T_SKY + 15:
        candidates.append(("T_cold_K", system["T_cold_K"] - (T_SKY + 10), "Lower cold-side temperature via larger sky radiator + volumetric evaporative surface"))

    if system["T_hot_K"] < 350:
        candidates.append(("T_hot_K", 360 - system["T_hot_K"], "Raise hot-side temperature via selective absorber or modest concentration"))

    # Mass-flow optimality is checked by re-evaluation, not listed here

    if not candidates:
        return None, "System is near theoretical limits under current assumptions"

    # Highest leverage = largest absolute gap
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0], candidates[0][2]

def optimize(system, max_iter=8):
    history = []
    current = deepcopy(system)

    for i in range(max_iter):
        scores = evaluate(current)
        bottleneck, action = find_bottleneck(scores, current)

        history.append({
            "iteration": i,
            "scores": scores,
            "bottleneck": bottleneck,
            "action": action,
            "state": deepcopy(current)
        })

        if bottleneck is None:
            break

        # Apply superior theoretical replacement
        if bottleneck == "regen_effectiveness":
            current["regen_effectiveness"] = min(0.95, current["regen_effectiveness"] + 0.15)
        elif bottleneck == "T_cold_K":
            current["T_cold_K"] = max(T_SKY + 10, current["T_cold_K"] - 12)
            current["area_sky_m2"] *= 1.4
        elif bottleneck == "T_hot_K":
            current["T_hot_K"] = min(380, current["T_hot_K"] + 20)

    final_scores = evaluate(current)
    return current, final_scores, history

if __name__ == "__main__":
    # Starting single-person theoretical system
    initial = {
        "mass_flow_kg_s": 0.02,
        "T_hot_K": 320.0,
        "T_cold_K": 290.0,
        "regen_effectiveness": 0.40,
        "area_disc_m2": 24.2,
        "area_sky_m2": 4.0,
        "eps_sky": 0.92,
        "engine_fraction": 0.40
    }

    optimized, final, history = optimize(initial)

    print("=" * 60)
    print("THEORETICAL OPTIMIZATION COMPLETE")
    print("=" * 60)
    print("\nInitial work per kg air: {:.1f} J/kg".format(history[0]["scores"]["work_per_kg"]))
    print("Final   work per kg air: {:.1f} J/kg".format(final["work_per_kg"]))
    print("Final system η (work/available): {:.3f}".format(final["eta_system"]))
    print("\nFinal state:")
    for k, v in optimized.items():
        print(f"  {k}: {v}")
    print("\nBottleneck path taken:")
    for h in history:
        if h["bottleneck"]:
            print(f"  iter {h['iteration']}: {h['bottleneck']} → {h['action']}")
