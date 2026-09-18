def find_max_efficiency_change(variables):
    """variables = list of dicts. Each must have:
       'name': str, 'potential_gain': float (0-1), 'energy_form': str, 'leverage': float (system-wide multiplier)
    """
    if not variables:
        return {"error": "Provide at least one variable"}
    
    # Pure atomic: one max() over the coefficient (most efficient possible)
    best = max(
        variables,
        key=lambda v: v.get("potential_gain", 0) * v.get("leverage", 1.0)
    )
    
    eff_coeff = best["potential_gain"] * best.get("leverage", 1.0)
    
    return {
        "variable_to_change": best["name"],
        "recommended_energy_form_with_most_input": best["energy_form"],
        "efficiency_coefficient": round(eff_coeff, 4),
        "solution": f"Change '{best['name']}' and increase '{best['energy_form']}' energy input. This single action gives the highest overall system benefit per unit effort."
    }


# === YOUR AERO CEMENT / PoPW SYSTEM VARIABLES ===
# This is the simplest, most computationally efficient script possible that does what you asked:
# - Identifies which single variable change delivers the MOST overall system benefit
# - Tells you which energy form should receive the most input
# - Uses only atomic operations (one max + one multiply)
#
# HOW TO CUSTOMIZE (zero ongoing human input after this):
# 1. Edit the numbers below with your real measured/estimated values
# 2. potential_gain = realistic improvement possible (0.0–1.0)
# 3. leverage = how much the WHOLE system (thermal + mechanical + heating/cooling + capture) benefits
# 4. Add or remove dicts as needed — script stays O(1) fast
# 5. Re-run: python3 efficiency.py

your_variables = [
    {"name": "aerocement_porosity", "potential_gain": 0.85, "energy_form": "solar_thermal", "leverage": 2.2},  # TODO: replace with your measured value
    {"name": "stirling_conversion_efficiency", "potential_gain": 0.75, "energy_form": "mechanical", "leverage": 1.8},  # TODO: replace with your measured value
    {"name": "insulation_or_thermal_mass_performance", "potential_gain": 0.90, "energy_form": "thermal", "leverage": 1.5},  # TODO: replace with your measured value
    {"name": "solar_capture_area_or_absorptivity", "potential_gain": 0.95, "energy_form": "solar", "leverage": 3.0},  # TODO: replace with your measured value
    # Add more variables here anytime (example):
    # {"name": "activated_carbon_surface_area", "potential_gain": 0.80, "energy_form": "solar_thermal", "leverage": 2.5},
]

result = find_max_efficiency_change(your_variables)
print(result)
