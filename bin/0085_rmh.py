import json, math

# Rocket Mass Heater + Molten Salt Thermal Storage Vehicle Model
# FIXED: Correctly calculates net power and range considering continuous input

T_hot = 538 + 273.15  # molten salt max temp (K)
T_cold = 293.15       # ambient (K)
stirling_eff = 0.35
gen_eff = 0.92
motor_eff = 0.90
salt_cp = 1530        # J/(kg·K)
salt_mass = 150       # kg
black_locust_LHV = 19.5e6  # J/kg
burn_rate = 2.5       # kg/h
rmh_eff = 0.85

# Carnot ceiling
carnot = 1 - (T_cold / T_hot)

# Energy in salt reservoir
dT = T_hot - T_cold
salt_energy = salt_mass * salt_cp * dT

# RMH Thermal Input (Watts)
rmh_thermal_power = burn_rate * black_locust_LHV * rmh_eff / 3600

# Wheel Power Output (Watts)
stirling_shaft = rmh_thermal_power * stirling_eff
wheel_power = stirling_shaft * gen_eff * motor_eff

# Demand
avg_draw = 5000  # Watts

# Net Power (Positive = Charging, Negative = Discharging)
net_power = wheel_power - avg_draw

# Range Calculation
if net_power >= 0:
    range_hours = float('inf')
    status = "Self-Sustaining (Net Positive)"
else:
    # Time until salt depletes covering the deficit
    deficit = abs(net_power)
    range_hours = salt_energy / (deficit * 3600)
    status = f"Deficit Mode ({deficit:.0f}W drain)"

results = {
    "carnot_ceiling": round(carnot * 100, 2),
    "rmh_thermal_kw": round(rmh_thermal_power / 1000, 2),
    "stirling_shaft_kw": round(stirling_shaft / 1000, 2),
    "wheel_power_kw": round(wheel_power / 1000, 2),
    "avg_draw_kw": round(avg_draw / 1000, 2),
    "net_power_kw": round(net_power / 1000, 2),
    "salt_storage_kwh": round(salt_energy / 3.6e6, 2),
    "est_range_hours": round(range_hours, 2) if range_hours != float('inf') else "INF",
    "status": status,
    "fuel_carbon_status": "carbon-negative (coppice roots sequester)"
}

print(json.dumps(results, indent=2))
# Try to save to openroot, fallback to local dir
try:
    with open("/data/data/com.termux/files/home/openroot/rmh_results.json", "w") as f:
        json.dump(results, f, indent=2)
except:
    with open("rmh_results.json", "w") as f:
        json.dump(results, f, indent=2)