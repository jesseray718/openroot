from dataclasses import dataclass, asdict
from typing import Dict, Any
@dataclass
class ScenarioResult:
    name: str
    thermal_kwh_day: float
    electrical_kwh_day: float
    cost_usd_day: float
    eta: float
    notes: str
def compare_current_vs_rmh_lab(floor_area_m2: float = 100.0, electricity_usd_kwh: float = 0.12) -> Dict[str, Any]:
    current_thermal = floor_area_m2 * 0.045 * (4200 / 365)
    current_elec = current_thermal / 2.8
    current_cost = current_elec * electricity_usd_kwh
    rmh_thermal = 4.5 * 19.5 * 0.90 / 3.6
    labyrinth = floor_area_m2 * 0.022 * 18.0 / 3.6
    proposed_elec = 0.15
    proposed_cost = proposed_elec * electricity_usd_kwh + 4.5 * 0.08
    savings_elec = max(0.0, current_elec - proposed_elec)
    return {
        "current": asdict(ScenarioResult("current_forced_air_electric", round(current_thermal,2), round(current_elec,2), round(current_cost,2), round(current_thermal/max(current_elec,0.01),2), "grid-dependent")),
        "proposed": asdict(ScenarioResult("rmh_black_locust_plus_aerocement_labyrinth", round(rmh_thermal+labyrinth,2), round(proposed_elec,2), round(proposed_cost,2), round((rmh_thermal+labyrinth)/max(proposed_elec+0.5,0.01),2), "carbon-negative + passive volumetric")),
        "electrical_fallback": asdict(ScenarioResult("electrical_fallback_only", round(current_thermal,2), round(current_thermal/0.95,2), round((current_thermal/0.95)*electricity_usd_kwh,2), 0.95, "pure resistance worst-case")),
        "electricity_savings_kwh_day": round(savings_elec, 2),
        "cost_savings_usd_day": round(current_cost - proposed_cost, 2),
        "annual_elec_savings_kwh": round(savings_elec * 365, 0),
        "nightly_capture_kwh_m2": 12.91,
        "climate": "Sikeston MO",
    }
