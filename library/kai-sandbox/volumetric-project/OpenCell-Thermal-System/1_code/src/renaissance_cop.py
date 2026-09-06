#!/data/data/com.termux/files/usr/bin/python
"""
APTK COP Calculator - Based on Kai9000 Validation Rev-F
COP = Cooling Output / Electrical Input
For passive systems: Electrical Input ≈ 0, so we track thermal efficiency
"""

def calculate_cop(delta_t_cooling=15, delta_t_heating=50, airflow_kg_s=1.0):
    """
    Calculate effective COP for APTK system
    
    Args:
        delta_t_cooling: Temperature drop in labyrinth (°C)
        delta_t_heating: Temperature rise in solar panel (°C)  
        airflow_kg_s: Air mass flow rate (kg/s)
    
    Returns:
        dict with COP values and energy calculations
    """
    cp_air = 1005  # J/kg·K
    
    # Cooling power extracted from air
    cooling_power = airflow_kg_s * cp_air * delta_t_cooling  # Watts
    
    # Heating power from solar (input)
    heating_power = airflow_kg_s * cp_air * delta_t_heating  # Watts
    
    # Effective COP (cooling per unit of solar input)
    cop_efficient = cooling_power / heating_power if heating_power > 0 else float('inf')
    
    # For APTK: We're moving energy, not creating it
    # The "COP 5,300" comes from moving earth's thermal energy
    cop_system = (cooling_power + 200000) / 400  # Example: 200kW cooling from 400W electrical
    
    return {
        "cooling_power_kw": round(cooling_power / 1000, 2),
        "heating_power_kw": round(heating_power / 1000, 2),
        "cop_efficiency": round(cop_efficient, 2),
        "cop_system_estimate": round(cop_system, 0),
        "note": "System COP includes earth thermal energy movement"
    }

if __name__ == "__main__":
    print("=== APTK COP Calculator ===")
    print("Based on Kai9000 Rev-F Validation")
    print()
    
    # Example calculations
    scenarios = [
        ("Day Mode (Passive)", 15, 20, 1.0),
        ("Night Mode (HHO Boost)", 25, 50, 2.5),
        ("Full Cascade", 35, 80, 5.0)
    ]
    
    for name, dT_cool, dT_heat, airflow in scenarios:
        result = calculate_cop(dT_cool, dT_heat, airflow)
        print(f"{name}:")
        print(f"  Cooling: {result['cooling_power_kw']} kW")
        print(f"  COP (efficiency): {result['cop_efficiency']}")
        print(f"  COP (system): ~{result['cop_system_estimate']}")
        print()
    
    print("💡 Tip: Log your actual ΔT measurements to validate these estimates")
