#!/usr/bin/env python3
"""
optimize_spiral.py
Tests different spiral pitches to find the Green Light (High dT + Low dP)
"""
import math

PHI = (1 + math.sqrt(5)) / 2
RHO = 1.175
CP = 1005
G = 9.81

class OptimizedSpiral:
    def __init__(self, pitch_factor, D=6.0, H=30.0, solar=1000.0):
        # pitch_factor: 1.0 = original, 0.6 = tighter, 0.4 = very tight
        self.p = pitch_factor * PHI * D
        self.D = D
        self.H = H
        self.dc = D / (PHI**2)
        self.Ain = math.pi * (D/2)**2
        self.Aout = math.pi * (self.dc/2)**2
        self.Q = solar
        
        # Adjust velocity based on pitch (tighter spiral = slower flow due to friction)
        # Empirical correction: velocity drops as pitch decreases
        self.v_base = 2.8 * (pitch_factor ** 0.5) 

    def pathL(self):
        dz = self.H / 500
        L = 0.0
        for i in range(500):
            z = i * dz
            Dl = self.D * (1 - 0.382 * z / self.H)
            # Longer path for tighter spiral
            L += math.sqrt(dz**2 + (2 * math.pi * (Dl/2) * dz / self.p)**2)
        return L

    def vel(self):
        # Velocity is roughly constant for this simplified model
        return self.v_base, self.v_base, self.v_base

    def mdot(self):
        return RHO * self.Ain * self.vel()[0]

    def dT(self):
        # Heat transfer depends on residence time (path / velocity)
        path = self.pathL()
        v = self.vel()[2]
        residence = path / v
        
        # More residence = more heat absorbed
        # Base heat potential (from solar)
        Dawg = self.D * 0.8
        wa = math.pi * Dawg * self.H * 0.6
        q_max = wa * self.Q * 0.95 * (1 - 0.04 - 0.08)
        
        # Efficiency factor based on residence time (saturation curve)
        # If residence is short, efficiency is low. If long, it approaches 1.0
        eff = 1.0 - math.exp(-residence / 20.0) # 20s is a time constant
        
        q_actual = q_max * eff
        return q_actual / (self.mdot() * CP)

    def dP(self):
        v = self.vel()[2]
        L = self.pathL()
        Dh = self.dc
        # Friction increases with path length but decreases with smoother flow
        f = 0.03 * (1 + 0.2 * (1 - self.p/(PHI*self.D))) # Slightly higher friction for tighter
        fc = 0.85
        return fc * f * (L / Dh) * (0.5 * RHO * v**2)

    def power(self, eta=0.40):
        v = self.vel()[2]
        dT = self.dT()
        Ta = 25 + dT/2 + 273.15
        md = RHO * self.Aout * v
        Pjet = 0.5 * md * v**2
        Pb = eta * md * G * self.H * (dT / Ta)
        return (Pjet * eta + Pb) / 1000

    def results(self, label):
        dT = self.dT()
        P = self.power()
        dP = self.dP()
        return {
            "label": label,
            "dT_C": round(dT, 2),
            "dP_Pa": round(dP, 1),
            "power_kW": round(P, 2),
            "WperPa": round(P * 1000 / max(dP, 1), 2),
            "path_m": round(self.pathL(), 1),
            "vel": round(self.vel()[2], 2)
        }

def run():
    # Test 3 pitch factors: 1.0 (Original), 0.6 (Tighter), 0.4 (Very Tight)
    tests = [
        (1.0, "Original (p=1.0*phi*D)"),
        (0.6, "Optimized (p=0.6*phi*D)"),
        (0.4, "Ultra-Tight (p=0.4*phi*D)")
    ]
    
    # Baseline Linear from previous run
    linear_dT = 3.18
    linear_dP = 19.8
    linear_power = 0.28
    
    print("="*70)
    print("OPTIMIZED SPIRAL SEARCH: FINDING THE GREEN LIGHT")
    print("="*70)
    print(f"Baseline Linear: dT={linear_dT}C, dP={linear_dP}Pa, Power={linear_power}kW")
    print("-"*70)
    
    fmt = "| {:<25} | {:>8} | {:>8} | {:>8} | {:>8} | {:>8} |"
    print(fmt.format("Config", "dT (C)", "dP (Pa)", "Power", "W/Pa", "Status"))
    print("-"*70)
    
    best_score = 0
    best_config = None
    
    for factor, label in tests:
        s = OptimizedSpiral(factor)
        r = s.results(label)
        
        # Scoring: We want dT >= Linear AND dP < Linear
        # Score = (dT/Linear_dT) * (Linear_dP/dP)
        score = (r["dT_C"] / linear_dT) * (linear_dP / r["dP_Pa"])
        
        status = "❌"
        if r["dT_C"] >= linear_dT and r["dP_Pa"] < linear_dP:
            status = "🟢 GREEN"
            if score > best_score:
                best_score = score
                best_config = r
        elif r["dT_C"] >= linear_dT:
            status = "🟡 OK (High dT)"
        elif r["dP_Pa"] < linear_dP:
            status = "🟡 OK (Low dP)"
            
        print(fmt.format(label, r["dT_C"], r["dP_Pa"], r["power_kW"], r["WperPa"], status))
    
    print("-"*70)
    if best_config:
        print(f"🏆 WINNER: {best_config['label']}")
        print(f"   dT: {best_config['dT_C']}C (>= {linear_dT}C)")
        print(f"   dP: {best_config['dP_Pa']}Pa (< {linear_dP}Pa)")
        print(f"   Power: {best_config['power_kW']}kW")
        print(f"   Efficiency: {best_config['WperPa']} W/Pa")
    else:
        print("⚠️ No configuration beats Linear on BOTH metrics yet.")
        print("   Recommendation: Try Hybrid (Spiral bottom + Staged top)")
    
    print("="*70)

if __name__ == "__main__":
    run()
