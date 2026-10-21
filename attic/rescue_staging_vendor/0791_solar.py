from dataclasses import dataclass
@dataclass
class SolarResult:
    area_m2: float
    irradiance_w_m2: float
    hours: float
    daily_energy_kwh: float
    capture_efficiency: float = 0.93
def calc_solar(area_m2: float, irradiance_w_m2: float = 931.0, hours: float = 5.0, capture_efficiency: float = 0.93) -> SolarResult:
    daily_j = area_m2 * irradiance_w_m2 * hours * 3600 * capture_efficiency
    return SolarResult(area_m2=area_m2, irradiance_w_m2=irradiance_w_m2, hours=hours,
                       daily_energy_kwh=daily_j / 3.6e6, capture_efficiency=capture_efficiency)
