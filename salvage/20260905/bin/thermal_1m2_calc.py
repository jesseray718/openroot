#!/usr/bin/env python3
"""
OPENROOT THERMAL CASCADE — 1 m² TILE SYSTEM CALCULATOR
DV.GEN.TH.AE01 — Complete system: Panel → Labyrinth → Cold Battery → TEG → RMH

Corrected parameters:
- AE-GFRC cure: 1-2 days (not 21)
- AR-glass fiber: ≥20% ZrO₂
- Blackbody: activated charcoal in open-cell aerocement
- Cold battery: ferrocement water tank + copper coil
"""

import math

# ═══════════════════════════════════════════════════════════════
# SOLAR PANEL — 1 m² VOLUMETRIC OPEN-CELL AEROCEMENT
# ═══════════════════════════════════════════════════════════════
panel_area = 1.0  # m²
solar_irradiance_peak = 1000  # W/m²
solar_daily_july = 6.5  # kWh/m²/day (Sikeston, MO summer avg)
absorption_efficiency = 0.95  # activated charcoal blackbody

daily_solar_captured = solar_daily_july * absorption_efficiency  # kWh/day
daily_solar_j = daily_solar_captured * 3_600_000  # joules

# Panel airflow (estimated for 1 m²)
air_density_hot = 1.0  # kg/m³ at ~70°C
air_specific_heat = 1.005  # kJ/kg·K
airflow_rate = 0.05  # m³/s (conservative for 1 m² panel)
mass_flow = airflow_rate * air_density_hot  # kg/s

# Temperature rise in panel
panel_inlet_temp = 32  # °C (summer ambient, Sikeston MO)
# Energy balance: Q = m_dot × cp × ΔT
# daily_solar_captured (kWh) over 8 sun hours = avg power
avg_power_w = (daily_solar_captured / 8) * 1000  # watts average over 8 hours
delta_t_panel = avg_power_w / (mass_flow * air_specific_heat * 1000)  # °C
panel_outlet_temp = panel_inlet_temp + delta_t_panel

print("═" * 60)
print("  1 m² THERMAL CASCADE — TILE SYSTEM (DV.GEN.TH.AE01)")
print("═" * 60)
print()
print("  ┌─ SOLAR PANEL ─────────────────────────────────────┐")
print(f"  │ Area:              {panel_area} m²")
print(f"  │ July daily solar:  {solar_daily_july} kWh/m²/day")
print(f"  │ Absorption:        {absorption_efficiency*100}% (activated charcoal)")
print(f"  │ Daily capture:      {daily_solar_captured:.2f} kWh ({daily_solar_j/1e6:.2f} MJ)")
print(f"  │ Avg power (8hr):    {avg_power_w:.1f} W")
print(f"  │ Airflow:            {airflow_rate} m³/s ({airflow_rate*3600:.0f} m³/hr)")
print(f"  │ Panel inlet:        {panel_inlet_temp}°C ({panel_inlet_temp*9/5+32:.0f}°F)")
print(f"  │ Panel outlet:       {panel_outlet_temp:.1f}°C ({panel_outlet_temp*9/5+32:.0f}°F)")
print(f"  │ ΔT across panel:    {delta_t_panel:.1f}°C")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# LABYRINTH — UNDERGROUND OPEN-CELL CONCRETE HEAT EXCHANGER
# ═══════════════════════════════════════════════════════════════
# Air enters hot, transfers heat to thermal mass, exits cooler
labyrinth_exit_temp = 35  # °C target exit (ambient + 3°C)
labyrinth_delta_t = panel_outlet_temp - labyrinth_exit_temp  # heat extracted

# Thermal mass: open-cell concrete + earth
concrete_specific_heat = 0.88  # kJ/kg·K
concrete_density = 400  # kg/m³ (aerated open-cell)
earth_specific_heat = 1.5  # kJ/kg·K (mixed soil)
earth_density = 1500  # kg/m³

