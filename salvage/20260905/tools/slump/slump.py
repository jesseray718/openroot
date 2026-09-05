#!/usr/bin/env python3
# slump.py - fresh concrete rheology (OpenRoot). Units: mm, kg/m3, Pa, degC, min, L/m3
# [lit]=published relation, untested on this rig. [est]=rule of thumb.
import sys, math
G=9.81
def warn(s):
    if not 50<=s<=250: print("! outside 50-250mm validity of P1 [lit]")
def tau_slump(s,rho): return rho*(300.0-s)/270.0            # [lit] Roussel 2006
def slump_tau(t,rho): return 300.0-270.0*t/rho
def tau_spread(Rmm,rho,Vml=5497.0):                          # [lit] R&C 2005, pancake regime
    R=Rmm/1000.0; V=Vml*1e-6
    return 225.0*rho*G*V*V/(128.0*math.pi**2*R**5)
def main(a):
    if not a: return usage()
    c=a[0]
    if c=="tau":                 # tau <slump_mm> <rho>
        s,r=float(a[1]),float(a[2]); warn(s)
        print(f"yield stress ~ {tau_slump(s,r):.0f} Pa")
    elif c=="slump":             # slump <tau_Pa> <rho>
        print(f"predicted slump ~ {slump_tau(float(a[1]),float(a[2])):.0f} mm")
    elif c=="spread":            # spread <R_mm> <rho> [vol_ml: 5497 big cone, 38 mini]
        V=float(a[3]) if len(a)>3 else 5497.0
        print(f"yield stress ~ {tau_spread(float(a[1]),float(a[2]),V):.1f} Pa (flow regime)")
    elif c=="rho":               # rho <mass_kg> <volume_L>
        print(f"density = {float(a[1])/float(a[2])*1000:.0f} kg/m3")
    elif c=="water":             # water <slump_now> <slump_target> <cement_kg_m3>
        dL=(float(a[2])-float(a[1]))/25.0*5.0                # [est] 5 L/m3 per 25mm
        if dL<=0: print("target <= current: wait, don't add water"); return
        print(f"add ~{dL:.1f} L/m3 -> strength cost ~{139.0*dL/float(a[3]):.1f}% [est Abrams B=4]")
    elif c=="window":            # window <slump_t0> <slump_t1> <minutes_apart> [min_ok=75]
        s0,s1,m=float(a[1]),float(a[2]),float(a[3]); smin=float(a[4]) if len(a)>4 else 75.0
        rate=(s0-s1)/m
        if rate<=0: print("no measurable loss yet"); return
        print(f"losing {rate:.2f} mm/min -> ~{(s1-smin)/rate:.0f} min till {smin:.0f}mm floor [est]")
    elif c=="maturity":          # maturity <csv: minutes,tempC per line> [datum=0]
        d=float(a[2]) if len(a)>2 else 0.0; M=0.0; prev=None
        for line in open(a[1]):
            p=line.strip().split(',')
            if len(p)<2: continue
            try: t,T=float(p[0]),float(p[1])
            except ValueError: continue
            if prev: M+=max(0.0,(T+prev[1])/2-d)*(t-prev[0])/60
            prev=(t,T)
        print(f"Nurse-Saul maturity = {M:.0f} degC-h [ASTM C1074, datum {d}]")
    else: usage()
def usage():
    print("slump.py tau|slump|spread|rho|water|window|maturity  (open file for arg order)")
main(sys.argv[1:])
