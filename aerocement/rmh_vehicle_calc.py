import json
import math

"""
Rocket Mass Heater Vehicle Calculator - Validated Config Comparison
Based on CHP analysis: Flue-coupling (600°C) delivers 3.1x electricity vs tank-coupling (82°C)
"""

def calculate_config(fuel_kg_day, mode='flue'):
    """Calculate outputs for given wood fuel and coupling mode"""
    
    # Fuel properties (black locust dry)
    LHV = 19.5e6  # J/kg
    
    # Validation parameters from CHP analysis
    if mode == 'tank':
        carnot = 0.217          # 82°C hot side
        stirling_real_eff = 0.087
        wood_to_elec = 0.065
        wood_to_heat = 0.683
        chimney_loss = 0.252
        hot_side_K = 82 + 273.15
        
    elif mode == 'flue':
        carnot = 0.681          # 600°C hot side
        stirling_real_eff = 0.273
        wood_to_elec = 0.204
        wood_to_heat = 0.544
        chimney_loss = 0.252
        hot_side_K = 600 + 273.15
        
    elif mode == 'molten_salt':
        # Your vehicle spec: 538°C molten salt
        carnot = 1 - (293.15 / (538 + 273.15))  # 63% theoretical
        stirling_real_eff = 0.35                # Optimistic but achievable
        wood_to_elec = 0.30                     # Target with optimized Stirling
        wood_to_heat = 0.45                     # Lower, more heat→electricity
        chimney_loss = 0.25
        hot_side_K = 538 + 273.15
    else:
        raise ValueError("mode must be 'tank', 'flue', or 'molten_salt'")
    
    # Daily energy flows
    thermal_input_J = fuel_kg_day * LHV
    thermal_input_kWh = thermal_input_J / 3.6e6
    
    elec_kWh = thermal_input_kWh * wood_to_elec
    heat_kWh = thermal_input_kWh * wood_to_heat
    loss_kWh = thermal_input_kWh * chimney_loss
    
    return {
        "mode": mode,
        "hot_side_C": hot_side_K - 273.15,
        "carnot_ceiling_pct": round(carnot * 100, 1),
        "stirling_real_eff_pct": round(stirling_real_eff * 100, 1),
        "wood_kg_day": round(fuel_kg_day, 2),
        "thermal_input_kWh_day": round(thermal_input_kWh, 2),
        "electricity_kWh_day": round(elec_kWh, 2),
        "useful_heat_kWh_day": round(heat_kWh, 2),
        "loss_kWh_day": round(loss_kWh, 2),
        "efficiency_chain": f"{round(wood_to_elec*100,1)}% → electric, {round(wood_to_heat*100,1)}% → heat"
    }

def calculate_vehicle_range(elec_kWh_day, salt_mass_kg=150, mode='molten_salt'):
    """Estimate vehicle range from daily electricity generation"""
    
    # Battery conversion (electrical energy stored in salt)
    salt_cp = 1530  # J/(kg·K)
    delta_T = (538 - 20) if mode == 'molten_salt' else (600 - 20)  # K
    
    salt_energy_J = salt_mass_kg * salt_cp * delta_T
    salt_energy_kWh = salt_energy_J / 3.6e6
    
    # Drivetrain
    gen_eff = 0.92
    motor_eff = 0.90
    drivetrain_eff = gen_eff * motor_eff
    
    # Assume 5kW avg draw at wheels for 45km/h cruising
    wheel_power_W = 5000
    speed_kmh = 45
    
    # Range calculation
    usable_elec_kWh = elec_kWh_day * drivetrain_eff
    drive_time_hr = usable_elec_kWh / (wheel_power_W / 1000)
    range_km = drive_time_hr * speed_kmh
    
    return {
        "salt_storage_kWh": round(salt_energy_kWh, 2),
        "usable_elec_kWh": round(usable_elec_kWh, 2),
        "drive_time_hours": round(drive_time_hr, 2),
        "range_km": round(range_km, 1),
        "avg_speed_kmh": speed_kmh,
        "avg_wheel_power_W": wheel_power_W
    }

def compare_configs(fuel_kg_day):
    """Compare all three coupling modes"""
    
    print("=" * 60)
    print("ROCKET MASS HEATER VEHICLE CONFIG COMPARISON")
    print("=" * 60)
    
    results = []
    
    for mode in ['tank', 'flue', 'molten_salt']:
        calc = calculate_config(fuel_kg_day, mode)
        veh = calculate_vehicle_range(calc['electricity_kWh_day'], mode=mode)
        
        merged = {**calc, **veh}
        results.append(merged)
        
        print(f"\n[{mode.upper()}] T={merged['hot_side_C']}°C")
        print(f"  Wood: {merged['wood_kg_day']} kg/day → {merged['efficiency_chain']}")
        print(f"  Carnot: {merged['carnot_ceiling_pct']}% | Real Stirling: {merged['stirling_real_eff_pct']}%")
        print(f"  Electric: {merged['electricity_kWh_day']} kWh/day | Heat: {merged['useful_heat_kWh_day']} kWh/day")
        print(f"  Salt Storage: {merged['salt_storage_kWh']} kWh | Range: {merged['range_km']} km")
        
        if mode != 'tank':
            ratio = results[-1]['electricity_kWh_day'] / results[0]['electricity_kWh_day']
            print(f"  >>> vs tank-coupled: {ratio:.1f}x MORE ELECTRICITY")
            
        print("-" * 60)
    
    return results

def main():
    """Interactive calculator"""
    
    import argparse
    parser = argparse.ArgumentParser(description="RMH Vehicle Power Calculator")
    parser.add_argument('--fuel', type=float, default=24.5, help='Wood burn rate kg/day')
    parser.add_argument('--compare', action='store_true', help='Compare all configs')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if args.compare:
        results = compare_configs(args.fuel)
        
        if args.json:
            print(json.dumps({
                "fuel_kg_day": args.fuel,
                "configs": results,
                "recommendation": "FLUE-COUPLED or MOLTEN_SALT - 3.1x electricity over tank-coupled"
            }, indent=2))
        
    else:
        # Default: show recommended config (flue/molten salt)
        calc = calculate_config(args.fuel, 'flue')
        veh = calculate_vehicle_range(calc['electricity_kWh_day'])
        
        output = {**calc, **veh}
        
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(output, indent=2))
    
    # Auto-copy to clipboard
    output_json = json.dumps(results if args.compare else calc, indent=2)
    try:
        subprocess.run(['echo', output_json, '|', 'termux-clipboard-set'], shell=True)
        print("\n>>> Results copied to clipboard")
    except:
        pass

if __name__ == '__main__':
    main()
