#!/usr/bin/env python3
"""
H-003 THERMAL CASCADE — SINGLE-PANEL RESONANT CIRCUIT SOLVER v0.1
=================================================================
One panel. One spiral. Full circuit. No waste.

CIRCUIT:
  SUN → [PANEL] → HOT AIR → [HEAT TAP] → [LABYRINTH] → [STEAM VESSEL]
                                                         → [STIRLING]
                                                           → [FLYWHEEL]
                                                             → [BELT+CLUTCH]
                                                               ├── MECH TOOLS
                                                               └── ALTERNATOR → ELEC
                                                  ↓ reject
                                            [COLD BATTERY] → COLD USE
                                                  ↑ recharge
                                            [RADIATIVE LID] → SKY/SPACE

η_sys = (Q_heat + Q_cold + W_mech + W_elec) / Q_solar × η_coupling × infra_factor
"""

import math

# ============================================================
# CONSTANTS
# ============================================================
G           = 9.81
R_AIR       = 287.05
CP_AIR      = 1005.0
CP_CONCRETE = 880.0
RHO_DENSE   = 2400.0
RHO_AERATED = 500.0
SIGMA       = 5.67e-8
H_VAP       = 2.257e6
MU_AIR      = 1.81e-5
T_AMB       = 293.15
T_SKY       = 253.0
I_PEAK      = 1000.0
DAY_HRS     = 14.5
NIGHT_HRS   = 24.0 - DAY_HRS

# ============================================================
# HELPERS
# ============================================================
def rho_air(T):
    return 101325.0 / (R_AIR * T)

def friction_factor(Re):
    if Re < 1: return 64.0
    if Re < 2300: return 64.0 / Re
    return 0.316 * Re**(-0.25)

def stefan_boltzmann(T_surf, T_sink, emis, area):
    return emis * SIGMA * area * (T_surf**4 - T_sink**4)

def solar_curve(hour, peak=I_PEAK, day_hrs=DAY_HRS):
    sunrise = (24 - day_hrs) / 2
    sunset = sunrise + day_hrs
    if hour < sunrise or hour > sunset:
        return 0.0
    frac = (hour - sunrise) / day_hrs
    return peak * math.sin(math.pi * frac)

# ============================================================
# PANEL — Single spiral, volumetric blackbody
# ============================================================
class Panel:
    def __init__(self, length=5.0, width=1.0, ch_d=0.08,
                 absorption=0.96, porosity_drag=3.0):
        self.L = length
        self.W = width
        self.D = ch_d
        self.alpha = absorption
        self.porosity_drag = porosity_drag
        spacing = ch_d * 1.5
        self.n_passes = max(1, int(width / spacing))
        self.path_len = self.n_passes * length
        self.A_cs = math.pi * ch_d**2 / 4.0
        self.r_curv = width / (2 * math.pi) if self.n_passes > 1 else length / 4
        self.area = length * width

    def solve_thermosiphon(self, irradiance, stack_h):
        Q_solar = self.alpha * irradiance * self.area
        D, L, A_cs = self.D, self.path_len, self.A_cs
        mdot = 0.002
        converged = False
        for _ in range(500):
            if mdot < 1e-9: mdot = 1e-9
            T_out = T_AMB + Q_solar / (mdot * CP_AIR)
            T_avg = (T_AMB + T_out) / 2.0
            ra, ro, rn = rho_air(T_avg), rho_air(T_out), rho_air(T_AMB)
            v = mdot / (ra * A_cs)
            Re = ra * v * D / MU_AIR
            f = friction_factor(Re)
            De = Re * math.sqrt(D / (2 * self.r_curv)) if self.r_curv > D else 0
            spiral_boost = 1.0 + 0.14 * math.sqrt(max(De, 0))
            f_eff = f * spiral_boost * self.porosity_drag
            dp_fric = f_eff * (L / D) * (ra * v**2 / 2.0)
            dp_minor = 3.0 * (ra * v**2 / 2.0)
            dp_loss = dp_fric + dp_minor
            dp_buoy = G * stack_h * (rn - ro)
            if dp_buoy <= 0 or dp_loss <= 0:
                mdot *= 0.5; continue
            ratio = dp_buoy / dp_loss
            if abs(ratio - 1.0) < 1e-5:
                converged = True; break
            mdot *= 1.0 + 0.3 * (ratio - 1.0)
            mdot = max(mdot, 1e-9)
        T_out = T_AMB + Q_solar / (max(mdot, 1e-9) * CP_AIR)
        return mdot, T_out, v, Re, converged, Q_solar