# Total heat to absorb daily
heat_to_absorb_kj = daily_solar_captured * 3600  # kJ

# Labyrinth volume calculation
# Assume 15°C temp rise in thermal mass (absorbs heat gradually)
temp_rise_mass = 15  # °C
# Mix of concrete structure + surrounding earth
# Assume 70% earth, 30% concrete by mass
effective_heat_cap = 0.7 * earth_specific_heat * earth_density + 0.3 * concrete_specific_heat * concrete_density
# kJ/m³/K
labyrinth_volume = heat_to_absorb_kj / (effective_heat_cap * temp_rise_mass)

# Labyrinth dimensions (buried trench, rectangular)
trench_depth = 1.0  # m
trench_width = 0.5  # m
labyrinth_length = labyrinth_volume / (trench_depth * trench_width)

print("  ┌─ LABYRINTH (underground heat exchanger) ───────────┐")
print(f"  │ Inlet temp:         {panel_outlet_temp:.1f}°C ({panel_outlet_temp*9/5+32:.0f}°F)")
print(f"  │ Exit temp target:   {labyrinth_exit_temp}°C ({labyrinth_exit_temp*9/5+32:.0f}°F)")
print(f"  │ Heat extracted:     {labyrinth_delta_t:.1f}°C drop")
print(f"  │ Daily heat stored:  {daily_solar_captured:.2f} kWh ({heat_to_absorb_kj/1000:.1f} MJ)")
print(f"  │ Thermal mass ΔT:    {temp_rise_mass}°C rise over day")
print(f"  │ Effective heat cap: {effective_heat_cap:.0f} kJ/m³/K")
print(f"  │ Labyrinth volume:  {labyrinth_volume:.3f} m³")
print(f"  │ Dimensions:         {labyrinth_length:.2f}m L × {trench_width}m W × {trench_depth}m D")
print(f"  │ Length needed:     {labyrinth_length:.2f} m of trench")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# COLD BATTERY — FERROCEMENT WATER TANK + COPPER COIL
# ═══════════════════════════════════════════════════════════════
# Charged at night via radiative cooling (panel emits IR to deep space)
# Water stores cold BTUs, copper coil circulates air through cold water

# Radiative cooling: panel emits to 3K deep space at night
# Conservative estimate (Claude flagged 12.91 kWh/m² as ~10x too high)
# Using conservative: ~1.3 kWh/m²/night (10x reduction from H-003 claim)
nightly_radiative_conservative = 1.3  # kWh/m²/night
nightly_radiative_claim = 12.91  # original H-003 claim (flagged)
nightly_cold_kj = nightly_radiative_conservative * 3600  # kJ

# Cold battery target: 5°C (above freezing, safe for water)
cold_target = 5  # °C
ambient_night = 25  # °C (summer night, Sikeston)
cold_delta = ambient_night - cold_target  # 20°C

# Water: highest specific heat of common materials
water_specific_heat = 4.186  # kJ/kg·K
water_density = 1000  # kg/m³

# Mass of water needed
water_mass = nightly_cold_kj / (water_specific_heat * cold_delta)
water_volume_liters = water_mass  # 1 kg = 1 L water

# Tank dimensions (ferrocement cylinder)
tank_radius = 0.2  # m (20 cm)
tank_height = water_mass / (math.pi * tank_radius**2 * water_density)

# Copper coil sizing
copper_tube_dia = 0.0127  # m (1/2 inch)
coil_length = 3.0  # m (estimated for heat exchange)
coil_surface_area = math.pi * copper_tube_dia * coil_length

