#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [THERMALV63] OpenRoot Optimal Balance v6.3 — HONEST+AUDITED
# Fixes over v6.2 (per audit 2026-09-24):
#   FIX1 geometry: spiral pitch must be >= channel dia + clearance (no self-intersecting coils)
#   FIX2 save: JSON actually written to disk (was stdout-only while claiming a save)
#   FIX3 capacity: 5 equivalent sun-hours/day (CF ~0.21), not 12h at 950 W/m2
#   FIX4 physics: selective coating (eps_thermal=0.10) on output + glazing (tau=0.88) on input
#   Plus: solver residual reported, fin efficiency uses computed h_air, 4.9 MPa hazard line
import json, math, os
from datetime import datetime

print("=" * 78)
print("  OPENROOT v6.3 — HONEST BALANCED SYSTEM (AUDITED)")
print(f"  Fix1 geometry | Fix2 real save | Fix3 sun-hours | Fix4 selectivity+glazing")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 78)

g, sigma = 9.81, 5.67e-8
cp_air, cp_concrete, L_fusion = 1005, 880, 334000

# Panel geometry
panel_L, panel_W = 5, 1
aperture = panel_L * panel_W
solar_flux = 950
absorption = 0.95
# FIX4: glazing transmission on INPUT, selective coating on OUTPUT
tau_cover = 0.88          # single glass cover, normal incidence
eps_thermal = 0.10        # selective surface thermal emissivity (NOT geometry)
solar_per_panel = solar_flux * aperture * absorption * tau_cover   # FIX4 input side

spiral_r = 0.35
friction_f = 0.025
emissivity = eps_thermal  # FIX4 output side

def compute_flow(n_ch, n_p, ch_d, chimney_h):
    # FIX1: pitch = channel dia + 1cm clearance; turns from REAL winding geometry
    pitch = ch_d + 0.01
    turns = max(1, int(panel_L / pitch))
    path_len = turns * 2 * math.pi * spiral_r
    channel_area = math.pi * (ch_d / 2) ** 2
    total_path = path_len * n_p
    rho_amb = 1.204
    mass_flow, total_flow = 0.05, 0.05 * n_ch

    final_temp, total_solar, residual = 20.0, 0.0, None
    for _ in range(200):
        T, total_solar = 20.0, 0
        for _p in range(n_p):
            T_surf = T + 20 + 20  # absorbed-surface + air temps approximated
            T_sky = 270
            q_rad = emissivity * sigma * ((T_surf + 273.15) ** 4 - T_sky ** 4) * aperture
            q_conv = 5 * (T_surf - 20 - 273.15 + 273.15 - 20) * aperture  # h_wind*(Ts-20)
            q_conv = 5 * (T_surf - 20) * aperture
            q_net = solar_per_panel - q_rad - q_conv
            if q_net <= 0:
                break
            T += q_net / (total_flow * cp_air)
            total_solar += q_net
        final_temp = T
        T_avg = (20 + final_temp) / 2
        rho_hot = rho_amb * (293.15 / (T_avg + 273.15))
        stack_h = n_p * 0.15 + chimney_h
        delta_P = (rho_amb - rho_hot) * g * stack_h
        velocity = total_flow / (n_ch * rho_hot * channel_area)
        delta_P_loss = friction_f * (total_path / ch_d) * (rho_hot * velocity ** 2 / 2) * 1.3
        if delta_P_loss > 0 and delta_P > 0:
            new_flow = rho_hot * channel_area * n_ch * \
                math.sqrt((2 * delta_P) / (friction_f * (total_path / ch_d) * rho_hot * 1.3))
            residual = abs(new_flow - total_flow) / total_flow
            total_flow = 0.5 * total_flow + 0.5 * new_flow
            if residual < 1e-4:
                break
    return total_flow, final_temp, total_solar, residual

def steam_hx_performance(air_temp, mass_flow, A_face=1.0, T_steam_sat=264):
    """Finned-tube coil, air side. Fin efficiency uses COMPUTED h_air (audit fix)."""
    T_air_in = air_temp
    tube_od, fin_height = 0.020, 0.015
    fin_thickness, fin_pitch, k_fin = 0.0004, 0.003, 200
    fins_per_m, tube_length = 1 / fin_pitch, 200

    r_tube = tube_od / 2; r_fin = r_tube + fin_height
    A_tube = math.pi * tube_od * tube_length
    A_fin_total = (2 * math.pi * (r_fin ** 2 - r_tube ** 2)) * fins_per_m * tube_length

    rho_air, mu_air, Pr = 1.2, 1.8e-5, 0.71
    v_air = mass_flow / (rho_air * A_face) if mass_flow > 0 else 0
    if v_air <= 0:
        return 0, T_air_in, 0, A_tube
    Re = rho_air * v_air * tube_od / mu_air
    j_H = 0.025 * Re ** (-0.2) if Re > 100 else 0.01
    h_air = j_H * cp_air * rho_air * v_air / Pr ** (2 / 3)

    # FIN EFFICIENCY WITH ACTUAL h_air (audit fix):
    m_param = math.sqrt(2 * h_air / (fin_thickness * k_fin)) if h_air > 0 else 0
    fin_eff = math.tanh(m_param * fin_height) / (m_param * fin_height) if m_param > 0 else 1.0
    A_effective = A_tube + A_fin_total * fin_eff
    A_total_report = A_tube + A_fin_total

    C_air = mass_flow * cp_air
    if C_air < 0.001:
        return 0, T_air_in, 0, A_total_report
    UA = h_air * A_effective
    if UA < 0.001:
        return 0, T_air_in, 0, A_total_report
    NTU = UA / C_air
    effectiveness = 1 - math.exp(-NTU)
    q_max = C_air * (T_air_in - T_steam_sat)
    if q_max <= 0:
        return 0, T_air_in, UA, A_total_report
    q_steam = effectiveness * q_max
    return q_steam, T_air_in - q_steam / C_air, UA, A_total_report