# ============================================================
# CIRCUIT NODES
# ============================================================

def heat_tap(Q_air, fraction=0.15):
    """Direct heat: cooking, drying, water heating. Zero conversion loss."""
    return Q_air * fraction, Q_air * (1 - fraction)

def labyrinth(Q_in, volume, rho=RHO_AERATED, cp=CP_CONCRETE, eff=0.80):
    """Porous open-cell storage. Air deposits heat in volumetric pores."""
    mass = volume * rho
    Q_stored = Q_in * eff
    Q_pass = Q_in - Q_stored
    T_storage = T_AMB + (Q_stored * 3600) / (mass * cp)
    return Q_stored, Q_pass, T_storage, mass

def steam_vessel(Q_in, T_source, P_bar=50.0):
    """Thermal transformer: hot storage -> pressurized steam."""
    T_sat = 100.0 * (P_bar / 1.01325)**0.25 + 273.15
    if T_source < T_sat + 10:
        return 0, T_sat, False
    eff_hx = 0.85
    return Q_in * eff_hx, T_sat, True

def stirling(Q_in, T_hot, T_cold):
    """Thermal -> Mechanical. Carnot ceiling x real efficiency."""
    if T_hot <= T_cold or Q_in <= 0:
        return 0, 0, 0, 0, False
    eta_carnot = 1.0 - T_cold / T_hot
    eta_real = eta_carnot * 0.45
    W = Q_in * eta_real
    Q_reject = Q_in - W
    return W, Q_reject, eta_carnot, eta_real, True

def flywheel(P_in, charge_hrs=6.0, mass=50.0, radius=0.4):
    """Mechanical accumulator. Slow build -> high torque burst."""
    I = 0.5 * mass * radius**2
    E = P_in * charge_hrs * 3600
    omega = math.sqrt(2 * E / I) if I > 0 and E > 0 else 0
    rpm = omega * 60 / (2 * math.pi)
    burst_30s = E / 30.0 if E > 0 else 0
    torque = I * omega / 30.0 if omega > 0 else 0
    return E, I, rpm, burst_30s, torque

def belt_alternator(W_cont, priority='mechanical', belt_eff=0.96, alt_eff=0.88):
    """Power split: tools first, electricity from remainder."""
    frac = 0.70 if priority == 'mechanical' else 0.30
    W_tools = W_cont * frac * belt_eff
    W_alt = W_cont * (1 - frac) * belt_eff
    W_elec = W_alt * alt_eff
    return W_tools, W_elec

def cold_battery(Q_reject, mass=200.0, cp=CP_CONCRETE, lid_area=16.0, emis=0.92):
    """Sink + cold storage. Day: absorbs reject. Night: radiative recharge."""
    C = mass * cp
    dT_day = (Q_reject * DAY_HRS * 3600) / C if C > 0 else 0
    T_night_start = T_AMB + dT_day
    P_rad = stefan_boltzmann(T_night_start, T_SKY, emis, lid_area)
    Q_overnight = P_rad * NIGHT_HRS * 3600
    dT_night = Q_overnight / C if C > 0 else 0
    net_dT = dT_day - dT_night
    T_cold = T_AMB + net_dT
    Q_cold = max(0, (T_AMB - T_cold) * C / (24 * 3600))
    balanced = abs(net_dT) < 5.0
    return {
        'mass': mass, 'C': C, 'dT_day': dT_day, 'dT_night': dT_night,
        'net_dT': net_dT, 'T_cold': T_cold, 'Q_cold': Q_cold,
        'P_rad': P_rad, 'Q_overnight_kWh': Q_overnight / 3.6e6,
        'balanced': balanced, 'lid_area': lid_area,
    }