print("  ┌─ COLD BATTERY (ferrocement tank + copper coil) ─────┐")
print(f"  │ Charging:          Radiative cooling at night")
print(f"  │ Nightly cold gen:  {nightly_radiative_conservative} kWh (conservative)")
print(f"  │ Original H-003:    {nightly_radiative_claim} kWh (FLAGGED ~10x high)")
print(f"  │ Ambient night:     {ambient_night}°C ({ambient_night*9/5+32:.0f}°F)")
print(f"  │ Cold target:       {cold_target}°C ({cold_target*9/5+32:.0f}°F)")
print(f"  │ Cold ΔT:           {cold_delta}°C storage range")
print(f"  │ Water mass:        {water_mass:.1f} kg ({water_volume_liters:.1f} L)")
print(f"  │ Tank:              ferrocement, {tank_radius*100:.0f}cm radius, {tank_height:.2f}m tall")
print(f"  │ Copper coil:       ½\" tube, {coil_length}m length, {coil_surface_area:.3f} m² area")
print(f"  │ Storage:           {nightly_cold_kj/1000:.1f} MJ cold capacity")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# THERMOELECTRIC GENERATOR (TEG)
# ═══════════════════════════════════════════════════════════════
# Hot side: solar-heated air from labyrinth (35°C) or RMH exhaust
# Cold side: cold battery water (5°C)
# During day: ΔT = 35°C - 5°C = 30°C (modest)
# With RMH: ΔT = 200°C+ (RMH exhaust) - 5°C = 195°C

teg_hot_solar = labyrinth_exit_temp  # 35°C from labyrinth
teg_hot_rmh = 200  # °C RMH exhaust (conservative)
teg_cold = cold_target  # 5°C from cold battery

delta_t_solar = teg_hot_solar - teg_cold
delta_t_rmh = teg_hot_rmh - teg_cold

# Typical TEG module specs (TEG1-12611-6.0 or similar)
teg_module_power_50k = 5  # W at ΔT=50°C
teg_module_efficiency = 0.05  # 5% typical

# Scale power with ΔT (roughly linear for small ΔT, sub-linear for large)
teg_power_solar = teg_module_power_50k * (delta_t_solar / 50)
teg_power_rmh = teg_module_power_50k * (delta_t_rmh / 50)

# Daily energy from TEG — 24 HOUR OPERATION (modular: solar OR RMH)
teg_hours_solar = 8    # daytime solar mode
teg_hours_rmh = 1.5    # evening/night RMH burn
teg_hours_residual = 24 - teg_hours_solar - teg_hours_rmh  # residual ΔT from stored heat
teg_power_residual = teg_module_power_50k * (30 / 50)  # ~3W from residual labyrinth heat
teg_daily_solar = teg_power_solar * teg_hours_solar / 1000
teg_daily_rmh = teg_power_rmh * teg_hours_rmh / 1000
teg_daily_residual = teg_power_residual * teg_hours_residual / 1000
teg_daily_total = teg_daily_solar + teg_daily_rmh + teg_daily_residual

print("  ┌─ THERMOELECTRIC GENERATOR ──────────────────────────┐")
print(f"  │ Solar mode:        Hot={teg_hot_solar}°C, Cold={teg_cold}°C, ΔT={delta_t_solar}°C")
print(f"  │   Power:           {teg_power_solar:.1f} W → {teg_daily_solar:.4f} kWh/day ({teg_hours_solar}hr)")
print(f"  │ RMH mode:          Hot={teg_hot_rmh}°C, Cold={teg_cold}°C, ΔT={delta_t_rmh}°C")
print(f"  │   Power:           {teg_power_rmh:.1f} W → {teg_daily_rmh:.3f} kWh/day ({teg_hours_rmh}hr)")
print(f"  │ Solar mode:        {teg_power_solar:.1f} W → {teg_daily_solar:.4f} kWh/day ({teg_hours_solar}hr)")
print(f"  │ RMH mode:          {teg_power_rmh:.1f} W → {teg_daily_rmh:.3f} kWh/day ({teg_hours_rmh}hr)")
print(f"  │ Residual mode:     {teg_power_residual:.1f} W → {teg_daily_residual:.4f} kWh/day ({teg_hours_residual}hr)")
print(f"  │ 24hr combined:    {teg_daily_total:.4f} kWh ({teg_daily_total*3600:.0f} kJ)")
print(f"  │ Modules needed:    1 (proof of concept)")
print(f"  │ Est. cost:         $15-30 per TEG module")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# ROCKET MASS HEATER (RMH) — 2 SYSTEMS
# ═══════════════════════════════════════════════════════════════
# Small RMH for 1 m² system: 4-inch system
rmh_diameter = 0.1  # 4 inches = 0.1m (internal)
rmh_height = 0.8  # 0.8m combustion unit height
rmh_thermal_output = 8  # kW (typical 4" RMH)
rmh_burn_time = 1.5  # hours per firing
rmh_daily_energy = rmh_thermal_output * rmh_burn_time  # kWh per firing

