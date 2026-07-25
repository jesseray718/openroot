#!/usr/bin/env python3
"""
OpenRoot Optimal Balance v6.1 — SELF-CONSISTENT FLOW
Fix: parallel spiral channels + iterative flow convergence
"""
import math

print("=" * 82)
print("  OPENROOT OPTIMAL BALANCE v6.1 — SELF-CONSISTENT")
print("  Parallel spiral channels + thermosiphon-flow convergence")
print("=" * 82)

g = 9.81
sigma = 5.67e-8
cp_air = 1005
cp_water = 4186
L_fusion = 334000

# ============================================================
# PANEL DESIGN
# ============================================================
panel_L = 5          # m
panel_W = 1          # m
aperture = panel_L * panel_W  # 5 m²
solar_flux = 950     # W/m²
absorption = 0.95
solar_per_panel = solar_flux * aperture * absorption  # 4512 W

# Spiral geometry
spiral_r = 0.35      # m
pitch = 0.04         # m
turns = int(panel_L / pitch)  # 125
path_len = turns * 2 * math.pi * spiral_r  # 274.9m
trap_factor = 0.25   # volumetric trapping
emissivity = 0.92

# ============================================================
# SELF-CONSISTENT FLOW SOLVER
# ============================================================
# The system must find the flow rate where:
#   Thermosiphon drive pressure = Friction losses through all panels
# This is an implicit equation — solve iteratively.

def compute_flow(n_parallel_channels, n_panels, channel_d, chimney_h, target_temp=264):
    """Find self-consistent mass flow through parallel spiral channels."""
    channel_area = math.pi * (channel_d/2)**2
    total_path = path_len * n_panels
    rho_amb = 1.204
    friction_f = 0.025
    
    # Iterate: guess flow → compute temps → compute densities → recompute flow
    mass_flow = 0.05  # initial guess kg/s per channel
    total_flow = mass_flow * n_parallel_channels
    
    for iteration in range(100):
        # Compute temperature cascade with current flow
        T = 20.0
        total_solar_captured = 0
        
        for p in range(n_panels):
            T_K = T + 273.15
            T_surface = 273.15 + 20 + (T_K - 273.15 - 20) * 0.4
            T_sky = 270
            q_rad = emissivity * sigma * (T_surface**4 - T_sky**4) * aperture * trap_factor
            h_wind = 5
            q_conv = h_wind * (T_surface - (20 + 273.15)) * aperture
            q_net = solar_per_panel - q_rad - q_conv
            
            if q_net <= 0:
                break
            
            dT = q_net / (total_flow * cp_air)
            T += dT
            total_solar_captured += q_net
        
        final_temp = T
        
        # Compute buoyancy with actual avg temperature
        T_avg = (20 + final_temp) / 2
        rho_hot = rho_amb * (293.15 / (T_avg + 273.15))
        
        # Stack height: panels + chimney
        stack_h = n_panels * 0.15 + chimney_h
        delta_P = (rho_amb - rho_hot) * g * stack_h
        
        # Friction through parallel channels
        # Each channel sees full path length, but flow splits N ways
        flow_per_channel = total_flow / n_parallel_channels
        velocity_per_channel = flow_per_channel / (rho_hot * channel_area)
        
        # Darcy-Weisbach: ΔP = f × (L/D) × (ρv²/2)
        delta_P_friction = friction_f * (total_path / channel_d) * (rho_hot * velocity_per_channel**2 / 2)
        
        # Minor losses (entrance, exit, bends) — add 30%
        delta_P_minor = 0.3 * delta_P_friction
        delta_P_total_loss = delta_P_friction + delta_P_minor
        
        # New flow: adjust toward equilibrium
        if delta_P_total_loss > 0:
            # Solve for flow that balances drive = loss
            # ΔP_buoyancy = f × (L/D) × (ρ × v²/2) × 1.3
            # v = sqrt(2 × ΔP_buoyancy / (f × (L/D) × ρ × 1.3))
            v_new = math.sqrt((2 * delta_P) / (friction_f * (total_path/channel_d) * rho_hot * 1.3))
            new_flow_per_channel = rho_hot * channel_area * v_new
            new_total = new_flow_per_channel * n_parallel_channels
            
            # Damping for convergence
            total_flow = 0.5 * total_flow + 0.5 * new_total
        else:
            break
    
    return total_flow, final_temp, total_solar_captured

# ============================================================
# SEARCH: Find optimal parallel channels + panel count + channel size
# ============================================================
print("\n  SEARCHING FOR SELF-CONSISTENT CONFIGURATION:")
print(f"  Target: 264°C (50-bar steam) with balanced thermosiphon flow\n")
print(f"  {'Ch':>3} {'Panel':>5} {'Dia(cm)':>8} {'Stack(m)':>8} {'Flow(kg/s)':>10} {'T_out(°C)':>10} {'Capture(W)':>10} {'Steam_in(W)':>11} {'Match':>6}")
print(f"  {'-'*3} {'-'*5} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*11} {'-'*6}")

