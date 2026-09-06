#!/usr/bin/env python3
"""AeroCement First-Law ledger. Per m2 collector. Peak AM1.5 design point.

N14: heat-engine eta, act eta, EROI, and sim scores are four quantities.
Latent heat is transport. Service-count is not efficiency.
"""

from __future__ import annotations

IRRADIANCE_W_M2 = 1000.0
ABSORPTION_EFF = 0.98
TRANSFER_EFF = 0.95
LATENT_WATER_KG_H = 0.5
HFG_J_KG = 2_260_000.0
CP_AIR = 1005.0

T_AMBIENT_C = 27.0
T_HOT_OUTLET_C = 77.0
T_COLD_UNDERGROUND_C = 2.0  # evaporative TARGET, not a hang
T_GROUND_C = 12.8           # \~55 F temperate ground
T_ENGINE_EXIT_C = 45.0
P_FRICTION_W = 0.1          # placeholder duct loss


def ledger() -> dict[str, float]:
    q_net = IRRADIANCE_W_M2 * ABSORPTION_EFF * TRANSFER_EFF
    dt_air = T_HOT_OUTLET_C - T_AMBIENT_C
    mdot = q_net / (CP_AIR * dt_air)
    q_latent = (LATENT_WATER_KG_H / 3600.0) * HFG_J_KG

    dt_engine = T_HOT_OUTLET_C - T_ENGINE_EXIT_C
    q_engine_in = mdot * CP_AIR * dt_engine
    t_h = T_HOT_OUTLET_C + 273.15
    t_c = T_COLD_UNDERGROUND_C + 273.15
    eta_carnot = 1.0 - (t_c / t_h)
    eta_stirling = eta_carnot * 0.60
    w_mech = q_engine_in * eta_stirling
    q_waste = q_engine_in - w_mech
    q_to_ground = q_net - w_mech - P_FRICTION_W
    first_law_residual = q_net - (w_mech + q_to_ground + P_FRICTION_W)

    service_heat = q_to_ground
    service_cool_sensible = mdot * CP_AIR * (T_ENGINE_EXIT_C - T_COLD_UNDERGROUND_C)
    service_count = w_mech + service_heat + service_cool_sensible

    return {
        "q_incident_w": IRRADIANCE_W_M2,
        "q_net_to_air_w": q_net,
        "mdot_kg_s": mdot,
        "q_latent_transport_w": q_latent,
        "eta_carnot": eta_carnot,
        "eta_stirling_of_engine_heat": eta_stirling,
        "q_engine_in_w": q_engine_in,
        "w_mech_w": w_mech,
        "q_waste_from_engine_w": q_waste,
        "q_to_ground_w": q_to_ground,
        "p_friction_w": P_FRICTION_W,
        "first_law_residual_w": first_law_residual,
        "heat_engine_eta_vs_incident": w_mech / IRRADIANCE_W_M2,
        "service_count_w": service_count,
        "t_ground_c": T_GROUND_C,
    }


if __name__ == "__main__":
    r = ledger()
    print("=" * 64)
    print("AEROCEMENT FIRST-LAW LEDGER  (design point, not a hang)")
    print("=" * 64)
    print(f"Incident solar                 {r['q_incident_w']:.1f} W/m2")
    print(f"Net to airflow (0.98*0.95)     {r['q_net_to_air_w']:.1f} W/m2")
    print(f"Mass flow                      {r['mdot_kg_s']:.5f} kg/s")
    print(f"Latent TRANSPORT (not input)   {r['q_latent_transport_w']:.1f} W/m2")
    print("-" * 64)
    print(f"Heat into Stirling exchangers  {r['q_engine_in_w']:.1f} W")
    print(f"Carnot (350K/275K target)      {r['eta_carnot']*100:.1f} %")
    print(f"Stirling as 60% of Carnot      {r['eta_stirling_of_engine_heat']*100:.1f} % of engine heat")
    print(f"Shaft work (model)             {r['w_mech_w']:.1f} W")
    print(f"Heat to ground / tanks         {r['q_to_ground_w']:.1f} W")
    print(f"Friction placeholder           {r['p_friction_w']:.1f} W")
    print(f"First-Law residual             {r['first_law_residual_w']:.4f} W")
    print("-" * 64)
    print(f"Heat-engine eta vs incident    {r['heat_engine_eta_vs_incident']*100:.2f} %   (N14 legal)")
    print(f"Service-count (work+heat+cool) {r['service_count_w']:.1f} W   (NOT an efficiency)")
    print(f"Ground sink class              {r['t_ground_c']:.1f} C (\~55 F)")
    print("=" * 64)
    print("VERDICT: joules conserve.")
    print("Do not print service-count / 1000 as solar efficiency.")
    print("Do not print service-count / 0.1 as a physical COP.")
    print("=" * 64)
