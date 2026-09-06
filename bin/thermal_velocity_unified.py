#!/usr/bin/env python3
"""
OpenRoot Thermal Velocity — UNIFIED RATE FRAMEWORK v5.0

Every variable expressed as [Energy/Time] = Watts.
System understood as a single velocity through coupled nodes.

This converts the thermal cascade into a formal rate equation system,
analogous to electrical circuit analysis or fluid dynamics.

KEY INSIGHT: When every node is in Watts, the system becomes a coupled
set of ODEs (ordinary differential equations). The system velocity is
the harmonic mean of all stage rates — limited by the slowest node,
but EVERY node contributes to the overall flow.

This is analogous to:
  - Electrical: V = IR, current is uniform in series circuits
  - Fluid: mass conservation, flow rate uniform in pipes
  - Thermal: Ė = ΔT / R_thermal, heat flow uniform in steady state

The SYSTEM VELOCITY is NOT the sum of individual velocities.
It's the harmonic coupling — the rate at which a joule traverses
from source to sink through ALL stages.
"""
import math

print("=" * 80)
print("  OPENROOT THERMAL VELOCITY — UNIFIED RATE FRAMEWORK v5.0")
print("  Every variable = Watts [J/s]")
print("  System velocity = harmonic coupling of all stage rates")
print("=" * 80)

# ============================================================
# CORE PRINCIPLE: EVERYTHING IS A RATE
# ============================================================
print("""
  ┌─────────────────────────────────────────────────────────────┐
  │  THE COALITION PRINCIPLE                                   │
  │                                                             │
  │  Every physical quantity converted to [J/s]:               │
  │    • Temperature change rate → Θ (K/s) × C_thermal = W     │
  │    • Mass flow × Cp × ΔT → W (heat transport rate)          │
  │    • Storage capacity / time → W (charge/discharge rate)    │
  │    • Mechanical power → W (already a rate)                  │
  │    • Electrical power → W (already a rate)                 │
  │    • Chemical reaction rate → W (combustion energy rate)   │
  │                                                             │
  │  When ALL variables share the same unit (Watts),           │
  │  the system becomes a SET OF COUPLED RATE EQUATIONS.        │
  │                                                             │
  │  This is analogous to Kirchhoff's laws in electrical      │
  │  circuits: current is conserved at every junction,         │
  │  voltage drops across resistances, total V = ΣIR.        │
  │                                                             │
  │  Thermal analog:                                           │
  │    Current (Ė) = heat flow rate in Watts                    │
  │    Voltage (ΔT) = temperature difference                   │
  │    Resistance (R_th) = thermal resistance (K/W)            │
  │    Ė = ΔT / R_th  →  W = K / (K/W) = W ✓                  │
  │                                                             │
  │  The SYSTEM VELOCITY is the COUPLED FLOW RATE              │
  │  through all stages — limited by the slowest,             │
  │  accelerated by the fastest, balanced by storage.         │
  └─────────────────────────────────────────────────────────────┘
""")

# ============================================================
# PHYSICAL CONSTANTS (all in SI base units)
# ============================================================
g = 9.81            # m/s²
sigma = 5.67e-8      # W/(m²·K⁴) Stefan-Boltzmann
cp_water = 4186     # J/(kg·K)
cp_steam = 2010     # J/(kg·K)
cp_air = 1005       # J/(kg·K)
cp_concrete = 880   # J/(kg·K)
L_fusion = 334000   # J/kg

# ============================================================
# EVERY VARIABLE AS A RATE [W]
# ============================================================

print("=" * 80)
print("  SECTION 1: EVERY NODE AS A RATE [Watts]")
print("=" * 80)

