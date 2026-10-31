from dataclasses import dataclass, asdict
from typing import Dict, Any

# Energy matching principle:
# - Heat demand should be served by heat sources (RMH, solar thermal, etc.)
# - Cooling demand should be served by cooling sinks (labyrinth, night purge, etc.)
# - Resistive/electrical conversion penalties are explicit

J_PER_KWH = 3_600_000.0

@dataclass
class SystemCase:
    name: str
    horizon_s: float

    # Demands
    heat_demand_J: float
    cool_demand_J: float
    dhw_demand_J: float  # domestic hot water demand

    # Sources/sinks capacities over horizon
    rmh_heat_available_J: float
    labyrinth_cool_available_J: float

    # Delivery efficiencies
    eta_heat_delivery: float
    eta_cool_delivery: float
    eta_dhw_delivery: float

    # Baseline electrical alternatives (for unmet loads)
    cop_heatpump_heating: float
    cop_heatpump_cooling: float
    eta_resistive_hot_water: float

    # Reliability and losses
    reliability_R: float
    distribution_loss_heat_frac: float
    distribution_loss_cool_frac: float

def clamp(x, lo=0.0):
    return x if x > lo else lo

def evaluate_case(c: SystemCase) -> Dict[str, Any]:
    # 1) Serve heat with RMH
    rmh_deliverable_heat_J = c.rmh_heat_available_J * c.eta_heat_delivery * c.reliability_R
    rmh_deliverable_heat_J *= (1.0 - c.distribution_loss_heat_frac)

    heat_served_by_rmh_J = min(c.heat_demand_J, rmh_deliverable_heat_J)
    heat_unmet_J = clamp(c.heat_demand_J - heat_served_by_rmh_J)

    # 2) Serve cooling with labyrinth
    lab_deliverable_cool_J = c.labyrinth_cool_available_J * c.eta_cool_delivery * c.reliability_R
    lab_deliverable_cool_J *= (1.0 - c.distribution_loss_cool_frac)

    cool_served_by_lab_J = min(c.cool_demand_J, lab_deliverable_cool_J)
    cool_unmet_J = clamp(c.cool_demand_J - cool_served_by_lab_J)

    # 3) DHW: first consume any remaining RMH heat
    # Calculate remaining on source-energy basis
    heat_consumed_source_J = heat_served_by_rmh_J / max(c.eta_heat_delivery, 1e-9)
    rmh_remaining_source_J = clamp(c.rmh_heat_available_J - heat_consumed_source_J)
    dhw_served_by_rmh_J = min(c.dhw_demand_J, rmh_remaining_source_J * c.eta_dhw_delivery)
    dhw_unmet_J = clamp(c.dhw_demand_J - dhw_served_by_rmh_J)

    # 4) Electrical fallback only for unmet loads
    # Heating fallback via heat pump
    elec_for_heat_unmet_J = heat_unmet_J / max(c.cop_heatpump_heating, 1e-9)

    # Cooling fallback via heat pump
    elec_for_cool_unmet_J = cool_unmet_J / max(c.cop_heatpump_cooling, 1e-9)

    # DHW fallback via resistive or equivalent eta
    elec_for_dhw_unmet_J = dhw_unmet_J / max(c.eta_resistive_hot_water, 1e-9)

    total_elec_fallback_J = elec_for_heat_unmet_J + elec_for_cool_unmet_J + elec_for_dhw_unmet_J

    # Useful delivered
    useful_J = heat_served_by_rmh_J + cool_served_by_lab_J + dhw_served_by_rmh_J + \
               (heat_unmet_J + cool_unmet_J + dhw_unmet_J)  # unmet loads assumed supplied by fallback
    # Input accounting in this simplified comparison:
    # We treat RMH/labyrinth availability as already captured useful-side service potential,
    # and explicitly count electrical fallback as incremental purchased input.
    # For comparative signal, define apparent efficiency wrt fallback electrical input avoided.
    baseline_all_electric_J = (c.heat_demand_J / max(c.cop_heatpump_heating, 1e-9)) + \
                              (c.cool_demand_J / max(c.cop_heatpump_cooling, 1e-9)) + \
                              (c.dhw_demand_J / max(c.eta_resistive_hot_water, 1e-9))

    elec_saved_J = baseline_all_electric_J - total_elec_fallback_J
    elec_saved_kWh = elec_saved_J / J_PER_KWH

    return {
        "name": c.name,
        "horizon_s": c.horizon_s,
        "heat_demand_J": c.heat_demand_J,
        "cool_demand_J": c.cool_demand_J,
        "dhw_demand_J": c.dhw_demand_J,
        "heat_served_by_rmh_J": heat_served_by_rmh_J,
        "cool_served_by_labyrinth_J": cool_served_by_lab_J,
        "dhw_served_by_rmh_J": dhw_served_by_rmh_J,
        "heat_unmet_J": heat_unmet_J,
        "cool_unmet_J": cool_unmet_J,
        "dhw_unmet_J": dhw_unmet_J,
        "electric_fallback_J": total_elec_fallback_J,
        "electric_fallback_kWh": total_elec_fallback_J / J_PER_KWH,
        "baseline_all_electric_J": baseline_all_electric_J,
        "baseline_all_electric_kWh": baseline_all_electric_J / J_PER_KWH,
        "electricity_saved_J": elec_saved_J,
        "electricity_saved_kWh": elec_saved_kWh,
        "reliability_R": c.reliability_R
    }

def compare_current_vs_rmh_lab():
    day = 24 * 3600.0

    current = SystemCase(
        name="current_all_electric",
        horizon_s=day,
        heat_demand_J=120e6,
        cool_demand_J=70e6,
        dhw_demand_J=25e6,
        rmh_heat_available_J=0.0,
        labyrinth_cool_available_J=0.0,
        eta_heat_delivery=0.0,
        eta_cool_delivery=0.0,
        eta_dhw_delivery=0.0,
        cop_heatpump_heating=3.0,
        cop_heatpump_cooling=3.2,
        eta_resistive_hot_water=0.95,
        reliability_R=0.98,
        distribution_loss_heat_frac=0.0,
        distribution_loss_cool_frac=0.0
    )

    proposed = SystemCase(
        name="rmh_plus_labyrinth_hybrid",
        horizon_s=day,
        heat_demand_J=120e6,
        cool_demand_J=70e6,
        dhw_demand_J=25e6,
        rmh_heat_available_J=130e6,
        labyrinth_cool_available_J=65e6,
        eta_heat_delivery=0.82,
        eta_cool_delivery=0.78,
        eta_dhw_delivery=0.75,
        cop_heatpump_heating=3.0,
        cop_heatpump_cooling=3.2,
        eta_resistive_hot_water=0.95,
        reliability_R=0.92,
        distribution_loss_heat_frac=0.08,
        distribution_loss_cool_frac=0.10
    )

    return evaluate_case(current), evaluate_case(proposed)

if __name__ == "__main__":
    import json
    a, b = compare_current_vs_rmh_lab()
    print(json.dumps({"current": a, "proposed": b}, indent=2))