# ============================================================
# COUPLING — impedance matching at each interface
# ============================================================
def coupling(params, panel_r, heat_Q, lab_r, steam_r, stir_r, cold_r):
    c1 = min(1.0, panel_r['T_rise'] / 200.0)
    c2 = min(1.0, heat_Q[1] / max(panel_r['Q_solar'], 1))
    if steam_r[2]:
        c3 = min(1.0, lab_r[2] / (steam_r[1] * 1.2))
    else:
        c3 = 0.3
    if stir_r[4]:
        dT = stir_r[5] - stir_r[6]
        c4 = min(1.0, dT / 300.0)
    else:
        c4 = 0.1
    c5 = min(1.0, cold_r['P_rad'] / max(stir_r[1], 1)) if stir_r[1] > 0 else 0.5
    c6 = 1.0 if cold_r['balanced'] else max(0, 1 - abs(cold_r['net_dT']) / 50)
    eta_coup = c1 * c2 * c3 * c4 * c5 * c6
    labels = [('Panel->Heat',c1),('Heat->Lab',c2),('Lab->Steam',c3),
              ('Steam->Stirling',c4),('Stirling->Cold',c5),('Cold->Sky',c6)]
    return eta_coup, labels

# ============================================================
# FULL CIRCUIT EVALUATION
# ============================================================
def evaluate(p):
    panel = Panel(length=p['panel_L'], width=p['panel_W'],
                  ch_d=p['ch_d'], absorption=p['alpha'],
                  porosity_drag=p['porosity_drag'])

    mdot, T_out, v, Re, conv, Q_solar = panel.solve_thermosiphon(I_PEAK, p['stack_h'])
    T_rise = T_out - T_AMB

    Q_heat, Q_after = heat_tap(Q_solar, p['heat_frac'])
    Q_stored, Q_pass, T_storage, lab_mass = labyrinth(
        Q_after, p['lab_vol'], eff=p['lab_eff'])
    Q_steam, T_sat, steam_ok = steam_vessel(Q_stored, T_storage, p['P_bar'])

    T_hot = T_sat if steam_ok else T_storage
    T_cold = T_AMB
    W_mech, Q_reject, eta_carnot, eta_stirling, running = stirling(
        Q_steam, T_hot, T_cold)

    cold = cold_battery(Q_reject, mass=p['cold_mass'], lid_area=p['lid_area'])
    T_cold_real = cold['T_cold']

    if running:
        W_mech, Q_reject, eta_carnot, eta_stirling, running = stirling(
            Q_steam, T_hot, T_cold_real)

    E_fw, I_fw, rpm_fw, burst_fw, torque_fw = flywheel(
        W_mech, charge_hrs=p['fw_charge_hrs'],
        mass=p['fw_mass'], radius=p['fw_radius'])

    W_tools, W_elec = belt_alternator(W_mech, priority='mechanical')

    panel_r = {'T_rise': T_rise, 'Q_solar': Q_solar}
    heat_r = (Q_heat, Q_after)
    lab_r = (Q_stored, Q_pass, T_storage, lab_mass)
    steam_r = (Q_steam, T_sat, steam_ok)
    stir_r = (W_mech, Q_reject, eta_carnot, eta_stirling, running, T_hot, T_cold_real)
    eta_coup, couplings = coupling(p, panel_r, heat_r, lab_r, steam_r, stir_r, cold)

    panel_mass = panel.area * 0.05 * RHO_AERATED
    total_mass = lab_mass + cold['mass'] + p['fw_mass'] + panel_mass

    Q_cold_use = cold['Q_cold']
    total_output = Q_heat + Q_cold_use + W_tools + W_elec

    eta_raw = total_output / Q_solar if Q_solar > 0 else 0
    infra_factor = min(1000.0 / max(total_mass, 100.0), 2.0)
    eta_sys = eta_raw * eta_coup * infra_factor

    E_daily_elec = W_elec * DAY_HRS / 1000.0
    E_daily_mech = W_tools * DAY_HRS / 1000.0
    E_daily_heat = Q_heat * DAY_HRS / 1000.0
    E_daily_cold = Q_cold_use * 24 / 1000.0
    E_daily_total = E_daily_elec + E_daily_mech + E_daily_heat + E_daily_cold
    E_annual = E_daily_total * 365 / 1000.0

    lab_energy = Q_stored * DAY_HRS * 3600
    coast_hours = lab_energy / (Q_steam * 3600) if Q_steam > 0 else 0

    return {
        'eta_sys': eta_sys, 'eta_raw': eta_raw, 'eta_coupling': eta_coup,
        'eta_carnot': eta_carnot, 'eta_stirling': eta_stirling,
        'infra_factor': infra_factor, 'couplings': couplings,
        'Q_solar': Q_solar, 'mdot': mdot, 'T_out': T_out,
        'T_out_C': T_out - 273.15, 'T_rise': T_rise, 'v': v, 'Re': Re,
        'converged': conv, 'Q_heat': Q_heat, 'Q_cold': Q_cold_use,
        'W_mech': W_mech, 'W_tools': W_tools, 'W_elec': W_elec,
        'Q_reject': Q_reject, 'total_output': total_output,
        'total_mass': total_mass, 'T_storage': T_storage, 'T_sat': T_sat,
        'steam_ok': steam_ok, 'stirling_running': running,
        'flywheel_E_kWh': E_fw / 3.6e6, 'flywheel_rpm': rpm_fw,
        'flywheel_burst_W': burst_fw, 'flywheel_torque': torque_fw,
        'cold': cold, 'E_daily_elec': E_daily_elec, 'E_daily_mech': E_daily_mech,
        'E_daily_heat': E_daily_heat, 'E_daily_cold': E_daily_cold,
        'E_daily_total': E_daily_total, 'E_annual_MWh': E_annual,
        'coast_hours': coast_hours, 'path_len': panel.path_len,
        'n_passes': panel.n_passes, 'lab_mass': lab_mass, 'params': p,
    }

