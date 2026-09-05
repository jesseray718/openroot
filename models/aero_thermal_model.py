#!/usr/bin/env python3
"""
Full Physics Model: AeroCement Passive Thermal Cascading System
Minimal-unit optimization for maximum useful energy services
(heat + cold + mechanical/electrical potential) with minimal material.

Based on:
- Stack-effect natural draft
- Volumetric open-cell absorber (aero-disc)
- High-surface-area underground labyrinth (open-cell cement)
- Sensible thermal batteries (water in ferrocement tanks)
- Latent heat exchange via moisture / desiccant interaction with open cells
- ΔT → work via Stirling (practical efficiency)

Author: physics model for Jesse / OpenRoot AeroCement
"""

import numpy as np
from scipy.optimize import differential_evolution, minimize
from dataclasses import dataclass
from typing import Dict, Tuple

# ============================================================
# PHYSICAL CONSTANTS
# ============================================================
G = 9.81                    # m/s²
RHO_AIR = 1.15              # kg/m³ (warm air approx)
CP_AIR = 1005               # J/(kg·K)
RHO_WATER = 1000            # kg/m³
CP_WATER = 4184             # J/(kg·K)
LATENT_HEAT = 2.45e6        # J/kg (approx at 30-40°C)
SOLAR_PEAK = 950.0          # W/m² clear sky
SUN_HOURS = 7.5             # effective full-sun hours / day (mid-latitude summer)
SOIL_TEMP = 15.0 + 273.15   # K stable deep soil
AMB_HOT = 35.0 + 273.15     # K design day
T_STORE_HOT_TARGET = 55.0 + 273.15  # K practical storage
T_STORE_COLD_TARGET = 12.0 + 273.15 # K
CD = 0.65                   # discharge coefficient stack

# Open-cell cement assumptions (user-controlled bubble size)
# Specific surface area achievable with close-packed uniform bubbles after collapse
SPECIFIC_SURFACE = 450.0    # m² / m³ of bulk open-cell volume (conservative; can be higher)
POROSITY = 0.55             # open volume fraction
H_CONV = 25.0               # W/(m²·K) effective convective coefficient in porous media under forced flow

# ============================================================
# DATA CLASSES
# ============================================================
@dataclass
class SystemGeometry:
    H_stack: float          # stack height difference (m)
    A_vent: float           # effective free area of vents (m²)
    A_disc: float           # projected solar absorbing area of aero-disc (m²)
    V_disc: float           # bulk volume of volumetric open-cell absorber (m³)
    V_lab: float            # bulk volume of underground labyrinth concrete (m³)
    V_hot: float            # water volume hot battery (m³)
    V_cold: float           # water volume cold battery (m³)
    L_lab_equiv: float      # equivalent flow path length (m) for pressure / residence

@dataclass
class DailyResults:
    Q_solar_thermal: float      # J/day
    Q_geo_latent: float         # J/day (earth + latent)
    Q_hot_stored: float         # J
    Q_cold_stored: float        # J
    delta_T: float              # K average available
    W_mech_potential: float     # J/day (Stirling work potential)
    W_elec_potential: float     # J/day (assuming generator η=0.9)
    total_useful: float         # J/day
    total_useful_kWh: float
    cement_volume: float        # m³ open-cell material
    tank_volume: float
    energy_per_cement: float    # kWh / m³ cement

# ============================================================
# CORE PHYSICS FUNCTIONS
# ============================================================
def stack_flow(H: float, A_vent: float, T_hot: float, T_cold: float) -> float:
    """Volumetric flow rate Q (m³/s) from stack effect."""
    if T_hot <= T_cold or H <= 0 or A_vent <= 0:
        return 0.0
    dT = T_hot - T_cold
    Q = CD * A_vent * np.sqrt(2 * G * H * (dT / T_hot))
    return Q

def absorber_efficiency(V_disc: float, A_disc: float, m_dot: float) -> float:
    """
    Effective solar-to-fluid efficiency for volumetric open-cell absorber.
    High internal area + multiple reflections → high η even without concentration.
    """
    if A_disc <= 0:
        return 0.0
    # Optical + volumetric absorption base
    eta_opt = 0.92
    # Heat transfer effectiveness rises with specific surface and residence
    A_internal = SPECIFIC_SURFACE * V_disc
    # Simple effectiveness model
    NTU = (H_CONV * A_internal) / (m_dot * CP_AIR + 1e-6)
    eta_ht = 1 - np.exp(-NTU)
    eta = eta_opt * (0.6 + 0.4 * eta_ht)  # blends optical with transfer
    return np.clip(eta, 0.5, 0.95)