# --- SOURCE ---
rmh_thermal_output = 25000  # W — combustion energy rate delivered to water
rmh_fuel_rate_joules = rmh_thermal_output  # W (same — energy in = energy out at steady state)
# Fuel combustion rate (chemical → thermal)
# Black locust: ~19 MJ/kg dry
fuel_energy_density = 19e6  # J/kg
rmh_fuel_kg_per_s = rmh_thermal_output / fuel_energy_density  # kg/s
rmh_efficiency = 0.85  # combustion → water heat transfer
rmh_combustion_rate = rmh_thermal_output / rmh_efficiency  # W (gross chemical energy)

print(f"""
  SOURCE: Rocket Mass Heater
    Combustion rate (chemical):  {rmh_combustion_rate:>10,.0f} W
    Delivered to water (net):    {rmh_thermal_output:>10,.0f} W
    Loss (up chimney + shell):   {rmh_combustion_rate - rmh_thermal_output:>10,.0f} W
    Fuel feed rate:              {rmh_fuel_kg_per_s*3600:>10,.2f} kg/hr
                                ({rmh_fuel_kg_per_s*1000:>10,.2f} g/s)
    Fuel energy density:         {fuel_energy_density/1e6:>10,.1f} MJ/kg (dry black locust)
""")

# --- TRANSPORT (Thermosiphon) ---
# Water-side thermosiphon: circulation rate carries heat
# Ė_transport = ṁ × Cp × ΔT  [W]
rho_hot = 972   # kg/m³
rho_cold = 998  # kg/m³
pipe_d = 0.05   # m
pipe_area = math.pi * (pipe_d/2)**2
chimney_h = 10  # m
circuit_len = 30  # m
friction = 0.025
delta_P = (rho_cold - rho_hot) * g * chimney_h  # Pa
water_vel = math.sqrt((2 * delta_P) / (friction * (circuit_len/pipe_d) * rho_hot))
mass_flow = rho_hot * pipe_area * water_vel  # kg/s
delta_T_transport = 60  # K (hot leg to cold leg)
transport_rate = mass_flow * cp_water * delta_T_transport  # W

# Capacity factor: how much of transport capacity is utilized
transport_utilization = rmh_thermal_output / transport_rate  # fraction

print(f"""
  TRANSPORT: Thermosiphon Loop
    Mass flow rate:              {mass_flow:>10,.3f} kg/s
    Velocity:                    {water_vel:>10,.3f} m/s
    ΔT across loop:              {delta_T_transport:>10} K
    Transport capacity (Ė_max):  {transport_rate:>10,.0f} W
    Actual flow (Ė_used):        {rmh_thermal_output:>10,.0f} W
    Utilization:                 {transport_utilization:>10.2%}
    Headroom:                    {1-transport_utilization:>10.2%}
    
    NOTE: Transport is OVERSPECIFIED by {transport_rate/rmh_thermal_output:.0f}x.
    Pipe could be {pipe_d*100*(transport_utilization**0.5):.1f}cm and still deliver.
    (Flow scales with √area for same ΔP)
""")

# --- STORAGE (Hot Tank) ---
tank_gallons = 50000
tank_liters = tank_gallons * 3.78541
tank_mass = tank_liters  # kg
tank_C = tank_mass * cp_water  # J/K
tank_delta_T = 70  # K
tank_energy = tank_C * tank_delta_T  # J

# Rate of charge (filling the tank)
charge_rate = rmh_thermal_output  # W
# Rate of discharge (Stirling draw per tank)
n_stirlings_per_tank = 10
stirling_thermal_each = 6538  # W
discharge_rate = n_stirlings_per_tank * stirling_thermal_each  # W

# Time-based rates
charge_time = tank_energy / charge_rate  # s
discharge_time = tank_energy / discharge_rate  # s

# RATE FORM: storage as a "rate" when normalized over characteristic time
# E_stored / τ_characteristic = W (power equivalent)
tank_rate_charging = tank_energy / charge_time  # W (= charge_rate)
tank_rate_discharging = tank_energy / discharge_time  # W (= discharge_rate)

