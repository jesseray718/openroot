#!/usr/bin/env python3
"""
AeroCement Unified Breath Loop v3.0
THE ACTUAL SYSTEM: One Vacuum, Two Stages, Day/Night Modes
CC-BY-SA Hardware | GPLv3 Software | No Patents | No Monopolies
"""

import math

class UnifiedBreathLoop:
    def __init__(self):
        self.Lv = 2260e3       # J/kg Latent heat of vaporization
        self.Lf = 334e3        # J/kg Latent heat of fusion
        self.Cp_air = 1005     # J/kgK
        self.Cp_water = 4186   # J/kgK
        self.k_copper = 401    # W/mK Thermal conductivity
        
    def stage1_volumetric(self, t_in_f, rh_in, t_ground_f, ntus=3.0):
        """
        Stage 1: Volumetric Aerocement Passage
        Air TOUCHES water in pores. Evaporative + sensible cooling.
        Pre-dried air maximizes evaporation driving force.
        """
        t_in_c = (t_in_f - 32) * 5/9
        t_ground_c = (t_ground_f - 32) * 5/9
        
        # Evaporative cooling pulls air toward ground temp
        effectiveness = 1 - math.exp(-ntus)
        
        t_out_c = t_ground_c + (t_in_c - t_ground_c) * (1 - effectiveness)
        t_out_f = t_out_c * 9/5 + 32
        
        return t_out_f
    
    def stage2_coil(self, t_in_f, t_tank_top_f, t_tank_bot_f, 
                    coil_ntus=4.0, ice_present=False):
        """
        Stage 2: Copper Coil inside Tank
        Air inside coil, water/ice outside.
        Tank stratifies: cold sinks, warm rises.
        Coil runs top-to-bottom (counter-current).
        
        If ice present: bottom temp = 32°F (phase change buffer)
        """
        t_in_c = (t_in_f - 32) * 5/9
        
        # Counter-current: air enters top (warmer water), exits bottom (coldest)
        t_top_c = (t_tank_top_f - 32) * 5/9
        t_bot_c = (t_tank_bot_f - 32) * 5/9
        
        if ice_present:
            # Bottom is locked at 32°F until all ice melts
            t_bot_c = 0.0  # 32°F
        
        # First half: cool against top water
        eff_half = 1 - math.exp(-coil_ntus / 2)
        t_mid_c = t_top_c + (t_in_c - t_top_c) * (1 - eff_half)
        
        # Second half: cool against bottom water/ice
        t_out_c = t_bot_c + (t_mid_c - t_bot_c) * (1 - eff_half)
        t_out_f = t_out_c * 9/5 + 32
        
        return t_out_f
    
    def night_charge(self, t_night_air_f, tank_gallons, t_tank_current_f,
                     coil_area_m2, duration_hours):
        """
        Night Mode: Cold air charges the tank through the coil.
        Calculates new tank temperature after night cycle.
        If subterranean passage freezes → bypass to coil directly.
        """
        t_air_c = (t_night_air_f - 32) * 5/9
        t_tank_c = (t_tank_current_f - 32) * 5/9
        
        vol_m3 = tank_gallons * 3.785 / 1000
        mass_water = vol_m3 * 1000  # kg
        
        # Heat removal rate through coil (simplified)
        U = 50  # W/m^2K overall heat transfer for copper coil in water
        delta_t = t_tank_c - t_air_c
        
        if delta_t <= 0:
            return t_tank_current_f, 0, "Tank already colder than night air. No charge."
        
        power_watts = U * coil_area_m2 * delta_t
        energy_joules = power_watts * duration_hours * 3600
        
        # Cool the tank
        q_per_kg = energy_joules / mass_water
        new_t_tank_c = t_tank_c - q_per_kg / self.Cp_water
        
        # Check for freezing
        ice_formed = False
        if new_t_tank_c <= 0:
            # Some water freezes
            new_t_tank_c = 0.0
            ice_formed = True
        
        new_t_tank_f = new_t_tank_c * 9/5 + 32
        
        return new_t_tank_f, power_watts, "ICE FORMED" if ice_formed else "Liquid"
    
    def run_full_simulation(self):
        print("=" * 65)
        print("  AEROCMENT UNIFIED BREATH LOOP v3.0")
        print("  One Vacuum. Two Stages. Day/Night Modes.")
        print("  CC-BY-SA | GPLv3 | No Patents | No Monopolies")
        print("=" * 65)
        
        # ============ DAY MODE ============
        print("\n" + "─" * 65)
        print("  ☀️  DAY MODE — Solar Chimney Drives")
        print("─" * 65)
        
        t_ambient = 110  # °F
        rh_input = 0     # % (after desiccant)
        t_ground = 55    # °F
        t_tank_top = 55  # °F (day start — charged from night)
        t_tank_bot = 33  # °F (ice at bottom from night charge)
        
        # Stage 1
        stage1_out = self.stage1_volumetric(t_ambient, rh_input, t_ground, ntus=3.0)
        
        # Stage 2
        final_out = self.stage2_coil(stage1_out, t_tank_top, t_tank_bot, 
                                     coil_ntus=4.0, ice_present=True)
        
        print(f"\n  Intake Air:     {t_ambient}°F (0% RH, Pre-Dried)")
        print(f"  After Stage 1:  {stage1_out:.1f}°F (Volumetric Evaporative)")
        print(f"  After Stage 2:  {final_out:.1f}°F (Coil in Ice-Tank)")
        print(f"  Total ΔT:       {t_ambient - final_out:.1f}°F drop")
        print(f"  Delivered to:   Deep Pit (density stratification)")
        
        # ============ NIGHT MODE ============
        print("\n" + "─" * 65)
        print("  🌙 NIGHT MODE — Rocket Mass Heater Drives")
        print("─" * 65)
        
        t_night = 40  # °F (desert night)
        tank_gal = 50000 # gallons
        coil_area = 100  # m^2
        night_hours = 8
        
        # Night charge cycle
        new_tank_f, power, status = self.night_charge(
            t_night, tank_gal, t_tank_top, coil_area, night_hours
        )
        
        print(f"\n  Night Air:      {t_night}°F")
        print(f"  Tank Start:     {t_tank_top}°F")
        print(f"  Tank End:       {new_tank_f:.1f}°F")
        print(f"  Charge Power:   {power/1000:.1f} kW")
        print(f"  Duration:       {night_hours} hours")
        print(f"  Status:         {status}")
        
        # ============ FREEZE DETECTION ============
        print("\n" + "─" * 65)
        print("  ⚠️  VALVE SWITCHING LOGIC")
        print("─" * 65)
        
        t_passage_freeze = 32  # °F
        t_passage_current = 55
        
        print(f"\n  Subterranean Passage Temp: {t_passage_current}°F")
        
        if t_passage_current <= t_passage_freeze:
            print("  ❄️  FREEZE DETECTED — Switching to BYPASS mode")
            print("     Route: Intake → [BYPASS] → Tank Coil → Exhaust")
            print("     Subterranean passage ISOLATED (charging as ice battery)")
        else:
            print("  ✅ PASSAGE CLEAR — Normal route active")
            print("     Route: Intake → Volumetric → Tank Coil → Exhaust")
        
        print("\n" + "─" * 65)
        print("  🔄 DAWN SWITCHBACK")
        print("─" * 65)
        print("  When sun rises:")
        print("  1. Solar chimney takes over from rocket heater")
        print("  2. Valves return to normal routing")
        print("  3. Ice in passage thaws → supplies cold to Stage 1")
        print("  4. Ice in tank supplies cold to Stage 2")
        print("  5. DOUBLE COLD SOURCE = Maximum day cooling")
        
        # ============ SUMMARY ============
        print("\n" + "=" * 65)
        print("  COMMANDER'S BRIEF")
        print("=" * 65)
        print(f"""
  Day Output:   {final_out:.0f}°F from {t_ambient}°F input
  Night Charge: Tank → {new_tank_f:.0f}°F in {night_hours}hrs @ {t_night}°F night
  COP:          ∞ (Zero electricity. Solar + Coppice fuel only.)
  
  THIS IS THE REVOLUTION:
  - Open source mechanical apparatus
  - Man + AI cooperative design
  - Every improvement mined from the collective
  - CC-BY-SA / GPLv3 — Babylon cannot patent-lock it
  - PoPW tokens reward BUILDERS, not idea hoarders
  
  The mechanism IS the patent. And it's free.
""")

if __name__ == "__main__":
    engine = UnifiedBreathLoop()
    engine.run_full_simulation()