best_config = None

for n_ch in range(4, 33, 4):       # 4, 8, 12, 16, 20, 24, 28, 32 parallel channels
    for n_p in range(8, 16):        # 8-15 panels
        for ch_d_cm in [8, 10, 12, 15, 20]:  # channel diameter
            ch_d = ch_d_cm / 100
            for chimney in [6, 8, 10, 12, 15]:
                flow, temp, solar_cap = compute_flow(n_ch, n_p, ch_d, chimney)
                
                if temp < 264:
                    continue
                
                # Heat to steam vessel
                T_steam = 264
                T_air_out_steam = T_steam - 10  # 254°C
                q_steam = flow * cp_air * (temp - T_air_out_steam)
                
                if q_steam < 500:
                    continue
                
                match = "OK" if abs(flow - 0.05) / 0.05 < 2.0 else "?"
                stack = n_p * 0.15 + chimney
                
                # Only print interesting configs
                if q_steam > 1000 and temp >= 264 and temp <= 320:
                    print(f"  {n_ch:>3} {n_p:>5} {ch_d_cm:>8} {stack:>8.1f} {flow:>10.4f} {temp:>10.1f} {solar_cap:>10,.0f} {q_steam:>11,.0f} {match:>6}")
                    
                    if best_config is None or q_steam > best_config['q_steam']:
                        # Check Stirling balance
                        stirling_each = 2000  # W thermal
                        n_stirlings = max(1, round(q_steam / stirling_each))
                        total_draw = n_stirlings * stirling_each
                        imbalance = q_steam - total_draw
                        
                        if abs(imbalance) < 1500:  # within 1.5kW
                            best_config = {
                                'n_ch': n_ch, 'n_p': n_p, 'ch_d': ch_d, 'chimney': chimney,
                                'flow': flow, 'temp': temp, 'solar': solar_cap,
                                'q_steam': q_steam, 'stack': stack,
                                'n_stirlings': n_stirlings, 'imbalance': imbalance
                            }

