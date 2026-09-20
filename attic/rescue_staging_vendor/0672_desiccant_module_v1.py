#!/usr/bin/env python3
"""
AeroCement Desiccant Module v1.0 — "Dry Air Before Sponge"
CC-BY-SA Hardware | GPLv3 Software | No Patents
Mission: Ensure 0% RH at Sponge Inlet to Prevent Saturation.
"""

import math

class DesiccantEngine:
    def __init__(self):
        self.humidity_ratio_sat = 0.03 # kg water/kg air at 110°F, 100% RH
        self.target_rh = 0.0           # Target: 0% RH
        self.density_air = 1.2         # kg/m³
        
    def moisture_load(self, airflow_cfm, inlet_temp_f, inlet_rh):
        """
        Calculates total water vapor entering the system per day.
        Formula: Mass Flow * Humidity Ratio
        """
        # Convert CFM to kg/s
        mass_flow_kg_s = (airflow_cfm * 0.0283 / 60) * self.density_air
        
        # Estimate humidity ratio at 110F, RH%
        # Approximate saturation pressure, but using simplified ratio for now
        # At 110F (43C), Psat ~ 8.7 kPa. 
        # P_vapor = RH * Psat. 
        # W = 0.622 * Pv / (P - Pv) (Atm=101.3kPa)
        
        T_C = (inlet_temp_f - 32) * 5/9
        # Magnus formula for saturation vapor pressure (kPa)
        P_sat = 0.61094 * math.exp((17.625 * T_C) / (T_C + 243.04))
        P_vap = (inlet_rh / 100.0) * P_sat
        W_in = 0.622 * P_vap / (101.325 - P_vap) # kg water / kg dry air
        
        water_kg_s = mass_flow_kg_s * W_in
        water_kg_day = water_kg_s * 86400
        
        return water_kg_day, W_in

    def desiccant_size(self, water_load_kg, capacity_per_kg=0.20):
        """
        Calculates required mass of desiccant.
        Capacity: Typical silica gel/zeolite holds ~20% of its weight in water.
        Safety Factor: 2.0 (to ensure 0% RH breakthrough).
        """
        safety_factor = 2.0
        required_capacity = water_load_kg * safety_factor
        mass_desiccant_kg = required_capacity / capacity_per_kg
        volume_m3 = mass_desiccant_kg / 800 # Density of packed zeolite ~800kg/m3
        return mass_desiccant_kg, volume_m3

    def regeneration_check(self, heat_source_watts, duration_hrs, latent_heat_j=2260e3):
        """
        Checks if available heat can dry the desiccant overnight.
        Water removal energy = mass_water * Lv (plus sensible heat).
        """
        energy_available_j = heat_source_watts * duration_hrs * 3600
        water_can_remove_kg = energy_available_j / latent_heat_j
        return water_can_remove_kg

    def run_simulation(self):
        print("=" * 75)
        print("  AEROCMENT DESICCANT MODULE v1.0 — DRYING THE AIR")
        print("  Commander: Jesse McMillen | Priority: Prevent Sponge Saturation")
        print("=" * 75)

        # === SCENARIO: VILLAGE SCALE (1000 Homes) ===
        cfm_total = 2265864 # From previous Earth Loop calc
        t_inlet = 110       # °F
        rh_inlet = 40       # % (Typical desert midday, dry but not zero)
        
        # === STEP 1: The Moisture Problem ===
        print("\n[💧] PHASE 1: MOISTURE LOAD CALCULATION")
        print("-" * 40)
        water_kg_day, w_in = self.moisture_load(cfm_total, t_inlet, rh_inlet)
        print(f"  Total Airflow:      {cfm_total:,.0f} CFM")
        print(f"  Inlet Temp:         {t_inlet}°F @ {rh_inlet}% RH")
        print(f"  Water Vapor Input:  {water_kg_day:,.1f} kg/day ({water_kg_day/3.785:.1f} Gallons)")
        print(f"  ⚠️  WARNING: If NOT removed, this water saturates the sponge in < 2 hours.")

        # === STEP 2: Sizing the Desiccant Bed ===
        print("\n[🏗️] PHASE 2: DESICCANT BED SIZING")
        print("-" * 40)
        mass_dry, vol_dry = self.desiccant_size(water_kg_day)
        print(f"  Required Dry Mass:  {mass_dry:,.0f} kg (~{mass_dry/1000:.1f} Tonnes)")
        print(f"  Volume Required:    {vol_dry:.1f} m³")
        print(f"  Material:           Zeolite or Silica Gel (Regenerable)")
        print(f"  Form Factor:        Perforated trays or rotating wheel.")
        print(f"  ✅ VERDICT: Massive bed required. Integrate into Chimney Base.")

        # === STEP 3: Regeneration (The Night Cycle) ===
        print("\n[🔥] PHASE 3: NIGHT REGENERATION (Using Rocket Mass Heat)")
        print("-" * 40)
        # Assume RMH waste heat available at night: 10 kW thermal
        heat_avail_W = 10000 
        duration_night = 8
        
        water_removed = self.regeneration_check(heat_avail_W, duration_night)
        
        print(f"  Waste Heat Source:  Rocket Mass Heater (Night Mode)")
        print(f"  Available Power:    {heat_avail_W/1000} kW")
        print(f"  Duration:           {duration_night} hrs")
        print(f"  Water Can Remove:   {water_removed:,.1f} kg")
        
        if water_removed >= water_kg_day:
            print(f"  ✅ SUCCESS: System is fully regeneratable overnight.")
            print(f"     Strategy: Route RMH exhaust through desiccant tray.")
        else:
            deficit = water_kg_day - water_removed
            print(f"  ⚠️  DEFICIT: Cannot remove all moisture. Need more heat or smaller load.")
            print(f"     Shortfall: {deficit:,.1f} kg/day")
            print(f"     Solution: Increase chimney size OR use solar thermal collector for regen.")

        # === STEP 4: The Warrior's Protocol ===
        print("\n[📜] PHASE 4: WARRIOR'S DAILY PROTOCOL")
        print("-" * 40)
        print("""
  1. SUNRISE (06:00):
     - Check desiccant trays. Are they dry? (Color change indicator).
     - Open "Intake to Sponge" vents.
     - Close "Desiccant Regen" vents.
     
  2. NOON (Peak Sun):
     - Verify airflow draft (Smoke test at chimney base).
     - Monitor output temp (Target: < 60°F).
     
  3. SUNSET (18:00):
     - Switch flow: Divert hot air from Rocket Mass Heater THROUGH desiccant.
     - This bakes the water OUT of the bed.
     
  4. MIDNIGHT (00:00):
     - Check tank temp. Is it < 45°F?
     - Record "Proof of Dryness" to DAO ledger.
""")

        # === SUMMARY ===
        print("\n" + "=" * 75)
        print("  COMMANDER'S FINAL BRIEF — DESICCANT MODULE")
        print("=" * 75)
        print(f"""
  1. THE KEY TO SURVIVAL: DRY AIR.
     Without drying, the sponge becomes a swamp and stops cooling.
  
  2. THE SOLUTION:
     - Build a massive Zeolite bed (20+ tonnes).
     - Use the Rocket Mass Heater's night waste heat to "bake" it dry.
  
  3. THE CYCLE:
     Day: Dry air → Wet Sponge → Cold House.
     Night: Hot Air → Wet Desiccant → Dry Bed.
  
  4. NEXT ACTION:
     - Draft the "Zeolite Bed Construction Guide" (CC-BY-SA).
     - Design the "Vent Switching Flapper" (Passive bi-metal or manual lever).
     - Hash this module to Arweave.

  "Dry air is the silent warrior. It carries the cold without drowning."
""")

if __name__ == "__main__":
    DesiccantEngine().run_simulation()
