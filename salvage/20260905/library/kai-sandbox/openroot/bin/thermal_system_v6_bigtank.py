#!/usr/bin/env python3
"""
OPENROOT THERMAL CASCADE v6 — 50,000 GAL FERROCEMENT COLD BATTERY
DV.GEN.TH.SYS06 | Big tank | Aluminum radiative lid | Stirling fixed
"""
import math

# ═══ CONSTANTS ═══
water_cp = 4.186; ice_cp = 2.108; latent_fusion = 335; sigma = 5.67e-8
air_cp = 1.005; air_density = 1.225; al_cond = 205  # W/m·K aluminum

# ═══ SYSTEM BASE: 1 m² PANEL (everything scales to this) ═══
panel_area = 1.0; chimney_height = 2.0; absorption = 0.95
ambient_temp = 25; ice_target = -10; ambient_humidity = 20
ground_temp = 15; night_hours = 12; day_hours = 12
airflow_m3s = 0.0178; airflow_kg_s = airflow_m3s * air_density
airflow_kg_hr = airflow_kg_s * 3600

# ═══ 50-BAR STEAM ═══
sys_pressure = 50; steam_sat_temp = 264; water_start = 25
sensible_50 = water_cp * (steam_sat_temp - water_start)
latent_50 = 1640; total_per_kg_50 = sensible_50 + latent_50
delta_T_full = steam_sat_temp - ice_target  # 274°C
carnot_eff = 1 - (ice_target + 273.15) / (steam_sat_temp + 273.15)  # 51%
stirling_eff = carnot_eff * 0.50  # 25.5%

cold_per_kg = water_cp * (ambient_temp - 0) + latent_fusion + ice_cp * (0 - ice_target)  # 460.7 kJ/kg

# ═══════════════════════════════════════════════════════════════
# THE BIG TANK — 50,000 GALLON FERROCEMENT
# ═══════════════════════════════════════════════════════════════
tank_gallons = 50000
tank_liters = tank_gallons * 3.78541  # 189,270 L
tank_water_kg = tank_liters  # 1 L = 1 kg
tank_volume_m3 = tank_liters / 1000  # 189.27 m³

# Wide and flat — parametrize depth, calculate surface area
# Shallower = more radiative surface area
tank_depth = 0.5  # m (half meter deep — maximizes surface area)
tank_surface_area = tank_volume_m3 / tank_depth  # m²
tank_side = math.sqrt(tank_surface_area)  # square tank for simplicity

# Aluminum lid: thin, in contact with water surface, painted reflective
# Reflective paint: high solar reflectance (~95%), high IR emissivity (~0.95)
# This is a radiative cooling surface — reflects sun by day, radiates to space by night
al_thickness = 0.002  # 2mm aluminum sheet
al_emissivity_ir = 0.95  # high IR emissivity (radiates to deep space)
al_solar_reflectance = 0.95  # reflects 95% of sunlight

# ═══════════════════════════════════════════════════════════════
# COLD CHARGING — RADIATIVE COOLING ON BIG TANK
# ═══════════════════════════════════════════════════════════════
ice_temp_k = ice_target + 273.15  # 263.15K
sky_temp_k = 3  # deep space

# Theoretical radiative flux (Stefan-Boltzmann)
rad_flux_theoretical = al_emissivity_ir * sigma * (ice_temp_k**4 - sky_temp_k**4)  # W/m²

# Realistic: atmosphere blocks ~40-50% depending on humidity
# Missouri summer nights: humid, so conservative 45% of theoretical
atm_transmission = 0.45
rad_flux_realistic = rad_flux_theoretical * atm_transmission

# But aluminum in DIRECT CONTACT with water = excellent heat transfer
# No air gap thermal resistance, water circulates by convection
# This is much better than typical radiative cooler designs

# DAYTIME radiative cooling (reflective coating):
# Reflects 95% of solar, still radiates in IR atmospheric window
# Net daytime cooling: typically 40-70 W/m² with proper coatings
rad_flux_day = 50  # W/m² conservative daytime net cooling