# ============================================================
# PARAMETER SWEEP
# ============================================================
def sweep():
    base = {
        'panel_L': 5.0, 'panel_W': 1.0,
        'alpha': 0.96, 'porosity_drag': 3.0,
        'heat_frac': 0.15, 'lab_eff': 0.80,
        'P_bar': 50.0,
        'fw_charge_hrs': 6.0, 'fw_mass': 50.0, 'fw_radius': 0.4,
        'cold_mass': 200.0, 'lid_area': 16.0,
    }
    results = []
    for ch_d in [0.04, 0.06, 0.08, 0.10, 0.12, 0.15]:
        for stack_h in [3, 5, 8, 10, 12]:
            for lab_vol in [0.5, 1.0, 2.0, 4.0, 8.0]:
                for cold_mass in [100, 200, 300, 500]:
                    for lid_area in [4, 9, 16, 25, 36]:
                        p = dict(base)
                        p.update({'ch_d': ch_d, 'stack_h': stack_h,
                                  'lab_vol': lab_vol,
                                  'cold_mass': cold_mass, 'lid_area': lid_area})
                        r = evaluate(p)
                        if r['converged'] and r['stirling_running'] and r['Q_solar'] > 0:
                            results.append(r)
    results.sort(key=lambda r: r['eta_sys'], reverse=True)
    return results