def labyrinth_effectiveness(V_lab: float, m_dot: float) -> float:
    """NTU-effectiveness for high-surface underground labyrinth."""
    A_s = SPECIFIC_SURFACE * V_lab
    NTU = (H_CONV * A_s) / (m_dot * CP_AIR + 1e-6)
    # For multipass / long path, effectiveness approaches 1 - exp(-NTU)
    return 1.0 - np.exp(-min(NTU, 8.0))

def latent_geo_contribution(V_lab: float, m_dot: float, hours: float = 24.0) -> float:
    """
    Combined geothermal conduction + latent heat from moisture exchange
    in open-cell structure. Conservative estimate.
    """
    # Geothermal base flux through the volume (very rough)
    # Better: surface area contact with soil
    A_soil_contact = 2.5 * (V_lab ** (2/3))  # approx external surface
    Q_geo = 0.08 * A_soil_contact * hours * 3600  # \~0.08 W/m² * area * time → J
    
    # Latent: open cells can exchange significant moisture
    # Assume 0.5–2 kg water vapor exchange per m³ per day under driven flow
    moisture_exchange_kg = 1.2 * V_lab * (m_dot / 0.05)  # scales weakly with flow
    moisture_exchange_kg = np.clip(moisture_exchange_kg, 0, 30 * V_lab)
    Q_latent = moisture_exchange_kg * LATENT_HEAT * 0.6  # 60% recoverable
    return Q_geo + Q_latent

def stirling_efficiency(T_h: float, T_c: float) -> float:
    """Practical Stirling efficiency (fraction of Carnot)."""
    if T_h <= T_c:
        return 0.0
    carnot = 1.0 - (T_c / T_h)
    # Low-ΔT Stirlings typically achieve 25–45% of Carnot depending on design & size
    # Optimistic but realistic for a well-built engine with good regenerator: 0.40
    return 0.40 * carnot

# ============================================================
# FULL SYSTEM SIMULATION (one day design day)
# ============================================================
def simulate(geo: SystemGeometry) -> DailyResults:
    # Average operating temperatures
    T_hot = T_STORE_HOT_TARGET
    T_cold = T_STORE_COLD_TARGET
    T_amb = AMB_HOT
    
    # 1. Stack-driven flow (use average ΔT)
    Q_flow = stack_flow(geo.H_stack, geo.A_vent, T_hot, T_cold)
    m_dot = RHO_AIR * Q_flow  # kg/s continuous average
    
    # Cap flow to reasonable values for small system
    m_dot = np.clip(m_dot, 0.01, 2.0)
    
    # 2. Solar thermal capture through aero-disc
    eta_abs = absorber_efficiency(geo.V_disc, geo.A_disc, m_dot)
    Q_solar = eta_abs * SOLAR_PEAK * geo.A_disc * SUN_HOURS * 3600  # J/day
    
    # 3. Labyrinth heat/cold exchange + latent + geo
    eff_lab = labyrinth_effectiveness(geo.V_lab, m_dot)
    # Cooling potential: bring ambient air toward soil temp
    dT_possible = T_amb - SOIL_TEMP
    Q_cool_potential = m_dot * CP_AIR * dT_possible * 86400 * eff_lab
    Q_geo_lat = latent_geo_contribution(geo.V_lab, m_dot)
    
    # 4. Storage capacities (sensible, one full charge cycle per day assumed)
    Q_hot_cap = geo.V_hot * RHO_WATER * CP_WATER * (T_hot - (T_amb - 5))  # from near amb
    Q_cold_cap = geo.V_cold * RHO_WATER * CP_WATER * ((T_amb - 5) - T_cold)
    
    # Actual stored limited by capture and capacity
    Q_hot_stored = min(Q_solar * 0.85, Q_hot_cap)  # 15% distribution loss
    Q_cold_stored = min(Q_cool_potential * 0.7 + Q_geo_lat * 0.4, Q_cold_cap)
    
    # 5. Temperature differential available for work
    delta_T = T_hot - T_cold
    
    # 6. Work potential
    # Heat that can be run through Stirling: portion of the hot stream
    Q_available_for_work = Q_hot_stored * 0.6  # leave some for direct heat use
    eta_s = stirling_efficiency(T_hot, T_cold)
    W_mech = Q_available_for_work * eta_s
    W_elec = W_mech * 0.90  # generator
    
    # Total useful services (thermal + work)
    # Count heat and cold at face value (they displace equivalent electricity that would otherwise be used)
    total_useful = Q_hot_stored + Q_cold_stored + W_mech
    
    cement_vol = geo.V_disc + geo.V_lab
    tank_vol = geo.V_hot + geo.V_cold
    
    return DailyResults(
        Q_solar_thermal=Q_solar,
        Q_geo_latent=Q_geo_lat,
        Q_hot_stored=Q_hot_stored,
        Q_cold_stored=Q_cold_stored,
        delta_T=delta_T,
        W_mech_potential=W_mech,
        W_elec_potential=W_elec,
        total_useful=total_useful,
        total_useful_kWh=total_useful / 3.6e6,
        cement_volume=cement_vol,
        tank_volume=tank_vol,
        energy_per_cement= (total_useful / 3.6e6) / (cement_vol + 1e-6)
    )

