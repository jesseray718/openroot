import math

def calc_gain(diameter_inch, freq_ghz, eta=0.55):
    D = diameter_inch * 0.0254  # inches to meters
    c = 3e8
    lambda_val = c / (freq_ghz * 1e9)
    gain_linear = (eta * math.pi**2 * D**2) / (lambda_val**2)
    return 10 * math.log10(gain_linear)

def fspl(dist_km, freq_ghz):
    return 20 * math.log10(dist_km) + 20 * math.log10(freq_ghz) + 92.45

diameters = [18, 24, 30]
freqs = [2.4, 5.8]

print(f"{'Diam':<6} | {'Freq':<6} | {'Gain (dBi)':<12} | {'FSPL 5km':<12} | {'FSPL 10km':<12} | {'FSPL 20km':<12}")
print("-" * 65)
for d in diameters:
    for f in freqs:
        g = calc_gain(d, f)
        f5 = fspl(5, f)
        f10 = fspl(10, f)
        f20 = fspl(20, f)
        print(f"{d:<6} | {f:<6} | {g:<12.2f} | {f5:<12.2f} | {f10:<12.2f} | {f20:<12.2f}")
