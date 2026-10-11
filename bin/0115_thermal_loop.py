"""Evaporative Thermal Loop — water phase change drives cooling.

The law: Hot dry air through wet porous concrete → evaporation occurs.
Latent heat of evaporation is extracted from the air itself.
Earth maintains moisture at ~55°F (13°C). Air exits at 35°F (2°C).
Massive surface area from open-cell (aerocement) structure.
"""
import math

# Constants
CP_AIR = 1005.0           # J/(kg·K) specific heat of dry air
RHO_AIR = 1.2             # kg/m³ at ~25°C
LATENT_HEAT_EVAP = 2450e3 # J/kg at ~30°C (varies with temp)
GROUND_TEMP_F = 55        # constant underground temp
TARGET_OUTLET_F = 35      # achievable with evaporation

def f_to_c(f): return (f - 32) * 5 / 9
def c_to_f(c): return c * 9 / 5 + 32

def evaporative_cooling_power(
    airflow_m3s: float,
    inlet_temp_f: float,
    target_outlet_f: float = TARGET_OUTLET_F,
    ground_temp_f: float = GROUND_TEMP_F,
    concrete_surface_area_m2: float = 10000.0,  # open-cell: massive
    moisture_availability_kg_s: float = 5.0,     # water supply
) -> dict:
    """Cooling power from evaporative loop.

    Hot dry air (e.g., 120°F) enters porous wet concrete tunnel.
    Water in pores evaporates, extracting latent heat from air.
    Air exits at near-ground temperature (35°F achievable).

    Q_total = Q_sensible + Q_latent
    Q_sensible = ṁ · cp · ΔT (air cools by conduction)
    Q_latent = m_water · L (phase change extracts more heat)

    Surface area determines evaporation rate.
    """
    inlet_c = f_to_c(inlet_temp_f)
    target_c = f_to_c(target_outlet_f)
    ground_c = f_to_c(ground_temp_f)
    
    mass_flow = RHO_AIR * airflow_m3s  # kg/s air
    
    # Sensible cooling: air gives up heat to concrete/ground
    delta_t_sensible = inlet_c - target_c
    q_sensible = mass_flow * CP_AIR * delta_t_sensible
    
    # Latent cooling: water evaporates, pulling heat from air
    # Limited by surface area and moisture availability
    evaporation_rate_kg_s = min(
        moisture_availability_kg_s,
        concrete_surface_area_m2 * 0.001  # ~1g/m²/s empirical
    )
    q_latent = evaporation_rate_kg_s * LATENT_HEAT_EVAP
    
    q_total_watts = q_sensible + q_latent
    
    # Check if loop can close
    outlet_actual_f = inlet_temp_f - (q_total_watts / (mass_flow * CP_AIR)) * 9/5
    
    return {
        "inlet_temp_f": inlet_temp_f,
        "target_outlet_f": target_outlet_f,
        "actual_outlet_f": outlet_actual_f,
        "ground_temp_f": ground_temp_f,
        "airflow_m3s": airflow_m3s,
        "mass_flow_kg_s": mass_flow,
        "sensible_cooling_watts": q_sensible,
        "latent_cooling_watts": q_latent,
        "total_cooling_watts": q_total_watts,
        "evaporation_rate_kg_s": evaporation_rate_kg_s,
        "loop_closed": outlet_actual_f <= target_outlet_f + 5,  # ±5°F tolerance
    }

def datacenter_load(
    rack_count: int,
    watts_per_rack: float = 10000.0,
    airflow_m3s_per_rack: float = 1.5,
    exhaust_temp_f: float = 120.0,  # hot aisle
) -> dict:
    """Total heat and airflow from server racks."""
    total_heat = rack_count * watts_per_rack
    total_airflow = rack_count * airflow_m3s_per_rack
    return {
        "total_heat_watts": total_heat,
        "total_airflow_m3s": total_airflow,
        "exhaust_temp_f": exhaust_temp_f,
        "rack_count": rack_count,
    }

def loop_analysis(
    racks: int,
    watts_per_rack: float,
    tunnel_length_m: float,
    tunnel_dia_m: float,
    ground_temp_f: float,
) -> dict:
    """Full thermal loop analysis.

    Tunnel geometry determines surface area.
    Open-cell concrete: ~50 m² surface per m³ volume.
    """
    racks_info = datacenter_load(racks, watts_per_rack)
    tunnel_volume = math.pi * (tunnel_dia_m/2)**2 * tunnel_length_m
    # Aerocement porosity ~50%, internal surface ~50x geometric
    surface_area = tunnel_volume * 50.0  # conservative estimate
    
    cooling_result = evaporative_cooling_power(
        airflow_m3s=racks_info["total_airflow_m3s"],
        inlet_temp_f=racks_info["exhaust_temp_f"],
        ground_temp_f=ground_temp_f,
        concrete_surface_area_m2=surface_area,
    )
    
    return {
        **racks_info,
        **cooling_result,
        "surface_area_m2": surface_area,
        "tunnel_volume_m3": tunnel_volume,
        "can_handle_load": cooling_result["total_cooling_watts"] >= racks_info["total_heat_watts"],
        "excess_capacity_watts": cooling_result["total_cooling_watts"] - racks_info["total_heat_watts"],
    }

if __name__ == "__main__":
    r = loop_analysis(
        racks=10,
        watts_per_rack=10000.0,
        tunnel_length_m=100.0,
        tunnel_dia_m=3.0,
        ground_temp_f=55.0,
    )
    print(f"{r['rack_count']} racks → {r['total_heat_watts']:,.0f} W heat")
    print(f"Airflow: {r['airflow_m3s']:,.1f} m³/s")
    print(f"Inlet: {r['inlet_temp_f']:,.0f}°F → Outlet: {r['actual_outlet_f']:,.0f}°F")
    print(f"Sensible: {r['sensible_cooling_watts']:,.0f} W | Latent: {r['latent_cooling_watts']:,.0f} W")
    print(f"Total cooling: {r['total_cooling_watts']:,.0f} W")
    print(f"Loop closes: {r['can_handle_load']}")