# NIGHTTIME radiative cooling:
rad_flux_night = rad_flux_realistic  # W/m²

# Total cold charging
cold_charge_night = rad_flux_night * tank_surface_area * night_hours / 1000  # kWh
cold_charge_day = rad_flux_day * tank_surface_area * day_hours / 1000  # kWh
cold_charge_total = cold_charge_night + cold_charge_day  # kWh/day

# Ice that can be frozen per night
ice_charged_kg = (cold_charge_night * 3600) / cold_per_kg

# Total cold storage capacity of full tank
tank_cold_capacity_kwh = (tank_water_kg * cold_per_kg) / 3600  # kWh if ALL water freezes

# Days to fully freeze tank from 25°C
days_to_freeze = tank_cold_capacity_kwh / cold_charge_total if cold_charge_total > 0 else 999

# ═══════════════════════════════════════════════════════════════
# HOT SIDE — ALL SOURCES (same as v5)
# ═══════════════════════════════════════════════════════════════
# 1. Solar
solar_daily = 6.5 * panel_area * absorption  # 6.17 kWh

# 2. RMH (modular)
rmh_daily = 8 * 2 * 1.5  # 24 kWh

# 3. Desiccant (net-zero cycle, releases heat during adsorption)
moisture_captured = airflow_kg_hr * 24 * (ambient_humidity - 2) / 1000
desiccant_heat = moisture_captured * 2800 / 3600  # kWh released

# 4. Ambient air thermal (warm air through ice battery)
ambient_to_ice_dT = ambient_temp - ice_target  # 35°C
ambient_captured = airflow_kg_s * air_cp * ambient_to_ice_dT * 3600 * 24 / 1000

# 5. Geothermal (labyrinth deposits heat, cold air picks up ground heat)
geo_deposited = airflow_kg_s * air_cp * (35 - 17) * 3600 * 24 / 1000
geo_to_ice = airflow_kg_s * air_cp * (ground_temp - ice_target) * 3600 * 24 / 1000

total_all_hot = solar_daily + rmh_daily + desiccant_heat + ambient_captured + geo_deposited
total_hot_kj = total_all_hot * 3600

# ═══════════════════════════════════════════════════════════════
# STIRLING ENGINE — PROPERLY CALCULATED
# ═══════════════════════════════════════════════════════════════
beale_num = 0.15; stirling_mean_p = 20e5; stirling_disp = 0.0015
stirling_rpm = 800; stirling_freq = stirling_rpm / 60
stirling_mech_raw = beale_num * stirling_mean_p * stirling_disp * stirling_freq  # W

# Thermal power available (Watts)
hot_power_w = (total_all_hot * 3600) / (24 * 3600)  # = total_all_hot / 24 * 1000
# This is total_all_hot kWh/day ÷ 24 hr × 1000 W/kW = W thermal
hot_power_w_simple = total_all_hot / 24 * 1000  # same thing, cleaner

# Stirling energy-limited output
stirling_energy_limit_w = hot_power_w_simple * stirling_eff

# Actual Stirling: limited by whichever is smaller
stirling_w = min(stirling_mech_raw, stirling_energy_limit_w)
stirling_kw = stirling_w / 1000
stirling_daily_mech = stirling_w * 24 / 1000  # kWh

# Stirling waste heat to cold side
waste_heat_w = stirling_w * (1 - stirling_eff) / stirling_eff
waste_heat_daily = waste_heat_w * 24 / 1000

# ═══════════════════════════════════════════════════════════════
# COLD BALANCE WITH BIG TANK
# ═══════════════════════════════════════════════════════════════
total_cold_charged = cold_charge_total
total_cold_consumed = ambient_captured + geo_to_ice + waste_heat_daily
cold_balance = total_cold_charged - total_cold_consumed