# ============================================================
# OPTIMIZATION: maximize useful energy / (cement + 0.3*tanks)
# subject to reasonable bounds for a minimal prototype unit
# ============================================================
def objective(x):
    H, Avent, Adisc, Vdisc, Vlab, Vhot, Vcold = x
    geo = SystemGeometry(
        H_stack=H,
        A_vent=Avent,
        A_disc=Adisc,
        V_disc=Vdisc,
        V_lab=Vlab,
        V_hot=Vhot,
        V_cold=Vcold,
        L_lab_equiv=20.0
    )
    res = simulate(geo)
    # Maximize useful kWh per day while penalizing size
    # Strong preference for high energy density
    score = res.total_useful_kWh - 8.0 * res.cement_volume - 2.0 * res.tank_volume
    return -score  # minimize negative

# Bounds for minimal practical unit (prototype to small home scale)
bounds = [
    (2.0, 8.0),     # H_stack m
    (0.05, 0.6),    # A_vent m²
    (2.0, 25.0),    # A_disc m²
    (0.05, 1.5),    # V_disc m³
    (0.5, 12.0),    # V_lab m³
    (0.2, 4.0),     # V_hot m³
    (0.2, 4.0),     # V_cold m³
]

if __name__ == "__main__":
    print("=" * 70)
    print("AEROCEMENT PASSIVE THERMAL SYSTEM — FULL PHYSICS OPTIMIZATION")
    print("=" * 70)
    
    # Global optimizer (robust)
    result = differential_evolution(
        objective,
        bounds,
        seed=42,
        maxiter=80,
        popsize=15,
        workers=1,
        atol=1e-3
    )
    
    x_opt = result.x
    geo_opt = SystemGeometry(
        H_stack=x_opt[0],
        A_vent=x_opt[1],
        A_disc=x_opt[2],
        V_disc=x_opt[3],
        V_lab=x_opt[4],
        V_hot=x_opt[5],
        V_cold=x_opt[6],
        L_lab_equiv=20.0
    )
    
    res = simulate(geo_opt)
    
    print("\n--- OPTIMAL MINIMAL UNIT ---")
    print(f"Stack height H                : {geo_opt.H_stack:.2f} m")
    print(f"Vent free area A_vent         : {geo_opt.A_vent:.3f} m²")
    print(f"Aero-disc projected area      : {geo_opt.A_disc:.2f} m²")
    print(f"Aero-disc bulk volume         : {geo_opt.V_disc:.3f} m³")
    print(f"Labyrinth bulk volume         : {geo_opt.V_lab:.2f} m³")
    print(f"Hot battery water volume      : {geo_opt.V_hot:.2f} m³")
    print(f"Cold battery water volume     : {geo_opt.V_cold:.2f} m³")
    
    print("\n--- DAILY ENERGY RESULTS (design hot sunny day) ---")
    print(f"Solar thermal captured        : {res.Q_solar_thermal/3.6e6:.1f} kWh")
    print(f"Geo + latent contribution     : {res.Q_geo_latent/3.6e6:.1f} kWh")
    print(f"Hot energy stored             : {res.Q_hot_stored/3.6e6:.1f} kWh")
    print(f"Cold energy stored            : {res.Q_cold_stored/3.6e6:.1f} kWh")
    print(f"Available ΔT                  : {res.delta_T:.1f} K")
    print(f"Mechanical work potential     : {res.W_mech_potential/3.6e6:.2f} kWh")
    print(f"Electrical potential (90%)    : {res.W_elec_potential/3.6e6:.2f} kWh")
    print(f"TOTAL USEFUL SERVICES         : {res.total_useful_kWh:.1f} kWh/day")
    print(f"Open-cell cement volume       : {res.cement_volume:.2f} m³")
    print(f"Energy density                : {res.energy_per_cement:.1f} kWh / m³ cement")
    
    print("\n--- KEY PHYSICS PARAMETERS USED ---")
    print(f"Specific surface (open-cell)  : {SPECIFIC_SURFACE} m²/m³")
    print(f"Convective h                  : {H_CONV} W/m²K")
    print(f"Stirling fraction of Carnot   : 0.40")
    print(f"Absorber optical base         : 0.92")
    
    print("\nOptimization success:", result.success)
    print("Message:", result.message)