# ============================================================
# DETAILED ANALYSIS OF BEST CONFIG
# ============================================================
if best_config:
    bc = best_config
    n_p = bc['n_p']
    flow = bc['flow']
    temp = bc['temp']
    solar_cap = bc['solar']
    q_steam = bc['q_steam']
    
    # Recompute full cascade
    print(f"\n\n{'='*82}")
    print(f"  OPTIMAL CONFIGURATION FOUND:")
    print(f"{'='*82}")
    print(f"""
  PANELS: {n_p} × (5m × 1m) in series = {n_p * 5} m² total aperture
  PARALLEL CHANNELS: {bc['n_ch']} spirals per panel (channel ø={bc['ch_d']*100:.0f}cm)
  CHIMNEY: {bc['chimney']}m above panel stack
  TOTAL STACK HEIGHT: {bc['stack']:.1f}m
  SELF-CONSISTENT FLOW: {flow:.4f} kg/s (thermosiphon-balanced)
  EXIT TEMPERATURE: {temp:.1f}°C ({temp - 20:.0f}K rise from ambient)
  SOLAR CAPTURED: {solar_cap:,.0f} W ({solar_cap/1000:.1f} kW)
  HEAT TO STEAM VESSEL: {q_steam:,.0f} W ({q_steam/1000:.1f} kW)
""")

    # Stirling analysis
    T_hot_K = 264 + 273.15
    T_cold_K = 20 + 273.15
    carnot = (T_hot_K - T_cold_K) / T_hot_K
    stirling_mech = carnot * 0.6
    stirling_elec = stirling_mech * 0.85
    n_stir = bc['n_stirlings']
    stir_thermal = n_stir * 2000
    stir_elec = stir_thermal * stirling_elec
    stir_reject = stir_thermal * (1 - stirling_mech)
    
    # Labyrinth
    T_air_lab_in = 254
    T_air_lab_out = 25
    q_labyrinth = flow * cp_air * (T_air_lab_in - T_air_lab_out)
    porosity = 0.70
    pore_size = 0.003
    sa_density = 6 / pore_size * porosity
    h_oc = 25
    dT_lm = ((T_air_lab_in - 20) - (T_air_lab_out - 20)) / math.log(max((T_air_lab_in - 20) / (T_air_lab_out - 20), 1.01))
    A_contact = q_labyrinth / (h_oc * dT_lm)
    lab_vol = A_contact / sa_density
    bulk_dens = 1800 * (1 - porosity)
    lab_mass = lab_vol * bulk_dens
    lab_C = lab_mass * 880
    
    # Cold battery
    eff_cp_cold = cp_water + (L_fusion / 20)
    em_lid = 0.9
    T_lid_K = 273.15
    T_sky_K = 270
    q_rad_m2 = em_lid * sigma * (T_lid_K**4 - T_sky_K**4)
    q_conv_gain = 3 * (20 - 0)  # 60 W/m² warming
    q_evap = 200  # W/m² evaporative boost
    q_net_cold = q_rad_m2 - q_conv_gain + q_evap
    lid_area = stir_reject / q_net_cold
    reject_12h = stir_reject * 12 * 3600
    cold_mass = reject_12h / (eff_cp_cold * 20)
    night_cool = q_net_cold * lid_area * 12 * 3600
    
    total_thermal_mass = lab_C + (cold_mass * eff_cp_cold)
    sys_rate = min(q_steam, stir_thermal, stir_reject, q_labyrinth)
    coast_time = (total_thermal_mass * 20) / sys_rate / 3600
    
    print(f"""  ┌──────────────────────────────────────────────────────────────────┐
  │  BALANCED SYSTEM — SELF-CONSISTENT THERMOSIPHON FLOW            │
  ├──────────────────────────────────────────────────────────────────┤
  │                                                                  │
  │  SOLAR COLLECTION:                                               │
  │    Panels: {n_p} × (5m × 1m) = {n_p*5} m² aperture                      │
  │    Parallel spirals: {bc['n_ch']} per panel (ø={bc['ch_d']*100:.0f}cm)                │
  │    Flow: {flow:.4f} kg/s (natural thermosiphon, converged)           │
  │    Air temp: 20°C → {temp:.0f}°C                                      │
  │    Solar captured: {solar_cap:,.0f} W ({solar_cap/1000:.1f} kW)               │
  │                                                                  │
  │  STEAM VESSEL:                                                   │
  │    50 bar / {264}°C saturation                                    │
  │    Heat input: {q_steam:,.0f} W ({q_steam/1000:.1f} kW)                       │
  │                                                                  │
  │  STIRLING: {n_stir} × 2kW thermal                                     │
  │    Carnot: {carnot*100:.1f}% | Elec: {stirling_elec*100:.1f}%                       │
  │    Draw: {stir_thermal:,.0f}W | Elec: {stir_elec:,.0f}W ({stir_elec/1000:.2f}kW)        │
  │    Reject: {stir_reject:,.0f}W ({stir_reject/1000:.1f}kW)                        │
  │    Imbalance: {bc['imbalance']:+.0f}W                                       │
  │                                                                  │
  │  LABYRINTH:                                                      │
  │    Volume: {lab_vol:.2f} m³ | Mass: {lab_mass:.0f} kg                      │
  │    Heat extracted: {q_labyrinth:,.0f}W ({q_labyrinth/1000:.1f}kW)             │
  │                                                                  │
  │  COLD BATTERY:                                                   │
  │    Mass: {cold_mass:.0f} kg | Lid: {lid_area:.0f} m² ({math.sqrt(lid_area):.0f}m × {math.sqrt(lid_area):.0f}m)    │
  │    Night recharge: {night_cool/3.6e6:.0f} kWh vs day reject: {reject_12h/3.6e6:.0f} kWh  │
  │    Balance: {'✅' if night_cool >= reject_12h else '⚠'}                                    │
  │                                                                  │
  │  ══════════════════════════════════════════════════════════      │
  │  SYSTEM VELOCITY:                                                │
  │    Solar → Air:     {solar_cap:>8,.0f} W                        │
  │    Air → Steam:     {q_steam:>8,.0f} W                        │
  │    Steam → Stirling:{stir_thermal:>8,.0f} W                        │
  │    Stirling → Elec: {stir_elec:>8,.0f} W                        │
  │    Stirling → Cold: {stir_reject:>8,.0f} W                        │
  │    Air → Labyrinth: {q_labyrinth:>8,.0f} W                        │
  │    Cold → Space:    {q_net_cold*lid_area:>8,.0f} W                        │
  │                                                                  │
  │  BALANCED RATE: {sys_rate:.0f} W ({sys_rate/1000:.1f} kW)                  │
  │  ELECTRICAL: {stir_elec:.0f}W ({stir_elec/1000:.2f} kW) continuous (sun hours)      │
  │  DAILY: {stir_elec*12/1000:.1f} kWh | ANNUAL: {stir_elec*12*365/1e6:.2f} MWh              │
  │  COAST TIME: {coast_time:.1f}h after sunset                            │
  │                                                                  │
  │  KEY: {bc['n_ch']} parallel spirals solve the friction problem.     │
  │  Each spiral keeps 275m path + vortex effect, but flow splits   │
  │  {bc['n_ch']} ways → friction drops {bc['n_ch']}× while heat transfer stays     │
  │  high. Thermosiphon now self-consistently drives the flow.      │
  └──────────────────────────────────────────────────────────────────┘
""")
else:
    print("\n  ⚠ No balanced configuration found in search space.")
    print("  Try expanding search or adjusting parameters.")
    
print("=" * 82)