# ============================================================
# DISPLAY
# ============================================================
def display(r, rank=None):
    p = r['params']
    c = r['cold']
    sep = "=" * 72
    tag = f"  RANK #{rank}" if rank else ""

    print(sep)
    print("  H-003 RESONANT CIRCUIT — SINGLE PANEL, ONE SPIRAL")
    print("  Max η_sys / Min Infrastructure — Every Joule Gets a Job")
    print(tag)
    print(sep)

    print(f"""
  ┌──────────────────────────────────────────────────────────────────┐
  │  PANEL (Source)                                                 │
  │    Size: {p['panel_L']:.0f}m × {p['panel_W']:.0f}m = {p['panel_L']*p['panel_W']:.0f} m² aperture                        │
  │    Spiral: 1 channel, ø={p['ch_d']*100:.0f}cm, {r['path_len']:.0f}m path, {r['n_passes']} passes              │
  │    Absorption: {p['alpha']*100:.0f}%  |  Porosity drag: {p['porosity_drag']:.0f}x                       │
  │    Stack height: {p['stack_h']:.0f}m (chimney buoyancy)                     │
  │    Flow: {r['mdot']:.5f} kg/s  |  Velocity: {r['v']:.3f} m/s  |  Re: {r['Re']:.0f}     │
  │    Air temp: 20°C → {r['T_out_C']:.0f}°C ({r['T_rise']:.0f}K rise)                  │
  │    Solar captured: {r['Q_solar']:,.0f} W ({r['Q_solar']/1000:.2f} kW)                   │
  │    Thermosiphon: {'CONVERGED ✓' if r['converged'] else 'FAILED ✗'}                             │
  ├──────────────────────────────────────────────────────────────────┤
  │  HEAT TAP (Direct Use — zero conversion loss)                   │
  │    Fraction: {p['heat_frac']*100:.0f}% of solar                                   │
  │    Output: {r['Q_heat']:,.0f} W ({r['Q_heat']/1000:.2f} kW) direct heat                   │
  │    Cooking, drying, water heating, process heat                 │
  ├──────────────────────────────────────────────────────────────────┤
  │  LABYRINTH (Hot Storage Cap)                                    │
  │    Volume: {p['lab_vol']:.1f} m³  |  Mass: {r['lab_mass']:.0f} kg aerated concrete       │
  │    Capture eff: {p['lab_eff']*100:.0f}%  |  Stored: {r['Q_heat'*(1-p['heat_frac'])*p['lab_eff']/1000:.2f} kW   │
  │    Storage temp: {r['T_storage']-273.15:.0f}°C                               │
  │    Remaining to steam: {(r['Q_solar']-r['Q_heat'])*(1-p['lab_eff']):,.0f} W              │
  ├──────────────────────────────────────────────────────────────────┤
  │  STEAM VESSEL (Thermal Transformer)                             │
  │    Pressure: {p['P_bar']:.0f} bar  |  Saturation: {r['T_sat']-273.15:.0f}°C                  │
  │    Heat to steam: {r['Q_solar']*(1-p['heat_frac'])*p['lab_eff']*0.85:,.0f} W                  │
  │    Status: {'ONLINE ✓' if r['steam_ok'] else 'OFFLINE ✗'}                                    │
  ├──────────────────────────────────────────────────────────────────┤
  │  STIRLING (Thermal → Mechanical)                                │
  │    Hot side: {r['T_sat']-273.15:.0f}°C  |  Cold side: {c['T_cold']-273.15:.0f}C                   │
  │    Carnot: {r['eta_carnot']*100:.1f}%  |  Real: {r['eta_stirling']*100:.1f}%                        │
  │    Mechanical: {r['W_mech']:,.0f} W ({r['W_mech']/1000:.2f} kW) shaft                    │
  │    Reject to cold: {r['Q_reject']:,.0f} W ({r['Q_reject']/1000:.2f} kW)                  │
  ├──────────────────────────────────────────────────────────────────┤
  │  FLYWHEEL (Slow Build → High Torque Burst)                      │
  │    Mass: {p['fw_mass']:.0f} kg  |  Radius: {p['fw_radius']:.1f}m  |  Charge: {p['fw_charge_hrs']:.0f}h         │
  │    Stored: {r['flywheel_E_kWh']:.2f} kWh  |  RPM: {r['flywheel_rpm']:.0f}                       │
  │    30s burst: {r['flywheel_burst_W']:,.0f} W ({r['flywheel_burst_W']/1000:.1f} kW)               │
  │    Torque: {r['flywheel_torque']:.1f} N·m                                  │
  ├──────────────────────────────────────────────────────────────────┤
  │  BELT + CLUTCH (Power Split — no waste)                         │
  │    Priority: MECHANICAL FIRST                                   │
  │    To tools: {r['W_tools']:,.0f} W ({r['W_tools']/1000:.2f} kW) direct shaft               │
  │    To alternator: {r['W_elec']/0.88:,.0f} W → {r['W_elec']:,.0f} W ({r['W_elec']/1000:.2f} kW) elec   │
  │    Mill, pump, compressor, press — no generator conversion loss │
  ├──────────────────────────────────────────────────────────────────┤
  │  COLD BATTERY (Sink + Cold Storage)                             │
  │    Mass: {c['mass']:.0f} kg  |  Lid: {c['lid_area']:.0f} m² ({math.sqrt(c['lid_area']):.0f}m × {math.sqrt(c['lid_area']):.0f}m)       │
  │    Day heating: +{c['dT_day']:.1f}K  |  Night cooling: -{c['dT_night']:.1f}K              │
  │    Net drift: {c['net_dT']:+.1f}K  |  {'BALANCED ✓' if c['balanced'] else 'DRIFTING ⚠'}              │
  │    Radiative power: {c['P_rad']:,.0f} W  |  Overnight: {c['Q_overnight_kWh']:.1f} kWh     │
  │    Cold usable: {r['Q_cold']:,.0f} W ({r['Q_cold']/1000:.3f} kW) refrigeration              │
  ├──────────────────────────────────────────────────────────────────┤
  │  COUPLING (Impedance Match at Each Interface)                   │""")
    
    for label, val in r['couplings']:
        bar = '█' * int(val * 20)
        print(f"  │    {label:20s} {val:.2f} {bar:<20s}{'│'}")

    print(f"""  │    Product: {r['eta_coupling']:.3f}                                      │
  ├──────────────────────────────────────────────────────────────────┤
  │  SYSTEM COEFFICIENT                                             │
  │    η_raw:     {r['eta_raw']*100:.1f}%  (total output / solar input)             │
  │    η_couple:  {r['eta_coupling']:.3f}  (interface impedance match)           │
  │    infra:     {r['infra_factor']:.3f}  (kg penalty: {r['total_mass']:.0f} kg total)              │
  │    ─────────────────────────────                                  │
  │    η_sys:     {r['eta_sys']:.4f}  ← MAXIMIZE THIS                  │
  ├──────────────────────────────────────────────────────────────────┤
  │  ENERGY BUDGET (Daily)                                          │
  │    Heat:     {r['E_daily_heat']:.2f} kWh  (cooking, drying, hot water)         │
  │    Cold:     {r['E_daily_cold']:.2f} kWh  (refrigeration, space cooling)       │
  │    Mech:     {r['E_daily_mech']:.2f} kWh  (tools, pumps, mill, press)         │
  │    Elec:     {r['E_daily_elec']:.2f} kWh  (lights, comms, charging)           │
  │    TOTAL:    {r['E_daily_total']:.2f} kWh/day                          │
  │    ANNUAL:   {r['E_annual_MWh']:.2f} MWh/yr                           │
  │    COAST:    {r['coast_hours']:.1f}h after sunset (labyrinth storage)       │
  ├──────────────────────────────────────────────────────────────────┤
  │  MASS BUDGET                                                    │
  │    Panel:     {p['panel_L']*p['panel_W']*0.05*RHO_AERATED:.0f} kg  (aerated concrete, 5cm)              │
  │    Labyrinth: {r['lab_mass']:.0f} kg  (open-cell porous storage)           │
  │    Cold batt: {c['mass']:.0f} kg  (thermal mass + radiative lid)          │
  │    Flywheel:  {p['fw_mass']:.0f} kg  (mechanical accumulator)             │
  │    TOTAL:     {r['total_mass']:.0f} kg                              │
  └──────────────────────────────────────────────────────────────────┘

  CIRCUIT DIAGRAM (Energy Flow):

    SUN ({r['Q_solar']:,.0f}W)
     │
     ▼
    [PANEL] ──{r['mdot']:.4f} kg/s──► {r['T_out_C']:.0f}°C air
     │
     ├──► [HEAT TAP] ──► {r['Q_heat']:,.0f}W direct heat (cooking/drying)
     │
     ▼
    [LABYRINTH] ──► {p['lab_vol']:.1f}m³, {r['T_storage']-273.15:.0f}°C storage
     │
     ▼
    [STEAM VESSEL] ──► {p['P_bar']:.0f}bar, {r['T_sat']-273.15:.0f}°C
     │
     ▼
    [STIRLING] ──► {r['W_mech']:,.0f}W mechanical
     │          └─► {r['Q_reject']:,.0f}W reject
     ▼
    [FLYWHEEL] ──► {r['flywheel_E_kWh']:.2f} kWh stored
     │
     ├──► [BELT+CLUTCH] ──► {r['W_tools']:,.0f}W to tools (direct shaft)
     └──► [ALTERNATOR]  ──► {r['W_elec']:,.0f}W electrical
     
    [STIRLING REJECT] ──► [COLD BATTERY] ──► {r['Q_cold']:,.0f}W cold use
                                   └──► [RADIATIVE LID] ──► DEEP SPACE (recharge)

  No waste. Every joule gets a job.
""")

