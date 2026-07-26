#!/usr/bin/env python3
"""
porous_exchanger_design.py  v2.2 (OpenRoot Aero-Disc)
Volumetric wet-media exchanger sizing for AeroCement / OpenRoot
Geometries: STRAIGHT CHANNELS | N-START SPIRAL (Dean, Ito+Dravid) | OPEN BED

v2.2: improved output formatting for Termux readability
v2.1: greenhouse air-gap note added
v2.0: coil radius, true helix length, Ito/Dravid correlations, optimizer

Note: A greenhouse air gap (25–35 mm) between black absorber face and
clear membrane is required. Extra buoyancy term not yet modeled.
Stdlib only. Termux-safe.
"""

import math

# ---------------- EDITABLE CONSTANTS ----------------
Q_AIR    = 0.18      # m3/s design airflow
T_IN     = 35.0      # C air entering block
T_MATRIX = 16.0      # C wet matrix temp
RHO_A    = 1.16
MU_A     = 1.85e-5
CP_A     = 1005.0
K_A      = 0.026
PR       = 0.71

# straight channels
D_CH     = 0.010
PHI      = 0.50
L_CH     = 2.0
FACE_CH  = 0.36

# N-start spiral channels
D_SP     = 0.010
PHI_SP   = 0.45
L_SP     = 2.0
FACE_SP  = 0.36
PITCH    = 0.080
R_HELIX  = 0.020
N_START  = 5

# spiral optimizer targets
NTU_MIN  = 3.0
L_SCAN_LO, L_SCAN_HI, L_STEP = 0.05, 2.0, 0.01

# open bed
EPS      = 0.30
DP       = 0.005
L_BED    = 0.5
FACE_BED = 9.0

# stack
H_STACK  = 6.0
DT_STACK = 25.0
T_K      = 305.0

# water / soil
R_PORE   = 25e-6
COS_THETA = 0.8
Q_EVAP   = 1000.0
H_FG     = 2.45e6
K_SOIL   = 1.5
SOIL_AREA = 20.0
SOIL_DT  = 10.0
FAN_ETA  = 0.5
# ----------------------------------------------------

def stack_pa():
    return RHO_A * 9.81 * H_STACK * (DT_STACK / T_K)

def channels():
    u = (Q_AIR / FACE_CH) / PHI
    re = RHO_A * u * D_CH / MU_A
    if re < 2300:
        dp = 32.0 * MU_A * L_CH * u / (D_CH ** 2)
        nu, regime = 3.66, "laminar"
    else:
        f = 0.316 * re ** -0.25
        dp = f * (L_CH / D_CH) * 0.5 * RHO_A * u * u
        nu, regime = 0.023 * re ** 0.8 * PR ** 0.4, "turbulent"
    dp += 1.5 * 0.5 * RHO_A * u * u
    h = nu * K_A / D_CH
    a_v = 4.0 * PHI / D_CH
    vol = FACE_CH * L_CH
    ntu = h * a_v * vol / (RHO_A * Q_AIR * CP_A)
    return dict(name="STRAIGHT CHANNELS", u=u, re=re, regime=regime,
                dp=dp, a_v=a_v, vol=vol, ntu=ntu)

def spiral_geom():
    b = PITCH / (2.0 * math.pi)
    rc = R_HELIX + (b * b) / R_HELIX
    stretch = math.sqrt(1.0 + (2.0 * math.pi * R_HELIX / PITCH) ** 2)
    return rc, stretch

def ito_friction_ratio(de):
    if de <= 13.5:
        return 1.0
    a = 1.729 / de
    core = math.sqrt(1.0 + a) - math.sqrt(a)
    return 0.1033 * math.sqrt(de) * core ** -3

def dravid_nu(de):
    if de < 50.0:
        return 3.66 * (1.0 + (de / 50.0) * (0.76 * math.sqrt(50.0)
                       * PR ** 0.175 / 3.66 - 1.0))
    return 0.76 * math.sqrt(de) * PR ** 0.175

def spiral_channels(l_axial=None):
    L = L_SP if l_axial is None else l_axial
    u = (Q_AIR / FACE_SP) / PHI_SP
    re = RHO_A * u * D_SP / MU_A
    rc, stretch = spiral_geom()
    l_helix = L * stretch
    de = re * math.sqrt(D_SP / (2.0 * rc))
    if re < 2300:
        f = (64.0 / re) * ito_friction_ratio(de)
        nu = dravid_nu(de)
        regime = "laminar+Dean (Ito/Dravid)"
    else:
        f = 0.316 * re ** -0.25
        nu = 0.023 * re ** 0.8 * PR ** 0.4
        regime = "turbulent"
    dp = f * (l_helix / D_SP) * 0.5 * RHO_A * u * u
    dp += 1.5 * 0.5 * RHO_A * u * u
    h = nu * K_A / D_SP
    a_v = 4.0 * PHI_SP / D_SP
    vol = FACE_SP * L
    ntu = h * a_v * vol * stretch / (RHO_A * Q_AIR * CP_A)
    return dict(name="%d-START SPIRAL" % N_START, u=u, re=re, regime=regime,
                dp=dp, a_v=a_v, vol=vol, ntu=ntu, De=round(de, 1),
                L=L, L_helix=l_helix)

