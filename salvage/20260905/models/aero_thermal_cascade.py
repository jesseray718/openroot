#!/usr/bin/env python3
"""
OpenRoot AeroCement Thermal Cascade — Full Physics Model + Optimizer
Minimal unit that maximizes useful services (heat + cold + mechanical work)
with the least open-cell cement.

Run: python models/aero_thermal_cascade.py
"""
import numpy as np
from scipy.optimize import differential_evolution
from dataclasses import dataclass

G = 9.81
RHO_AIR = 1.15
CP_AIR = 1005
RHO_WATER = 1000
CP_WATER = 4184
LATENT_HEAT = 2.45e6
SOLAR_PEAK = 950.0
SUN_HOURS = 7.5
SOIL_TEMP = 15.0 + 273.15
AMB_HOT = 35.0 + 273.15
T_HOT = 55.0 + 273.15
T_COLD = 12.0 + 273.15
CD = 0.65
SPECIFIC_SURFACE = 450.0   # m²/m³ — open-cell after bubble collapse
H_CONV = 25.0

@dataclass
class Geometry:
    H_stack: float
    A_vent: float
    A_disc: float
    V_disc: float
    V_lab: float
    V_hot: float
    V_cold: float

def stack_flow(H, A, Th, Tc):
    if Th <= Tc or H <= 0 or A <= 0: return 0.0
    return CD * A * np.sqrt(2 * G * H * ((Th - Tc) / Th))

def absorber_eta(V, A, mdot):
    if A <= 0: return 0.0
    NTU = (H_CONV * SPECIFIC_SURFACE * V) / (mdot * CP_AIR + 1e-6)
    return np.clip(0.92 * (0.6 + 0.4 * (1 - np.exp(-NTU))), 0.5, 0.95)

def lab_eff(V, mdot):
    NTU = (H_CONV * SPECIFIC_SURFACE * V) / (mdot * CP_AIR + 1e-6)
    return 1.0 - np.exp(-min(NTU, 8.0))

def stirling_eta(Th, Tc):
    if Th <= Tc: return 0.0
    return 0.40 * (1.0 - Tc / Th)

def simulate(g: Geometry):
    Q = stack_flow(g.H_stack, g.A_vent, T_HOT, T_COLD)
    mdot = np.clip(RHO_AIR * Q, 0.01, 2.0)
    eta = absorber_eta(g.V_disc, g.A_disc, mdot)
    Q_solar = eta * SOLAR_PEAK * g.A_disc * SUN_HOURS * 3600
    eff = lab_eff(g.V_lab, mdot)
    Q_cool = mdot * CP_AIR * (AMB_HOT - SOIL_TEMP) * 86400 * eff
    Q_hot = min(Q_solar * 0.85, g.V_hot * RHO_WATER * CP_WATER * (T_HOT - (AMB_HOT - 5)))
    Q_cold = min(Q_cool * 0.7, g.V_cold * RHO_WATER * CP_WATER * ((AMB_HOT - 5) - T_COLD))
    W = 0.6 * Q_hot * stirling_eta(T_HOT, T_COLD)
    total = Q_hot + Q_cold + W
    return {
        "solar_kWh": Q_solar / 3.6e6,
        "hot_kWh": Q_hot / 3.6e6,
        "cold_kWh": Q_cold / 3.6e6,
        "mech_kWh": W / 3.6e6,
        "total_kWh": total / 3.6e6,
        "cement_m3": g.V_disc + g.V_lab,
        "deltaT": T_HOT - T_COLD
    }

def objective(x):
    g = Geometry(*x)
    r = simulate(g)
    return -(r["total_kWh"] - 8.0 * r["cement_m3"] - 2.0 * (g.V_hot + g.V_cold))

bounds = [(2,8),(0.05,0.6),(2,25),(0.05,1.5),(0.5,12),(0.2,4),(0.2,4)]

if __name__ == "__main__":
    res = differential_evolution(objective, bounds, seed=42, maxiter=60, popsize=12)
    g = Geometry(*res.x)
    r = simulate(g)
    print("=== OPTIMAL MINIMAL UNIT ===")
    print(f"Stack height          : {g.H_stack:.2f} m")
    print(f"Vent area             : {g.A_vent:.3f} m²")
    print(f"Aero-disc area        : {g.A_disc:.1f} m²")
    print(f"Aero-disc volume      : {g.V_disc:.3f} m³")
    print(f"Labyrinth volume      : {g.V_lab:.2f} m³")
    print(f"Hot tank              : {g.V_hot:.1f} m³")
    print(f"Cold tank             : {g.V_cold:.1f} m³")
    print(f"Open-cell cement      : {r['cement_m3']:.2f} m³")
    print()
    print("=== DESIGN-DAY RESULTS ===")
    print(f"Solar captured        : {r['solar_kWh']:.0f} kWh")
    print(f"Hot stored            : {r['hot_kWh']:.0f} kWh")
    print(f"Cold stored           : {r['cold_kWh']:.0f} kWh")
    print(f"Mechanical work       : {r['mech_kWh']:.1f} kWh")
    print(f"TOTAL USEFUL SERVICES : {r['total_kWh']:.0f} kWh/day")
    print(f"ΔT                    : {r['deltaT']:.0f} K")
    print(f"Energy density        : {r['total_kWh']/r['cement_m3']:.0f} kWh per m³ cement")