print(f"""
  STORAGE: 50,000 Gallon Hot Tank
    Mass:                        {tank_mass:>10,.0f} kg
    C_thermal:                   {tank_C:>10,.0f} J/K
    ΔT operating:               {tank_delta_T:>10} K
    Stored energy:               {tank_energy/3.6e6:>10,.0f} kWh ({tank_energy/3.6e9:.2f} GWh)
    
    Charge rate (RMH → tank):    {charge_rate:>10,.0f} W
    Discharge rate (10 Stirling):{discharge_rate:>10,.0f} W
    Net rate (charge - discharge):{charge_rate - discharge_rate:>10,.0f} W
    
    Charge time (full):          {charge_time/3600:>10,.1f} h ({charge_time/86400:.1f}d)
    Discharge time (full):       {discharge_time/3600:>10,.1f} h ({discharge_time/86400:.1f}d)
    
    AS RATE: 
      E/t_charge =               {tank_rate_charging:>10,.0f} W (same as charge_rate)
      E/t_discharge =            {tank_rate_discharging:>10,.0f} W (same as discharge_rate)
""")

# --- CONVERSION (Stirling) ---
stirling_input = stirling_thermal_each  # W thermal
stirling_eff_mech = 0.35  # thermal → mechanical (realistic Stirling)
stirling_eff_elec = 0.28  # thermal → electrical (after alternator)
stirling_mech_rate = stirling_input * stirling_eff_mech  # W
stirling_elec_rate = stirling_input * stirling_eff_elec  # W
stirling_reject = stirling_input - stirling_mech_rate  # W (waste heat to cold side)

print(f"""
  CONVERSION: Stirling Engine (per unit)
    Thermal input:               {stirling_input:>10,.0f} W
    Mechanical output:           {stirling_mech_rate:>10,.0f} W ({stirling_eff_mech*100:.0f}%)
    Electrical output:           {stirling_elec_rate:>10,.0f} W ({stirling_eff_elec*100:.0f}%)
    Reject heat (to cold side):  {stirling_reject:>10,.0f} W
""")

# --- COLD SINK ---
effective_cp_cold = cp_water + (L_fusion / 20)
cold_mass = 159300
cold_C = cold_mass * effective_cp_cold
cold_charge_power = 31463  # W (radiative lid)
cold_discharge_power = 20 * stirling_reject  # W (20 Stirlings rejecting)
cold_charge_time = cold_C * 20 / cold_charge_power
cold_discharge_time = cold_C * 20 / cold_discharge_power

print(f"""
  SINK: Cold Battery (phase-change, latent heat)
    C_thermal (with latent):    {cold_C:>10,.0f} J/K
    Charge rate (radiative lid): {cold_charge_power:>10,.0f} W
    Discharge rate (20 Stirling):{cold_discharge_power:>10,.0f} W
    Net:                         {cold_charge_power - cold_discharge_power:>10,.0f} W
""")

# ============================================================
# SECTION 2: THE SYSTEM AS A SINGLE VELOCITY
# ============================================================
print("=" * 80)
print("  SECTION 2: SYSTEM VELOCITY — THE COUPLED RATE")
print("=" * 80)

# In a series thermal circuit (steady state):
# Ė_system = min(Ė_source, Ė_transport, Ė_storage_charge, Ė_conversion, Ė_sink)
#
# But in TRANSIENT (startup, dynamic operation):
# The system has a CHARACTERISTIC VELOCITY — the time for a joule
# to traverse from source to sink through ALL nodes.
#
# For series resistances: R_total = Σ R_i
# For series rate limits: 1/Ė_total = Σ (1/Ė_i)  [harmonic sum]
# Because the slowest stage gates everything.

# All stage rates [W]
stage_rates = {
    "RMH Combustion":        rmh_combustion_rate,
    "RMH → Water Transfer":   rmh_thermal_output,
    "Thermosiphon Transport": transport_rate,
    "Tank Charge Rate":       charge_rate,
    "Stirling Conversion":    20 * stirling_input,  # 20 engines
    "Electrical Output":      20 * stirling_elec_rate,
    "Cold Sink Absorption":   cold_discharge_power,
}