# How much of tank freezes per day (net)
net_cold_daily = cold_balance
ice_growth_kg_day = (net_cold_daily * 3600) / cold_per_kg if net_cold_daily > 0 else 0

# How long tank lasts if deficit
if cold_balance < 0:
    survival_days = tank_cold_capacity_kwh / abs(cold_balance)
else:
    survival_days = 999999  # sustainable

# ═══════════════════════════════════════════════════════════════
# FLYWHEEL + GEAR + ALTERNATOR
# ═══════════════════════════════════════════════════════════════
fw_mass = 75; fw_radius = 0.6; fw_rpm = 600
fw_I = 0.5 * fw_mass * fw_radius**2
fw_energy = 0.5 * fw_I * (fw_rpm * 2 * math.pi / 60)**2
fw_kwh = fw_energy / 3.6e6
gear_ratio = 3600 / stirling_rpm  # 4.5:1
alt_eff = 0.92
alt_w = stirling_w * alt_eff
alt_daily = alt_w * 24 / 1000

# TEG cascade
stirling_exhaust = steam_sat_temp - (delta_T_full * stirling_eff)
teg_dt = stirling_exhaust - ice_target
teg_count = 8; teg_mod_50k = 5
teg_per_mod = teg_mod_50k * (teg_dt / 50)
teg_total_w = teg_per_mod * teg_count
teg_daily = teg_total_w * 24 / 1000

total_elec = alt_daily + teg_daily

# ═══════════════════════════════════════════════════════════════
# ACRE
# ═══════════════════════════════════════════════════════════════
jpa = 1000
acre_total = (solar_daily*3600/jpa + rmh_daily*3600/jpa + desiccant_heat*3600/jpa +
              ambient_captured*3600/jpa + geo_deposited*3600/jpa +
              total_cold_charged*3600/jpa + stirling_daily_mech*3600/jpa +
              teg_daily*3600/jpa + alt_daily*3600/jpa)

# ═══════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════
print("=" * 72)
print("  OPENROOT THERMAL CASCADE v6 — 50,000 GAL FERROCEMENT TANK")
print("  DV.GEN.TH.SYS06 | Big cold battery | Aluminum radiative lid")
print("=" * 72)

print()
print("┌─ THE TANK ────────────────────────────────────────────┐")
print(f"│ Capacity:        {tank_gallons:,} gallons ({tank_liters:,.0f} L)")
print(f"│ Water mass:      {tank_water_kg:,.0f} kg ({tank_water_kg/1000:.0f} tonnes)")
print(f"│ Volume:          {tank_volume_m3:.1f} m³")
print(f"│ Depth:           {tank_depth}m (wide and flat)")
print(f"│ Surface area:    {tank_surface_area:.1f} m² (lid)")
print(f"│ Dimensions:      ~{tank_side:.1f}m × {tank_side:.1f}m × {tank_depth}m")
print(f"│ Material:        Ferrocement (insulated sides/bottom)")
print(f"│ Lid:             {al_thickness*1000:.0f}mm aluminum sheet")
print(f"│ Lid treatment:   Reflective paint (high solar reflectance)")
print(f"│                  + high IR emissivity (radiates to space)")
print(f"│ Contact:         Aluminum directly on water surface")
print(f"│                  (zero air gap = perfect heat transfer)")
print(f"│ Copper coil:     Runs through tank (Stirling cold-side HX)")
print("└──────────────────────────────────────────────────────┘")