# Thermal mass (cob bench or stone) to store RMH heat
rmh_mass_specific_heat = 0.88  # kJ/kg·K (cob/stone)
rmh_mass_temp_rise = 30  # °C
rmh_mass_needed = (rmh_daily_energy * 3600) / (rmh_mass_specific_heat * rmh_mass_temp_rise)

# 2 RMHs
rmh_count = 2
rmh_total_daily = rmh_daily_energy * rmh_count
rmh_total_mass = rmh_mass_needed * rmh_count

print("  ┌─ ROCKET MASS HEATER × 2 ────────────────────────────┐")
print(f"  │ System size:        4-inch ({rmh_diameter*100:.0f}cm internal diameter)")
print(f"  │ Height:             {rmh_height}m")
print(f"  │ Thermal output:     {rmh_thermal_output} kW per unit")
print(f"  │ Burn time:          {rmh_burn_time} hr/firing")
print(f"  │ Energy/firing:      {rmh_daily_energy} kWh per RMH")
print(f"  │ Total (×2):         {rmh_total_daily} kWh/day if both fired")
print(f"  │ Thermal mass/unit:  {rmh_mass_needed:.0f} kg (cob/stone, ΔT={rmh_mass_temp_rise}°C)")
print(f"  │ Total mass (×2):    {rmh_total_mass:.0f} kg")
print(f"  │ Materials:          Firebrick, steel pipe, cob, perlite")
print(f"  │ Est. cost:          $50-100 per RMH unit")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# SYSTEM TOTAL — DAILY ENERGY BALANCE
# ═══════════════════════════════════════════════════════════════
total_hot_collected = daily_solar_captured + rmh_total_daily
total_cold_stored = nightly_radiative_conservative
total_electricity = teg_daily_total

# ACRE minting (1 ACRE = 1000 J verified)
acre_from_solar = daily_solar_j / 1000
acre_from_rmh = rmh_total_daily * 3_600_000 / 1000
acre_from_teg = total_electricity * 3_600_000 / 1000
acre_daily_total = acre_from_solar + acre_from_rmh + acre_from_teg
acre_monthly = acre_daily_total * 30