def display_top(results, n=10):
    print("=" * 72)
    print("  H-003 RESONANT CIRCUIT SOLVER — TOP CONFIGURATIONS")
    print("  Single Panel, One Spiral — Sweeping for Maximum η_sys")
    print("=" * 72)
    print()
    
    hdr = f"  {'Rank':<5} {'ch_cm':<6} {'stk_m':<6} {'lab_m3':<7} {'cold_kg':<8} {'lid_m2':<7} {'η_sys':<8} {'η_raw':<7} {'η_coup':<7} {'W_mech':<7} {'W_elec':<7} {'kg_tot':<7}"
    print(hdr)
    print("  " + "-" * 68)
    
    for i, r in enumerate(results[:n]):
        p = r['params']
        row = (f"  {i+1:<5} {p['ch_d']*100:<6.0f} {p['stack_h']:<6.0f} "
               f"{p['lab_vol']:<7.1f} {p['cold_mass']:<8.0f} {p['lid_area']:<7.0f} "
               f"{r['eta_sys']:<8.4f} {r['eta_raw']*100:<7.1f} {r['eta_coupling']:<7.3f} "
               f"{r['W_mech']:<7.0f} {r['W_elec']:<7.0f} {r['total_mass']:<7.0f}")
        print(row)
    print()