TARGET_TEMP, MIN_STEAM = 264, 4000
print(f"\n  TARGET: >={TARGET_TEMP}C air, >={MIN_STEAM}W steam, MINIMAL complexity")
print(f"  FIX4: solar input x tau_cover={tau_cover}; radiative loss eps={eps_thermal}")
print(f"  Steam HX: 200m finned-tube coil (20mm tubes + 15mm Al fins)")
print()

best_configs = []
for n_ch in range(4, 41, 4):
    for n_p in range(8, 25):
        for ch_d_cm in [5, 8, 10, 15, 20, 25, 30]:   # FIX1: thin channels now viable
            ch_d = ch_d_cm / 100
            for chimney in [6, 8, 10, 12, 15]:
                flow, temp, solar_cap, resid = compute_flow(n_ch, n_p, ch_d, chimney)
                if temp < TARGET_TEMP:
                    continue
                q_steam, T_out, UA, A_HX = steam_hx_performance(temp, flow)
                if q_steam < MIN_STEAM:
                    continue
                total_aperture = n_p * aperture
                electric = q_steam * 0.232
                eff = electric / solar_cap * 100 if solar_cap > 0 else 0
                complexity = n_ch * n_p * (ch_d_cm ** 2)
                best_configs.append({
                    'n_ch': n_ch, 'n_p': n_p, 'ch_d': ch_d, 'ch_d_cm': ch_d_cm,
                    'chimney': chimney, 'flow': flow, 'temp': temp, 'resid': resid,
                    'solar': solar_cap, 'q_steam': q_steam, 'T_out': T_out,
                    'UA': UA, 'A_HX': A_HX, 'electric': electric,
                    'eff': eff, 'complexity': complexity})

best_configs.sort(key=lambda x: x['complexity'])
print(f"  Found {len(best_configs)} configs meeting targets")
if not best_configs:
    print("\n  NO CONFIG MEETS TARGETS under audited physics.")
    print("  Options: relax MIN_STEAM, raise chimney, or add panels.")
    raise SystemExit(1)

print(f"\n  {'Ch':>3} {'Pan':>4} {'Dcm':>5} {'Chim':>5} {'Flow':>7} {'T_air':>6} "
      f"{'Steam':>8} {'Elec':>6} {'Eff%':>5} {'Cx':>6} {'conv':>6}")
for cfg in best_configs[:10]:
    print(f"  {cfg['n_ch']:>3} {cfg['n_p']:>4} {cfg['ch_d_cm']:>5} {cfg['chimney']:>5} "
          f"{cfg['flow']:>7.4f} {cfg['temp']:>6.0f} {cfg['q_steam']:>8,.0f} "
          f"{cfg['electric']:>6,.0f} {cfg['eff']:>5.1f} {cfg['complexity']:>6.0f} "
          f"{(cfg['resid'] or -1):>6.0%}")

best = best_configs[0]
n_p, n_ch, flow, temp = best['n_p'], best['n_ch'], best['flow'], best['temp']
solar_cap, q_steam, electric, eff = best['solar'], best['q_steam'], best['electric'], best['eff']
UA, A_HX, chimney, ch_d = best['UA'], best['A_HX'], best['chimney'], best['ch_d']
T_air_out, resid = best['T_out'], best['resid']
stack_h = n_p * 0.15 + chimney
total_aperture = n_p * aperture

T_hot_K, T_cold_K = 264 + 273.15, 20 + 273.15
carnot = (T_hot_K - T_cold_K) / T_hot_K
stirling_mech = carnot * 0.6
n_stirlings = max(1, int(q_steam / 2000))
stirling_draw = n_stirlings * 2000
reject_heat = stirling_draw * (1 - stirling_mech)
electric_gen = stirling_draw * stirling_mech * 0.85