print("  ┌─ DAILY ENERGY BALANCE ──────────────────────────────┐")
print(f"  │ HOT collected:")
print(f"  │   Solar panel:     {daily_solar_captured:.2f} kWh")
print(f"  │   RMH (×2):        {rmh_total_daily:.2f} kWh")
print(f"  │   Total hot:       {total_hot_collected:.2f} kWh")
print(f"  │")
print(f"  │ COLD stored:")
print(f"  │   Radiative night: {total_cold_stored:.2f} kWh")
print(f"  │")
print(f"  │ ELECTRICITY gen:")
print(f"  │   TEG (solar+RMH): {total_electricity:.4f} kWh")
print(f"  │")
print(f"  │ ACRE MINTING (1 ACRE = 1000 J verified):")
print(f"  │   From solar:      {acre_from_solar:,.0f} ACRE")
print(f"  │   From RMH:        {acre_from_rmh:,.0f} ACRE")
print(f"  │   From TEG:        {acre_from_teg:,.0f} ACRE")
print(f"  │   Daily total:     {acre_daily_total:,.0f} ACRE")
print(f"  │   Monthly total:   {acre_monthly:,.0f} ACRE")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# MATERIALS + COST — 1 m² TILE PROTOTYPE
# ═══════════════════════════════════════════════════════════════
materials = [
    ("Portland cement Type I/II", "1 bag (~50kg)", 20, "LLC expense"),
    ("AR-glass fiber (≥20% ZrO₂)", "2 kg", 50, "LLC expense"),
    ("Activated charcoal powder", "2 kg", 20, "LLC expense — has some already"),
    ("Xanthan gum", "125g", 10, "LLC expense"),
    ("Silicone-treated cardboard (mold)", "pre-cut w/ tabs/flanges", 15, "LLC expense"),
    ("Silicone spray (additional)", "1 can", 8, "LLC expense — mold + membrane"),
    ("Clear membrane (greenhouse cover)", "1 m² + 1 inch lip", 12, "LLC expense"),
    ("Thermoelectric generator (TEG)", "1 module", 25, "LLC expense"),
    ("Copper coil (½ inch tube)", "3 m", 25, "LLC expense — cold battery"),
    ("Ferrocement tank materials", "small tank (~40L)", 20, "LLC expense"),
    ("RMH materials (×2)", "firebrick, pipe, cob", 100, "LLC expense — next week priority"),
]

total_cost = sum(m[2] for m in materials)
cost_this_week = total_cost - 100  # defer RMH to next week

print("  ┌─ MATERIALS — 1 m² TILE PROTOTYPE ───────────────────┐")
print(f"  {'Item':<35} {'Qty':<20} {'Cost':>6} {'Route'}")
print(f"  {'─'*35} {'─'*20} {'─'*6} {'─'*12}")
for name, qty, cost, route in materials:
    marker = " ⏭" if "next week" in route else ""
    print(f"  {name:<35} {qty:<20} ${cost:>5} {route}{marker}")