if __name__ == '__main__':
    import sys
    print("Sweeping parameter space...")
    print("  ch_d: 4-15cm | stack: 3-12m | lab: 0.5-8m³ | cold: 100-500kg | lid: 4-36m²")
    print()
    
    results = sweep()
    
    if not results:
        print("No converged configurations found. Expanding search...")
        # Fallback: relax constraints
        base = {
            'panel_L': 5.0, 'panel_W': 1.0, 'alpha': 0.96, 'porosity_drag': 2.0,
            'heat_frac': 0.10, 'lab_eff': 0.70, 'P_bar': 30.0,
            'fw_charge_hrs': 6.0, 'fw_mass': 50.0, 'fw_radius': 0.4,
        }
        for ch_d in [0.06, 0.08, 0.10, 0.12]:
            for stack_h in [5, 8, 10, 12, 15]:
                for lab_vol in [1.0, 2.0, 4.0]:
                    for cold_mass in [200, 300]:
                        for lid_area in [9, 16, 25]:
                            p = dict(base)
                            p.update({'ch_d': ch_d, 'stack_h': stack_h,
                                      'lab_vol': lab_vol,
                                      'cold_mass': cold_mass, 'lid_area': lid_area})
                            r = evaluate(p)
                            if r['converged'] and r['Q_solar'] > 0:
                                results.append(r)
        results.sort(key=lambda r: r['eta_sys'], reverse=True)
    
    if results:
        display_top(results, n=15)
        print("=" * 72)
        print("  OPTIMAL CONFIGURATION — FULL DETAIL")
        print("=" * 72)
        display(results[0], rank=1)
        
        # Show 2nd and 3rd for comparison
        if len(results) > 1:
            print("\n  " + "=" * 72)
            print("  RUNNER-UP #2")
            print("  " + "=" * 72)
            display(results[1], rank=2)
        if len(results) > 2:
            print("\n  " + "=" * 72)
            print("  RUNNER-UP #3")
            print("  " + "=" * 72)
            display(results[2], rank=3)
    else:
        print("  ⚠ No balanced configuration found.")
        print("  Try expanding search or adjusting parameters.")
    print("=" * 72)