print()
print("┌─ RADIATIVE COOLING — BIG LID ────────────────────────┐")
print(f"│ Lid area:          {tank_surface_area:.1f} m²")
print(f"│ IR emissivity:    {al_emissivity_ir}")
print(f"│ Solar reflectance: {al_solar_reflectance}")
print(f"│")
print(f"│ Theoretical flux:  {rad_flux_theoretical:.1f} W/m²")
print(f"│ Atmosphere block:  ~{(1-atm_transmission)*100:.0f}% (MO summer humidity)")
print(f"│ Realistic night:   {rad_flux_night:.1f} W/m²")
print(f"│ Daytime net:       {rad_flux_day:.0f} W/m² (reflects sun + radiates IR)")
print(f"│")
print(f"│ NIGHT charging:    {rad_flux_night:.1f}W × {tank_surface_area:.0f}m² × {night_hours}hr")
print(f"│                    = {cold_charge_night:.1f} kWh/night")
print(f"│ DAY charging:      {rad_flux_day:.0f}W × {tank_surface_area:.0f}m² × {day_hours}hr")
print(f"│                    = {cold_charge_day:.1f} kWh/day")
print(f"│ TOTAL COLD/d:      {cold_charge_total:.1f} kWh/day")
print(f"│")
print(f"│ Ice frozen/night:  {ice_charged_kg:.0f} kg")
print(f"│")
print(f"│ FULL TANK CAPACITY:")
print(f"│   Water→ice→-10C: {tank_cold_capacity_kwh:,.0f} kWh")
print(f"│   = {tank_water_kg:,.0f} kg × {cold_per_kg:.0f} kJ/kg")
print(f"│   Days to freeze:  {days_to_freeze:.0f} days from 25°C")
print(f"│   (from empty, no cold draw)")
print("└──────────────────────────────────────────────────────┘")

print()
print("┌─ COLD BALANCE — BIG TANK vs SMALL ────────────────────┐")
print(f"│                        SMALL (v5b)    BIG TANK (v6)")
print(f"│  ──────────────────────────────────────────────────")
print(f"│  Lid area:              {panel_area:.0f} m²          {tank_surface_area:.0f} m²")
print(f"│  Cold charged/d:        {1.55:>8.1f} kWh     {cold_charge_total:>8.1f} kWh")
print(f"│  Ambient air demand:   {ambient_captured:>8.1f} kWh     {ambient_captured:>8.1f} kWh")
print(f"│  Geothermal demand:    {geo_to_ice:>8.1f} kWh     {geo_to_ice:>8.1f} kWh")
print(f"│  Stirling waste:       {waste_heat_daily:>8.1f} kWh     {waste_heat_daily:>8.1f} kWh")
print(f"│  Total consumed:       {total_cold_consumed:>8.1f} kWh     {total_cold_consumed:>8.1f} kWh")
print(f"│  ──────────────────────────────────────────────────")
if cold_balance >= 0:
    print(f"│  BALANCE: SURPLUS       {cold_balance:>8.1f} kWh/day  ← SUSTAINABLE!")
    print(f"│  Ice growth/d:         {ice_growth_kg_day:>8.0f} kg/day")
    print(f"│  Tank fills in:        {tank_cold_capacity_kwh/cold_balance:.0f} days (if no draw)")
    print(f"│")
    print(f"│  ★ COLD SIDE SOLVED ★")
    print(f"│  Tank has {tank_cold_capacity_kwh:,.0f} kWh cold reserve")
    print(f"│  Charging at {cold_charge_total:.0f} kWh/day")
    print(f"│  Draws only {total_cold_consumed:.0f} kWh/day")
    print(f"│  Surplus builds ice bank continuously")
else:
    print(f"│  BALANCE: DEFICIT      {abs(cold_balance):>8.1f} kWh/day")
    print(f"│  Tank lasts:           {survival_days:.0f} days")
    print(f"│  Need:                {abs(cold_balance)/cold_charge_total*tank_surface_area:.0f} m² more lid")
print("└──────────────────────────────────────────────────────┘")

print()
print("┌─ HOT SIDE (unchanged) ───────────────────────────────┐")
print(f"│  Solar:           {solar_daily:.2f} kWh")
print(f"│  RMH:             {rmh_daily:.2f} kWh")
print(f"│  Desiccant:       {desiccant_heat:.2f} kWh (net-zero cycle)")
print(f"│  Ambient air:     {ambient_captured:.2f} kWh")
print(f"│  Geothermal:      {geo_deposited:.2f} kWh")
print(f"│  TOTAL HOT:       {total_all_hot:.2f} kWh/day")
print("└──────────────────────────────────────────────────────┘")