def bed():
    u = Q_AIR / FACE_BED
    visc = 150.0 * MU_A * (1 - EPS) ** 2 / (EPS ** 3 * DP ** 2) * u
    iner = 1.75 * RHO_A * (1 - EPS) / (EPS ** 3 * DP) * u * u
    dp = (visc + iner) * L_BED
    re = RHO_A * u * DP / (MU_A * (1 - EPS))
    nu = 2.0 + 1.1 * (re ** 0.6) * (PR ** (1.0 / 3.0))
    h = nu * K_A / DP
    a_v = 6.0 * (1 - EPS) / DP
    vol = FACE_BED * L_BED
    ntu = h * a_v * vol / (RHO_A * Q_AIR * CP_A)
    return dict(name="OPEN BED", u=u, re=re, regime="Ergun", dp=dp,
                a_v=a_v, vol=vol, ntu=ntu)

def optimize_spiral(avail):
    best_passive, best_any = None, None
    L = L_SCAN_LO
    while L <= L_SCAN_HI + 1e-9:
        g = spiral_channels(L)
        if g["ntu"] >= NTU_MIN:
            if best_any is None:
                best_any = g
            if g["dp"] <= avail and best_passive is None:
                best_passive = g
            if best_passive is not None:
                break
        L += L_STEP
    return best_passive, best_any

def report(g, avail):
    eff = 1.0 - math.exp(-g["ntu"])
    t_out = T_MATRIX + (T_IN - T_MATRIX) * math.exp(-g["ntu"])
    ok = g["dp"] <= avail
    fan_w = 0.0 if ok else Q_AIR * g["dp"] / FAN_ETA

    print()
    print("=" * 52)
    print("  %s" % g["name"])
    print("=" * 52)

    if "L" in g:
        print("  Axial length     : %7.2f m" % g["L"])
        print("  Helical path     : %7.2f m" % g["L_helix"])
    print("  Specific area    : %7.0f m²/m³" % g["a_v"])
    print("  Volume           : %7.2f m³" % g["vol"])
    print("  Velocity         : %7.2f m/s" % g["u"])
    print("  Reynolds number  : %7.0f  (%s)" % (g["re"], g["regime"]))
    if "De" in g:
        print("  Dean number      : %7.1f" % g["De"])
    print("-" * 52)
    print("  Pressure drop    : %7.1f Pa" % g["dp"])
    print("  Stack available  : %7.1f Pa" % avail)
    if ok:
        print("  Status           : PASSIVE OK")
    else:
        print("  Status           : NEEDS FAN  (%.1f W)" % fan_w)
    print("-" * 52)
    print("  NTU              : %7.2f" % g["ntu"])
    print("  Effectiveness    : %6.1f %%" % (eff * 100))
    print("  Outlet temp      : %7.2f °C" % t_out)
    print("=" * 52)

def water_soil():
    h_cap = 2.0 * 0.072 * COS_THETA / (1000.0 * 9.81 * R_PORE)
    lph = Q_EVAP / H_FG * 3600.0
    q_soil = K_SOIL * SOIL_DT / 0.25 * SOIL_AREA
    print()
    print("=" * 52)
    print("  WATER / SOIL INTERFACE")
    print("=" * 52)
    print("  Capillary rise   : %7.2f m" % h_cap)
    print("  Water use        : %7.2f L/h  @ %.0f W" % (lph, Q_EVAP))
    print("  Soil capacity    : %7.0f W sustained" % q_soil)
    print("-" * 52)
    print("  Rule: NTU past \~5 buys almost nothing but extra ΔP.")
    print("        Soil interface is the real capacity limit.")
    print("=" * 52)

if __name__ == "__main__":
    avail = stack_pa()
    print()
    print("+" + "-" * 50 + "+")
    print("|  OpenRoot Aero-Disc  —  Sizing Tool  v2.2        |")
    print("+" + "-" * 50 + "+")
    print("  Stack pressure available : %5.1f Pa" % avail)
    print("  (H = %.1f m,  ΔT = %.0f K)" % (H_STACK, DT_STACK))
    print("+" + "-" * 50 + "+")

    report(channels(), avail)
    report(spiral_channels(), avail)
    report(bed(), avail)

    bp, ba = optimize_spiral(avail)

    print()
    print("+" + "-" * 50 + "+")
    print("|  SPIRAL OPTIMIZER  (target NTU ≥ %.1f)            |" % NTU_MIN)
    print("+" + "-" * 50 + "+")

    if bp:
        print("  Result: shortest PASSIVE geometry found")
        report(bp, avail)
    elif ba:
        print("  Result: no fully passive solution in scan range")
        print("  Showing shortest geometry that meets NTU target:")
        report(ba, avail)
        print()
        print("  Suggestion: increase FACE_SP (lower velocity)")
        print("              or raise H_STACK / ΔT to go passive")
    else:
        print("  No geometry met the NTU target in the scan range.")

    water_soil()

    print()
    print("Done. Edit constants at top of script and re-run.")
    print()