print(f"  {'─'*35} {'─'*20} {'─'*6}")
print(f"  {'TOTAL':<35} {'':>20} ${total_cost:>5}")
print(f"  {'THIS WEEK (no RMH)':<35} {'':>20} ${cost_this_week:>5}")
print(f"  {'NEXT WEEK (RMH ×2)':<35} {'':>20} ${'100':>5}")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# CURE TIME CORRECTION
# ═══════════════════════════════════════════════════════════════
print("  ┌─ CURE TIMES (CORRECTED) ────────────────────────────┐")
print(f"  │ AE-GFRC panel:      1-2 days minimum cure")
print(f"  │   (Open-cell aerated, low water, fast initial set)")
print(f"  │   Full strength:    7 days (acceptable for prototype)")
print(f"  │")
print(f"  │ Ferrocement tank:   21 days wet cure (absolute)")
print(f"  │   (Water-containing, structural, must be fully cured)")
print(f"  │")
print(f"  │ Timeline:")
print(f"  │   Day 1-2:  Pour AE-GFRC panel, demold")
print(f"  │   Day 2-3:  Build ferrocement tank (start 21-day cure)")
print(f"  │   Day 3-7:  Panel dry-fit, assemble airflow path")
print(f"  │   Day 7:    Panel strength sufficient for testing")
print(f"  │   Day 21:   Ferrocement tank cured — system go live")
print(f"  │   Day 22+:  Begin ACRE minting from physical data")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# MOLD DESIGN — CLICK-TOGETHER SILICONE CARDBOARD
# ═══════════════════════════════════════════════════════════════
print("  ┌─ MOLD DESIGN — CLICK PANEL ─────────────────────────┐")
print(f"  │ Material:           Silicone-treated cardboard")
print(f"  │ Construction:       Pre-cut with tabs/flanges")
print(f"  │ Assembly:          Click-together, no fasteners")
print(f"  │")
print(f"  │ Panel mold:         1m × 1m × 50mm deep")
print(f"  │   Side walls:       4 pieces with interlocking tabs")
print(f"  │   Base:             Flat cardboard, silicone-coated")
print(f"  │   Release:          Silicone spray (already treated)")
print(f"  │")
print(f"  │ Dual-purpose silicone layer:")
print(f"  │   1. Mold release (during pour)")
print(f"  │   2. Waterproof membrane (backside, post-cure)")
print(f"  │   3. Insulation backing (retains heat in panel)")
print(f"  │   4. 1-inch lip extension for clear membrane cover")
print(f"  │")
print(f"  │ Greenhouse cover:  Clear air/watertight membrane")
print(f"  │   Sits on 1-inch lip, traps solar IR, heats air gap")
print(f"  │   Creates greenhouse effect above blackbody panel")
print(f"  │   Air inlet/outlet ports molded into panel edges")
print("  └────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════════════════
# 12-MONTH CREDIT + ACRE PROJECTION
# ═══════════════════════════════════════════════════════════════
print("═" * 60)
print("  12-MONTH PROJECTION — CREDIT + ACRE GROWTH")
print("═" * 60)
print()

months = [
    (1, 660, 500, "Set up Varo Believe, first prime cycles"),
    (2, 665, 500, "Consistent <9% utilization, history building"),
    (3, 672, 500, "3 months on-time payments registered"),
    (4, 680, 750, "Possible limit increase (graduation review)"),
    (5, 685, 750, "Continued prime utilization at higher limit"),
    (6, 692, 1000, "6-month mark — limit increase likely"),
    (7, 700, 1000, "Crossed 700 threshold 🎯"),
    (8, 708, 1000, "Aged accounts, strong history"),
    (9, 715, 1500, "9-month credit age, another limit bump"),
    (10, 720, 1500, "10-month consistent prime"),
    (11, 728, 2000, "Approaching 1-year credit age"),
    (12, 735, 2500, "1-year mark — secured→unsecured possible"),
]

# ACRE scales with system deployment
acre_monthly_base = acre_monthly  # from 1 m² system
acre_growth = [1, 1, 1, 1.5, 1.5, 2, 2, 3, 3, 4, 4, 5]  # system expansion factor

print(f"  {'Mo':>3} {'Score':>6} {'Limit':>7} {'9%Max':>7} {'ACRE/mo':>12} {'Cumulative':>14}  Notes")
print(f"  {'─'*3} {'─'*6} {'─'*7} {'─'*7} {'─'*12} {'─'*14}  {'─'*30}")

cumulative_acre = 0
for i, (mo, score, limit, note) in enumerate(months):
    prime_max = int(limit * 0.09)
    monthly_acre = acre_monthly_base * acre_growth[i]
    cumulative_acre += monthly_acre
    print(f"  {mo:>3} {score:>6} ${limit:>6} ${prime_max:>6} {monthly_acre:>12,.0f} {cumulative_acre:>14,.0f}  {note}")

print()
print(f"  Starting score:    660 (all three bureaus)")
print(f"  Target 12-month:   ~735 (with prime utilization + on-time)")
print(f"  Starting limit:    $500 (Varo Believe secured)")
print(f"  Projected 12-mo:  $2,500 (limit growth + graduation)")
print(f"  9% room growth:   $45 → $225 (5x more spending room)")
print(f"  ACRE 12-month:    {cumulative_acre:,.0f} (from thermal system scaling)")
print()
print("  ⚠ Score projections are ESTIMATES — actual growth depends on")
print("    bureau reporting timing, Varo's graduation policy, and")
print("    whether Kikoff reports to all three bureaus consistently.")
print("  ⚠ ACRE numbers are THEORETICAL until physical validation (T3).")
print("═" * 60)