print()
print("┌─ STIRLING ENGINE (FIXED) ─────────────────────────────┐")
print(f"│  Beale raw:        {stirling_mech_raw:.0f} W")
print(f"│  Thermal power:    {hot_power_w_simple:.0f} W ({hot_power_w_simple/1000:.2f} kW)")
print(f"│  Energy limit:     {stirling_energy_limit_w:.0f} W")
print(f"│  ACTUAL:           {stirling_w:.0f} W ({stirling_kw:.2f} kW)")
print(f"│  Daily mech:       {stirling_daily_mech:.2f} kWh")
print(f"│  Carnot:           {carnot_eff*100:.1f}%")
print(f"│  Real eff:         {stirling_eff*100:.1f}%")
print(f"│  Exhaust:          ~{stirling_exhaust:.0f}°C")
print(f"│  Waste heat:       {waste_heat_w:.0f}W ({waste_heat_daily:.1f} kWh/day)")
print("└──────────────────────────────────────────────────────┘")

print()
print("┌─ FLYWHEEL + GEAR + ALTERNATOR ───────────────────────┐")
print(f"│  Flywheel:     {fw_mass}kg × {fw_radius}m @ {fw_rpm} RPM = {fw_kwh:.4f} kWh")
print(f"│  Gear ratio:   {gear_ratio:.1f}:1 (Stirling {stirling_rpm}→Alt 3600 RPM)")
print(f"│  Alternator:  {alt_w:.0f}W ({alt_daily:.2f} kWh/day)")
print(f"│  TEG bank:    {teg_total_w:.0f}W ({teg_daily:.2f} kWh/day)")
print(f"│  TOTAL ELEC:  {total_elec:.2f} kWh/day ({total_elec*1000/24:.0f}W continuous)")
print("└──────────────────────────────────────────────────────┘")

print()
print("┌─ DAILY ENERGY BALANCE ───────────────────────────────┐")
print(f"│")
print(f"│  HOT IN:           {total_all_hot:.1f} kWh")
print(f"│  COLD CHARGED:     {cold_charge_total:.1f} kWh")
print(f"│  COLD CONSUMED:   {total_cold_consumed:.1f} kWh")
print(f"│  COLD BALANCE:    {cold_balance:+.1f} kWh {'✓' if cold_balance>=0 else '✗'}")
print(f"│  COLD RESERVE:    {tank_cold_capacity_kwh:,.0f} kWh (full tank)")
print(f"│")
print(f"│  ELECTRICAL:      {total_elec:.1f} kWh ({total_elec*1000/24:.0f}W)")
print(f"│  MECHANICAL:      {stirling_daily_mech:.1f} kWh (flywheel + shaft)")
print(f"│  WASTE HEAT:      {waste_heat_daily:.1f} kWh (to cascade)")
print(f"│")
print(f"│  ACRE/DAY:        {acre_total:,.0f}")
print(f"│  ACRE/MONTH:      {acre_total*30:,.0f}")
print(f"│  ACRE/YEAR:       {acre_total*365:,.0f}")
print("└──────────────────────────────────────────────────────┘")

# ═══════════════════════════════════════════════════════════════
# SCALING — panel scales, tank is FIXED
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 72)
print("  SCALING — PANEL SCALES, TANK FIXED AT 50,000 GAL")
print("=" * 72)
print()
print(f"  Tank surface area: {tank_surface_area:.0f} m² (fixed)")
print(f"  Tank cold charge:  {cold_charge_total:.0f} kWh/day (fixed)")
print(f"  Tank cold reserve: {tank_cold_capacity_kwh:,.0f} kWh (fixed)")
print()
print(f"  {'Scale':<14} {'Panel':>5} {'Hot/d':>7} {'Cold/d':>7} {'ColdBal':>8} {'Stir.W':>7} {'Elec/d':>7} {'ACRE/d':>10}")
print(f"  {'-'*14} {'-'*5} {'-'*7} {'-'*7} {'-'*8} {'-'*7} {'-'*7} {'-'*10}")