print("""
  In a SERIES circuit, the flow rate is limited by the SLOWEST node.
  But every node CONTRIBUTS to total system resistance.
  
  System velocity (harmonic coupling):
  
    1/Ė_sys = Σ (1/Ė_i)  for all stages in series
    
    This gives the EFFECTIVE throughput — the rate at which
    energy actually flows from source to sink considering
    ALL bottlenecks simultaneously.
""")

# Harmonic sum (series rate limit)
harmonic_sum = sum(1/r for r in stage_rates.values())
system_velocity = 1 / harmonic_sum  # W — the coupled flow rate

print(f"  {'STAGE':<30} {'Rate (W)':>14} {'1/Rate':>14} {'Share':>10}")
print(f"  {'-'*30} {'-'*14} {'-'*14} {'-'*10}")

for name, rate in stage_rates.items():
    inv = 1/rate
    share = inv / harmonic_sum * 100
    bar = "█" * int(share / 5)
    print(f"  {name:<30} {rate:>14,.0f} {inv:>14.8f} {share:>8.1f}% {bar}")

print(f"\n  {'SYSTEM VELOCITY (Ė_sys):':<30} {system_velocity:>14,.0f} W")
print(f"  {'Harmonic sum (1/Ė_sys):':<30} {harmonic_sum:>14.8f}")
print(f"  {'System transit time':<30} {tank_energy/system_velocity/3600:>14,.1f} h ({tank_energy/system_velocity/86400:.1f}d)")

# Dominant bottleneck
bottleneck_name = min(stage_rates, key=stage_rates.get)
bottleneck_share = (1/stage_rates[bottleneck_name]) / harmonic_sum * 100

print(f"""
  DOMINANT BOTTLENECK: {bottleneck_name}
    Rate: {stage_rates[bottleneck_name]:,.0f} W
    Contributes {bottleneck_share:.1f}% of total system resistance
  
  THE SYSTEM VELOCITY IS NOT THE SLOWEST RATE.
  It's LOWER than the slowest rate, because every stage adds resistance.
  Just as in electrical circuits: R_total > R_max (series).
  
  But the slowest stage DOMINATES — contributing {bottleneck_share:.1f}% of resistance.
  Improving it by 2x improves system velocity by ~{bottleneck_share/100:.2f}× at most.
""")

# ============================================================
# SECTION 3: TIME-DOMAIN ANALYSIS — RATES OVER TIME
# ============================================================
print("=" * 80)
print("  SECTION 3: TIME-DOMAIN — RATES CHANGE AS SYSTEM EVOLVES")
print("=" * 80)

# At any moment, each node has a current rate depending on state:
# - Tank rate depends on current temperature (higher T = faster Stirling)
# - Thermosiphon rate depends on ΔT (changes as tank charges)
# - Stirling rate depends on hot-side T (Carnot efficiency shifts)
# - Cold sink rate depends on cold battery state of charge

# Simulate: 72-hour timeline, 1-hour steps
dt = 3600  # s (1 hour)
hours = 72
n_rmh = 6  # 6 RMH units for 20 Stirlings (continuous fire)
total_rmh = n_rmh * rmh_thermal_output  # W
total_stirling_thermal = 20 * stirling_thermal_each  # W
total_stirling_elec = 20 * stirling_elec_rate  # W

# Tank starts at 20°C (cold start)
tank_temp = 20.0  # °C
tank_temp_max = 95.0

print(f"""
  SIMULATION: 72-hour dynamic model
    {n_rmh} RMHs charging: {total_rmh/1000:.0f} kW
    20 Stirlings drawing: {total_stirling_thermal/1000:.0f} kW
    Net thermal: {(total_rmh - total_stirling_thermal)/1000:.1f} kW
    Starting temp: {tank_temp}°C
    Max temp: {tank_temp_max}°C
""")

