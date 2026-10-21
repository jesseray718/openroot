#!/usr/bin/env python3
"""
AeroCement Integrated Energy Triad v1.0
Mission: Simultaneous Heat Banking, Cold Banking, Water Harvesting, & Power Generation.
License: CC-BY-SA Hardware | GPLv3 Software
No Patents. Open Source.
Educational Purpose: Demonstrates energy balance in a closed-loop thermal system.
Shows how water harvesting (latent heat) competes with electricity generation.
"""

import math

class TriadEngine:
    def __init__(self):
        self.latent_heat_water_j_kg = 2260e3
        self.density_air = 1.2
        self.teg_efficiency = 0.05
        self.stirling_efficiency = 0.15

    def calculate_mass_flow(self, cfm):
        return (cfm * 0.0283 / 60) * self.density_air

    def get_vapor_content(self, temp_f, rh_percent):
        T_C = (temp_f - 32) * 5/9
        P_sat = 0.61094 * math.exp((17.625 * T_C) / (T_C + 243.04))
        P_vap = (rh_percent / 100.0) * P_sat
        W = 0.622 * P_vap / (101.325 - P_vap)
        return W

    def run_triad_simulation(self):
        print("=" * 80)
        print("  AEROCMENT INTEGRATED TRIAD ENGINE v1.0")
        print("  Strategy: Heat -> Water -> Mech -> Electric")
        print("=" * 80)

        cfm_total = 2265864
        inlet_temp_f = 110
        inlet_rh = 40
        heat_input_watts = 5e6
        duration_hrs = 8

        mass_flow = self.calculate_mass_flow(cfm_total)
        water_ratio_in = self.get_vapor_content(inlet_temp_f, inlet_rh)
        water_kg_day = mass_flow * water_ratio_in * 86400
        water_gal_day = water_kg_day / 3.785

        print("\n[💧] PHASE 1: ATMOSPHERIC WATER HARVESTING")
        print("-" * 40)
        print(f"  Airflow: {cfm_total:,.0f} CFM")
        print(f"  Water Vapor Input: {water_kg_day:,.0f} kg/day ({water_gal_day:,.0f} Gallons)")
        print(f"  ⚠️  NOTE: This is the amount of water we MUST evaporate to dry the bed.")

        print("\n[🔥] PHASE 2: THERMAL TO MECHANICAL/ELECTRIC")
        print("-" * 40)

        total_energy_j = heat_input_watts * duration_hrs * 3600
        energy_for_evap_j = water_kg_day * self.latent_heat_water_j_kg

        print(f"  Total Heat Injected: {heat_input_watts/1e6:.1f} MW × {duration_hrs} hrs")
        print(f"  Total Energy Available: {total_energy_j/1e9:.1f} GJ")
        print(f"  Energy Needed to Evaporate Water: {energy_for_evap_j/1e9:.1f} GJ")

        remaining_heat_j = total_energy_j - energy_for_evap_j

        if remaining_heat_j > 0:
            print(f"  ✅ Surplus Heat Available: {remaining_heat_j/1e9:.2f} GJ")
            teg_elec_j = remaining_heat_j * self.teg_efficiency
            teg_kwh = teg_elec_j / 3.6e6
            stirling_elec_j = remaining_heat_j * (1 - self.teg_efficiency) * self.stirling_efficiency
            stirling_kwh = stirling_elec_j / 3.6e6
            total_elec_kwh = teg_kwh + stirling_kwh
            print(f"  [⚡] TEG Output: {teg_kwh:,.0f} kWh/day")
            print(f"  [⚙️] Stirling Output: {stirling_kwh:,.0f} kWh/day")
            print(f"  💰 TOTAL ELECTRICITY GENERATED: {total_elec_kwh:,.0f} kWh/day")
            elec_status = "SUCCESS"
            elec_value = total_elec_kwh
        else:
            deficit = abs(remaining_heat_j)
            print(f"  ⚠️  DEFICIT DETECTED: All heat consumed by evaporation.")
            print(f"     Shortfall: {deficit/1e9:.1f} GJ")
            print(f"     To close gap: Need {deficit / (heat_input_watts * 3600):.0f} more hours @ {heat_input_watts/1e6:.0f}MW")
            total_elec_kwh = 0
            elec_status = "DEFICIT"
            elec_value = 0

        print("\n[❄️] PHASE 3: COLD BANK & CONDENSATION")
        print("-" * 40)
        print(f"  Strategy: Use Cold Bank to condense wet exhaust AFTER power gen.")
        print(f"  Result: Capture 100% of harvested water.")

        print("\n" + "=" * 80)
        print("  COMMANDER'S SUMMARY")
        print("=" * 80)
        print(f"""
   RESOURCE          │ OUTPUT                    │ STATUS
   ──────────────────┼───────────────────────────┼──────────
   Water Harvested   │ {water_gal_day:,.0f} Gal/Day    │ 💧 HARVESTED
   Electricity       │ {elec_value:,.0f} kWh/Day   │ {'⚡ GENERATED' if elec_status=='SUCCESS' else '⚠️ DEFICIT'}

   LEARNING POINT:
   At Village Scale (1000 homes), the water load is massive.
   The latent heat required to dry the bed consumes ALL available thermal input.
   ACTIONABLE INSIGHT: Scale Down to Single-Home Prototype first.
""")
        print('   "The water IS the resource. The heat IS the engine."')

if __name__ == "__main__":
    TriadEngine().run_triad_simulation()
