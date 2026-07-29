import math
SIGMA = 5.670374e-8

def rad_cooling(area, t_surf_c, t_sky_c=-10, emissivity=0.93):
    ts = t_surf_c + 273.15
    tk = t_sky_c + 273.15
    power = SIGMA * emissivity * area * (ts**4 - tk**4)
    return power

for area in [1, 10]:
    night = rad_cooling(area, 15)
    day_sub = rad_cooling(area, 28, -40)  # selective paint radiates to deep space
    daily_kwh = night * 12 / 1000  # 12 effective night hours
    print(f"{area} m² lid:")
    print(f"  Night cooling: {night:.1f} W ({night/area:.1f} W/m²)")
    print(f"  Selective paint (day, deep space target): {day_sub:.1f} W")
    print(f"  Night energy removed: {daily_kwh:.2f} kWh")
    print(f"  ΔT boost to cold trench: ~{night/500:.1f}°C additional drop")
    print()