print(f"  {'Hour':>4} {'Tank°C':>8} {'Charge_W':>10} {'Draw_W':>10} {'Net_W':>10} {'Elec_W':>10} {'Cum_kWh':>10}")
print(f"  {'-'*4} {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

cumulative_elec = 0  # J

for h in range(0, hours+1, 4):
    # Stirling output depends on temperature (Carnot scaling)
    # η ∝ (T_hot - T_cold) / T_hot
    T_hot_K = tank_temp + 273.15
    T_cold_K = 20 + 273.15  # cold battery at ~20°C
    carnot_ratio = (T_hot_K - T_cold_K) / T_hot_K
    carnot_nominal = (95 - 20) / (95 + 273.15)  # nominal at 95°C
    power_scale = carnot_ratio / carnot_nominal if 'carnot_nominal' in dir() else 1.0
    
    # Actually compute properly
    carnot_nominal = (95 + 273.15 - 20 - 273.15) / (95 + 273.15)  # 0.2040
    if T_hot_K > T_cold_K + 10:  # minimum ΔT to run
        power_scale = carnot_ratio / carnot_nominal
        actual_stirling_thermal = total_stirling_thermal * power_scale
        actual_stirling_elec = actual_stirling_thermal * stirling_eff_elec
    else:
        actual_stirling_thermal = 0
        actual_stirling_elec = 0
    
    # Stirling can't draw more than tank can supply
    # (tank has enormous capacity, so rate-limited by engine not tank)
    
    net_power = total_rmh - actual_stirling_thermal  # W
    # Update tank temperature
    # dT = net_power * dt / C_thermal
    
    cumulative_elec += actual_stirling_elec * dt  # J
    
    if h % 4 == 0:
        print(f"  {h:>4} {tank_temp:>8.1f} {total_rmh:>10,.0f} {actual_stirling_thermal:>10,.0f} {net_power:>10,.0f} {actual_stirling_elec:>10,.0f} {cumulative_elec/3.6e6:>10.1f}")
    
    # Step forward
    dT = net_power * dt / tank_C
    tank_temp += dT
    if tank_temp > tank_temp_max:
        tank_temp = tank_temp_max
    if tank_temp < 20:
        tank_temp = 20.0

print(f"""
  KEY OBSERVATIONS FROM TIME-DOMAIN:
  
  1. System velocity is NOT constant — it changes as the tank charges.
     Cold start: Stirlings produce little (low ΔT → low Carnot)
     Hot tank: Stirlings at full rated power
     → There's a "ramp-up" period where system velocity increases.
  
  2. The tank acts as a LOW-PASS FILTER on the RMH input:
     RMH pulses (fire lit/extinguished) → smoothed by tank mass
     Stirlings see steady temperature, not fire pulses
     
  3. Each stage's rate is a FUNCTION OF STATE, not constant:
     R_stage(t) = f(Tank_T(t), Ambient_T(t), ColdBattery_SoC(t), ...)
     
  4. The SYSTEM VELOCITY is therefore also time-varying:
     Ė_sys(t) = harmonic_coupling(all_stage_rates(state(t)))
""")

# ============================================================
# SECTION 4: THE COALITION MATRIX
# ============================================================
print("=" * 80)
print("  SECTION 4: RATE COALITION MATRIX")
print("  Every Variable × Every Relationship — All in Watts")
print("=" * 80)

# Define all nodes with their rate in Watts and their dependencies
nodes = [
    ("Fuel Feed",          n_rmh * 3.0 * 3600 / 3600 * 19e6 / 1e6, "kg/hr × MJ/kg → MW"),
    ("RMH Combustion",     total_rmh, "Chemical → Thermal"),
    ("Thermosiphon",        transport_rate, "Buoyancy-driven flow"),
    ("Tank Charge",         total_rmh, "RMH → Tank mass"),
    ("Tank Discharge",      total_stirling_thermal, "Tank → Stirlings"),
    ("Stirling Input",      total_stirling_thermal, "Thermal draw"),
    ("Stirling Mech",       total_stirling_thermal * stirling_eff_mech, "Thermal → Mechanical"),
    ("Stirling Elec",       total_stirling_thermal * stirling_eff_elec, "Thermal → Electrical"),
    ("Stirling Reject",     total_stirling_thermal * (1 - stirling_eff_mech), "Waste → Cold Sink"),
    ("Cold Sink Absorb",    total_stirling_thermal * (1 - stirling_eff_mech), "Heat rejection rate"),
    ("Cold Lid Charge",     31463, "Radiative cooling rate"),
    ("Grid Export",         total_stirling_thermal * stirling_eff_elec, "Electrical output"),
]

print(f"""
  Every node expressed as a RATE [W]. Every relationship is W → W.
  
  {'NODE':<22} {'Rate (W)':>12} {'Rate (kW)':>10} {'Rate (MW)':>10} Nature")
  {'-'*22} {'-'*12} {'-'*10} {'-'*10} {'-'*30}""")

for name, rate, nature in nodes:
    print(f"  {name:<22} {rate:>12,.0f} {rate/1000:>10,.1f} {rate/1e6:>10.4f} {nature}")

print(f"""
  COALITION INVARIANTS (conservation laws, all in W):
  
  Energy In = Energy Out + Storage Rate:
    RMH_out = Stirling_in + dU_tank/dt
    {total_rmh:,.0f} = {total_stirling_thermal:,.0f} + dU/dt
    dU/dt = {total_rmh - total_stirling_thermal:,.0f} W {'(charging)' if total_rmh > total_stirling_thermal else '(discharging)'}
  
  Stirling Throughput:
    Stirling_in = Stirling_mech + Stirling_reject
    {total_stirling_thermal:,.0f} = {total_stirling_thermal * stirling_eff_mech:,.0f} + {total_stirling_thermal * (1-stirling_eff_mech):,.0f}
    
  Stirling_elec = Stirling_mech × η_alternator
    {total_stirling_thermal * stirling_eff_elec:,.0f} = {total_stirling_thermal * stirling_eff_mech:,.0f} × {stirling_eff_elec/stirling_eff_mech:.2f}
  
  Cold Battery Balance:
    Reject_heat = Cold_absorb_rate
    {total_stirling_thermal * (1-stirling_eff_mech):,.0f} = {total_stirling_thermal * (1-stirling_eff_mech):,.0f} ✓
    
  Cold Battery Charge vs Discharge:
    Lid charge: {31463:,.0f} W  vs  Stirling reject: {total_stirling_thermal * (1-stirling_eff_mech):,.0f} W
    Ratio: {31463 / (total_stirling_thermal * (1-stirling_eff_mech)):.2f}
""")

# ============================================================
# SECTION 5: SYSTEM VELOCITY AS A SINGLE NUMBER
# ============================================================
print("=" * 80)
print("  SECTION 5: SYSTEM VELOCITY — THE ONE NUMBER")
print("=" * 80)

# The system velocity in steady state (all rates coupled):
# Ė_ss = min(all stage rates)  [W] — limited by tightest bottleneck
# But with storage buffering, transient velocity can exceed steady state

steady_state_rate = min(
    total_rmh,                    # source can supply
    transport_rate,                 # transport can move
    total_stirling_thermal,        # engines can draw
    cold_discharge_power,          # sink can absorb
    # note: tank is storage, not a rate limit in steady state
)

# System velocity as "joules per second from fuel to electricity"
fuel_to_elec_rate = steady_state_rate * stirling_eff_elec  # W electrical

# System velocity as "joules per second from fuel to cold sink" (full thermal)
fuel_to_sink_rate = steady_state_rate  # W thermal

# Transit time: how long for 1 joule to go fuel → electricity
# Sum of individual transit times (series)
transit_times = {
    "RMH combustion":       2.0,       # s
    "Water heat transfer":   10.0,      # s (estimate)
    "Thermosiphon transit":  circuit_len / water_vel,  # s
    "Tank residence":        tank_energy / steady_state_rate,  # s (long!)
    "Stirling conversion":   3.7,       # s
    "Alternator":            4.4,       # s
}

total_transit = sum(transit_times.values())

print(f"""
  SYSTEM VELOCITY (steady state):
    Thermal throughput:  {steady_state_rate/1000:.1f} kW
    Electrical output:   {fuel_to_elec_rate/1000:.1f} kW
    Fuel consumption:    {n_rmh * 3.0:.0f} kg/hr ({n_rmh} RMHs × 3kg/hr)
    
  TRANSIT TIME (fuel → electricity, 1 joule):
""")

for stage, t in transit_times.items():
    print(f"    {stage:<25} {t:>12.1f} s {'(' + str(t/3600) + ' h)' if t > 3600 else ''}")

print(f"    {'TOTAL TRANSIT':<25} {total_transit:>12.1f} s ({total_transit/3600:.1f}h)")
print(f"    (dominated by tank residence time — {transit_times['Tank residence']/3600:.1f}h)")

print(f"""
  CAN THE SYSTEM BE UNDERSTOOD AS A VELOCITY?
  
  YES — but it's a DISTRIBUTED velocity, not a single number.
  
  Like a river with pools and rapids:
    • RMH → fast rapids (2s transit, high rate)
    • Thermosiphon → current (30s transit, moderate rate)  
    • Tank → deep pool (hours of residence, storage role)
    • Stirling → waterfall (3.7s transit, conversion point)
    • Cold sink → estuary (slow, vast, accepts all flow)
  
  The SYSTEM VELOCITY is the harmonic coupling:
    Ė_sys = 1 / Σ(1/Ė_i) = {system_velocity:,.0f} W thermal
    Electrical: {system_velocity * stirling_eff_elec:,.0f} W
    
  But the TANK makes this a RESIDENCE TIME problem, not just a rate problem.
  The tank is not a resistor — it's a capacitor (integrator).
  
  Proper analogy:
    RMH = current source (forced flow)
    Thermosiphon = conductor (passive flow, self-regulating)
    Tank = capacitor (stores charge, smooths ripple)
    Stirling = load (draws current, converts form)
    Cold sink = ground (accepts return current)
    
  SYSTEM VELOCITY = dE_elec/dt = Ė_source × Π(efficiencies)
    = {total_rmh:,.0f} × {stirling_eff_elec:.2f}
    = {total_rmh * stirling_eff_elec:,.0f} W electrical (MAX, all 6 RMHs)
    = {total_rmh * stirling_eff_elec / 1000:.1f} kW continuous
    
  This is the STEADY-STATE system velocity.
  Transients (startup, load changes) deviate but converge to this.
""")

# ============================================================
# SECTION 6: WHAT THIS MEANS FOR DESIGN
# ============================================================
print("=" * 80)
print("  SECTION 6: DESIGN IMPLICATIONS")
print("=" * 80)

print(f"""
  When you express EVERYTHING as rates [W]:
  
  1. BOTTLENECK ANALYSIS becomes trivial:
     Sort by rate, lowest = bottleneck. Done.
     
  2. OPTIMIZATION becomes multiplicative:
     System_eff = Π(stage_efficiencies)
     System_rate = min(stage_rates) [steady state]
     
  3. STORAGE adds a TIME dimension:
     Without storage: Ė_sys = min(rates) — instantaneous limit
     With storage: Ė_sys(t) can EXCEED min(rates) temporarily
     → Tank allows "burst mode" generation above RMH rate
     
  4. COALITION (your word) = COUPLING:
     When all nodes share units [W], you can:
       • Add them (parallel paths)
       • Take harmonic mean (series paths)  
       • Multiply by efficiency (conversion)
       • Integrate over time (storage)
       • Differentiate (transients)
       
  5. THE SYSTEM AS A WHOLE has a velocity:
     dE_out/dt = f(all_node_rates, all_storage_states)
     
     In steady state:  dE_out/dt = {total_rmh * stirling_eff_elec / 1000:.1f} kW
     With full tank burst: dE_out/dt = {total_stirling_thermal * stirling_eff_elec / 1000:.1f} kW
     Burst duration: {tank_energy / (total_stirling_thermal - total_rmh) / 3600:.1f}h
     (before RMH can't keep up and tank starts draining)
     
  6. The "velocity" you intuited IS REAL and is:
     v_sys = Ė_sys / (total thermal mass)  [K/s or J/s per J/K]
     
     = {steady_state_rate / tank_C:.10f} K/s (temperature rise rate)
     = {steady_state_rate / tank_C * 86400:.6f} K/day
     = {steady_state_rate / tank_C * 86400 * 365:.3f} K/year
     
     But with Stirlings drawing, the NET rate is:
     v_net = (total_rmh - total_stirling_thermal) / tank_C
     = {(total_rmh - total_stirling_thermal) / tank_C:.10f} K/s
     = {(total_rmh - total_stirling_thermal) / tank_C * 3600:.6f} K/hr
""")

# ============================================================
# FINAL ANSWER
# ============================================================
print("=" * 80)
print("  ANSWER TO YOUR QUESTION")
print("=" * 80)
print(f"""
  Q: "Can the system be understood as a velocity-type variable?"
  
  A: YES. The system has TWO velocities:
  
  1. FLOW VELOCITY (throughput rate):
     How fast energy moves from fuel to grid.
     Steady state: {total_rmh * stirling_eff_elec / 1000:.1f} kW electrical
     Burst mode:  {total_stirling_thermal * stirling_eff_elec / 1000:.1f} kW electrical
     
  2. STATE VELOCITY (rate of change):
     How fast the system's state (temperature) changes.
     Net charging: {(total_rmh - total_stirling_thermal) / tank_C * 3600:.4f} K/hr
     Full charge time: {tank_energy / (total_rmh - total_stirling_thermal) / 3600:.1f}h
     Full discharge: {tank_energy / total_stirling_thermal / 3600:.1f}h (no RMH)
     
  When you assign EVERY variable as a rate [W]:
  
  • Source rate: {total_rmh:,.0f} W (RMH combustion)
  • Transport rate: {transport_rate:,.0f} W (thermosiphon capacity)
  • Storage rate: {tank_energy/tank_energy*tank_C/tank_energy*charge_rate:,.0f} W (charge) / {discharge_rate:,.0f} W (discharge)
  • Conversion rate: {total_stirling_thermal:,.0f} W (Stirling draw)
  • Output rate: {total_rmh * stirling_eff_elec:,.0f} W (electrical)
  • Sink rate: {cold_discharge_power:,.0f} W (cold battery absorption)
  
  These form a COUPLED SET — like Kirchhoff's circuit laws —
  where energy is conserved at every node and the system velocity
  emerges from the interaction of all rates simultaneously.
  
  The COALITION you described is exactly this: every node
  contributes its rate to the whole, the whole is limited by
  the weakest contributor, and storage provides the buffer
  that decouples source rate from load rate.
  
  This IS a velocity. Not metaphorically — mathematically.
  dE/dt has units of [J/s = W] everywhere in the system.
  The system's "speed" is its power throughput.
  The system's "momentum" is its stored thermal energy.
  The system's "acceleration" is its net charging rate.
  
  Newton's second law analog:
    F = ma  →  Ė_net = C_thermal × (dT/dt)
    Force = mass × acceleration → Power = capacitance × temp_rate
    
  Your thermal system IS a dynamical system with velocity,
  momentum, and acceleration — all measurable in Watts.
""")
print("=" * 80)
