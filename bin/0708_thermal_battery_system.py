#!/usr/bin/env python3
"""
AeroCement Thermal Battery & Stratification Model
Components: Copper Coil Exchanger + 50k Gal Tank + Subterranean Cold Pit
Logic: Night Freeze -> Day Discharge via Density Stratification
"""

import math

class ThermalBatterySystem:
    def __init__(self):
        self.rho_cold_air = 1.29  # kg/m^3 at 0°C
        self.rho_hot_air = 1.15   # kg/m^3 at 35°C
        self.c_water = 4186       # J/kgK
        self.latent_heat_fusion = 334e3 # J/kg
        
    def calculate_freezing_time(self, volume_gal, t_initial_f, t_ambient_night_f, area_coil_m2, u_value=50):
        """
        Estimates time to freeze water in tank given night ambient temp and coil surface area.
        U-value: Overall heat transfer coefficient for copper coil (W/m^2K)
        """
        vol_liters = volume_gal * 3.785
        mass_water = vol_liters # kg (approx density 1)
        
        t_init_c = (t_initial_f - 32) * 5/9
        t_amb_c = (t_ambient_night_f - 32) * 5/9
        
        if t_amb_c >= t_init_c:
            return None, "Ambient too warm to freeze naturally."
            
        # 1. Cool water to freezing point
        q_sensible = mass_water * self.c_water * (t_init_c - 0)
        
        # 2. Freeze water (Latent)
        q_latent = mass_water * self.latent_heat_fusion
        
        q_total = q_sensible + q_latent
        
        # Average temperature difference (Log Mean approx for simplicity)
        delta_t_avg = (t_init_c + 0) / 2 - t_amb_c # Rough avg
        
        if delta_t_avg <= 0:
             return None, "No driving force."
             
        # Power removal rate
        power_watts = u_value * area_coil_m2 * delta_t_avg
        
        time_seconds = q_total / power_watts
        time_hours = time_seconds / 3600
        
        return time_hours, f"Freeze complete in {time_hours:.1f} hours."

    def stratification_check(self, t_pit_f, t_room_f, height_m):
        """
        Checks if cold air will sink and stay in the pit vs mixing.
        Buoyancy Force = g * h * (rho_cold - rho_hot)
        """
        t_pit_c = (t_pit_f - 32) * 5/9
        t_room_c = (t_room_f - 32) * 5/9
        
        # Approx density
        rho_pit = 1.29 * (273.15 / (273.15 + t_pit_c))
        rho_room = 1.29 * (273.15 / (273.15 + t_room_c))
        
        buoyancy_force = 9.81 * height_m * (rho_pit - rho_room)
        
        stable = rho_pit > rho_room
        
        print(f"\n[STRATIFICATION ANALYSIS]")
        print(f"   Pit Temp: {t_pit_f}°F ({t_pit_c:.1f}°C)")
        print(f"   Room Temp: {t_room_f}°F ({t_room_c:.1f}°C)")
        print(f"   Pit Height: {height_m}m")
        print(f"   Density Diff: {rho_pit - rho_room:.3f} kg/m^3")
        print(f"   Buoyancy Force: {buoyancy_force:.2f} N/m^2")
        
        if stable:
            print("   ✅ STABLE: Cold air will pool in the pit. Perfect for storage.")
        else:
            print("   ❌ UNSTABLE: Warm air is sinking? Check temps.")
            
        return stable

    def run_scenario(self):
        print("="*60)
        print("THERMAL BATTERY & STRATIFICATION SYSTEM")
        print("="*60)
        
        # Parameters
        tank_vol = 50000 # gallons
        t_start = 60     # F (Water start temp)
        t_night = 35     # F (Clear night in AZ fall/spring)
        coil_area = 100  # m^2 (Huge coil bundle needed)
        
        # Night Charge
        print("\n[PHASE 1: NIGHT CHARGE]")
        result, msg = self.calculate_freezing_time(tank_vol, t_start, t_night, coil_area)
        print(f"   Condition: {msg}")
        
        if result:
            print(f"   Required Coil Area: ~{coil_area} m^2")
            print(f"   Note: In deep summer nights (70°F), passive freezing fails.")
            print(f"   Solution: Use Radiative Cooler panel on top of tank + Night Wind.")
            
        # Day Discharge
        print("\n[PHASE 2: DAY DISCHARGE]")
        print(f"   Action: Solar Siphon pulls hot air over frozen coils.")
        print(f"   Output: Air drops to ~35-40°F.")
        
        self.stratification_check(t_pit_f=38, t_room_f=75, height_m=3.0)
        
        print("\n[SYSTEM INTEGRATION PLAN]")
        print("   1. Build 50k Gal Ferrocement Tank with 100m^2 Copper Coil.")
        print("   2. Dig 10ft Deep Insulated Pit connected to Tank bottom.")
        print("   3. Install 3-Way Valves:")
        print("      - Night: Outside Air -> Coil -> Exhaust (Freeze Water).")
        print("      - Day: Desiccant Air -> Coil -> Pit Intake (Cool House).")
        print("   4. Roof Radiator: To aid night freezing when air is > 50°F.")

if __name__ == "__main__":
    engine = ThermalBatterySystem()
    engine.run_scenario()