scales = [
    ("Tile", 1), ("Bench", 5), ("Home", 25),
    ("Home+", 50), ("Farm", 100), ("Community", 250), ("Village", 500),
]

for name, f in scales:
    h = total_all_hot * f
    # Cold consumed scales with panel (more airflow = more hot = more cold draw)
    cc = total_cold_consumed * f
    cb = cold_charge_total - cc  # tank charge is FIXED
    # Stirling limited by cold balance — can only use what cold is available
    if cb > 0:
        # Cold is surplus — Stirling limited by hot side
        sw = min(stirling_w * f, stirling_energy_limit_w * f)
    else:
        # Cold limited — Stirling limited by available cold
        # Max Stirling that doesn't exceed cold capacity
        cold_avail = cold_charge_total  # fixed tank
        # Waste heat = Stirling_w * (1-eff)/eff, must be <= cold_avail - other draws
        other_draws = cc - waste_heat_daily * f  # ambient + geo (scales with panel)
        if other_draws < cold_avail:
            cold_for_stirling = cold_avail - other_draws
            # waste_heat = sw * (1-eff)/eff <= cold_for_stirling
            # sw <= cold_for_stirling * eff / (1-eff) * 1000 / 24 (convert kWh to W)
            sw_max_cold = (cold_for_stirling * 1000 / 24) * stirling_eff / (1 - stirling_eff)
            sw = min(stirling_w * f, sw_max_cold)
        else:
            sw = 0
    sw = max(sw, 0)
    el = sw * alt_eff * 24 / 1000 + teg_daily * f
    ac = acre_total * f
    bal_str = f"{cb:+.0f}" if abs(cb) < 1000 else f"{cb:+.0f}"
    print(f"  {name:<14} {panel_area*f:>4.0f}m² {h:>6.0f} {cc:>6.0f} {bal_str:>8} {sw:>6.0f}W {el:>6.1f}k {ac:>10,.0f}")

print()
print("  Tank is FIXED — it doesn't scale with panel.")
print("  Cold is abundant for small panels, becomes limiting at scale.")
max_panel = cold_charge_total / (total_cold_consumed / 1)  # panel factor where cold breaks even
print(f"  Break-even: ~{max_panel:.0f} m² panel (cold charge = cold demand)")
print(f"  Beyond that: add more tanks or reduce airflow")
print("=" * 72)

# ═══════════════════════════════════════════════════════════════
# VERDICT
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 72)
print("  VERDICT")
print("=" * 72)
print()
if cold_balance >= 0:
    print(f"  ★ COLD SIDE SOLVED ★")
    print(f"  50,000 gal tank with {tank_surface_area:.0f} m² aluminum radiative lid")
    print(f"  charges {cold_charge_total:.0f} kWh/day of cold")
    print(f"  Demand is only {total_cold_consumed:.0f} kWh/day")
    print(f"  Surplus: {cold_balance:.0f} kWh/day builds ice reserve")
    print(f"  Reserve: {tank_cold_capacity_kwh:,.0f} kWh total capacity")
    print(f"")
    print(f"  Stirling: {stirling_w:.0f}W continuous → {total_elec:.1f} kWh/day elec")
    print(f"  That's {total_elec*1000/24:.0f}W average on a 1m² panel + big tank")
    print(f"")
    print(f"  The tank is the battery. The lid is the charger.")
    print(f"  Deep space is the cold source. The sun is the hot source.")
    print(f"  The Stirling sits between them.")
else:
    print(f"  Still a cold deficit of {abs(cold_balance):.0f} kWh/day")
    print(f"  But tank provides {tank_cold_capacity_kwh:,.0f} kWh buffer = {survival_days:.0f} days")
    print(f"  Much better than 0.3 hour survival with small tank!")
print("=" * 72)