# FIX3: honest capacity — 5 equivalent sun-hours (CF ~0.21 annualized incl. weather)
SUN_HOURS = 5
daily_kwh = electric_gen * SUN_HOURS / 1000
annual_mwh = daily_kwh * 365 / 1000
pv_kw = total_aperture * 950 * 0.20 / 1000
pv_daily = pv_kw * SUN_HOURS

# Cold battery
eff_cp_cold = cp_concrete + (L_fusion / 20)
q_rad_m2 = 0.9 * sigma * (273.15 ** 4 - 270 ** 4) + 200
lid_area = reject_heat / q_rad_m2 if q_rad_m2 > 0 else 1.0
night_kwh = q_rad_m2 * lid_area * 12 * 3600 / 3.6e6
day_kwh = reject_heat * 12 * 3600 / 3.6e6

print(f"\n{'='*78}")
print(f"  SELECTED CONFIG (minimal complexity at target, AUDITED PHYSICS)")
print(f"{'='*78}")
print(f"""
  PANELS: {n_p} x (5m x 1m) = {total_aperture} m2 aperture (glazed, tau={tau_cover})
  PARALLEL SPIRALS: {n_ch} per panel (D={ch_d*100:.0f}cm, pitch={ch_d*100+1:.0f}cm) [FIX1]
  CHIMNEY: {chimney}m | STACK HEIGHT: {stack_h:.1f}m
  FLOW: {flow:.4f} kg/s (thermosiphon; conv residual: {resid:.2%})
  AIR TEMP: 20C -> {temp:.0f}C
  SOLAR CAPTURED (post-glazing): {solar_cap:,.0f} W

  STEAM HX: UA={UA:,.0f} W/K | area={A_HX:,.0f} m2 | q_steam={q_steam:,.0f} W
  STIRLING: {n_stirlings} x 2kW | Carnot {carnot*100:.1f}% | elec gen {electric_gen:,.0f} W
  SOLAR-ELEC EFFICIENCY: {electric/solar_cap*100:.1f}% (peak, honest)

  ── FIX3 CAPACITY ACCOUNTING ──
  PEAK ELECTRIC: {electric_gen:,.0f} W ({electric_gen/1000:.2f} kW)
  DAILY: {daily_kwh:.1f} kWh (5 equiv sun-hours, NOT 12)
  ANNUAL: {annual_mwh:.2f} MWh
  PV BASELINE (same basis): {pv_daily:.1f} kWh/day — ratio: {daily_kwh/pv_daily:.2f}x

  COLD BATTERY: lid {lid_area:.1f} m2 ({math.sqrt(lid_area):.1f}m x {math.sqrt(lid_area):.1f}m)
    night recharge {night_kwh:.0f} kWh vs day reject {day_kwh:.0f} kWh
    {'BALANCED' if night_kwh >= day_kwh*0.9 else 'DEFICIT: enlarge lid'}

  !! HAZARD LINE (grant docs must carry this) !!
  Steam at 264C saturation = ~4.9 MPa (~50 bar). This is pressure-vessel
  territory: certified boiler tubing, relief valves, and inspection are
  NON-OPTIONAL. Amateur plumbing at 50 bar is a bomb.
""")

# FIX2: actually save
OUT_DIR = os.environ.get("OUT_DIR", "/storage/emulated/0/Documents/openroot-data")
fname = f"thermal_v63_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
payload = {
    "version": "THERMALV63", "timestamp": datetime.now().isoformat(),
    "audit_fixes": ["FIX1 spiral geometry", "FIX2 real save",
                    "FIX3 5 sun-hours CF", "FIX4 selective coating + glazing"],
    "panels": n_p, "parallel_channels": n_ch,
    "channel_diameter_cm": best['ch_d_cm'], "pitch_cm": best['ch_d_cm'] + 1,
    "chimney_height_m": chimney, "solver_residual": resid,
    "flow_kg_s": round(flow, 4), "exit_temp_C": round(temp, 1),
    "solar_captured_W": round(solar_cap), "steam_heat_W": round(q_steam),
    "peak_electric_W": round(electric_gen), "daily_kwh": round(daily_kwh, 1),
    "annual_MWh": round(annual_mwh, 2), "efficiency_percent_peak": round(eff, 1),
    "stirling_count": n_stirlings, "cold_battery_lid_m2": round(lid_area, 1),
    "hazard": "264C sat steam = ~4.9 MPa; pressure-vessel protocols mandatory",
}
saved_to = None
try:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, fname), "w") as fh:
        json.dump(payload, fh, indent=2)
    saved_to = os.path.join(OUT_DIR, fname)
except (PermissionError, OSError):
    OUT_DIR = "/data/data/com.termux/files/home/openroot/data"
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, fname), "w") as fh:
        json.dump(payload, fh, indent=2)
    saved_to = os.path.join(OUT_DIR, fname)

print(f"[banked] FIX2: config ACTUALLY saved -> {saved_to}")
print(json.dumps(payload, indent=2))
print("[exit=0] THERMALV63")
