<!-- STATUS: MODEL — trial.A1.sample
NOT FOR ACRE/FIELD CLAIMS — needs logged mass + dT + minutes
-->
# RMH + labyrinth comparison
generated: 2026-09-01T02:07:04Z
root: /home/jesse/openroot
N14: model output, not pad measurement.
CSV trial.A1.sample is a 3-row fixture. Do not publish as a hang.

```json
[
  {
    "name": "current_all_electric",
    "horizon_s": 86400.0,
    "heat_demand_J": 120000000.0,
    "cool_demand_J": 70000000.0,
    "dhw_demand_J": 25000000.0,
    "heat_served_by_rmh_J": 0.0,
    "cool_served_by_labyrinth_J": 0.0,
    "dhw_served_by_rmh_J": 0.0,
    "heat_unmet_J": 120000000.0,
    "cool_unmet_J": 70000000.0,
    "dhw_unmet_J": 25000000.0,
    "electric_fallback_J": 88190789.4736842,
    "electric_fallback_kWh": 24.497441520467834,
    "baseline_all_electric_J": 88190789.4736842,
    "baseline_all_electric_kWh": 24.497441520467834,
    "electricity_saved_J": 0.0,
    "electricity_saved_kWh": 0.0,
    "reliability_R": 0.98
  },
  {
    "name": "rmh_plus_labyrinth_hybrid",
    "horizon_s": 86400.0,
    "heat_demand_J": 120000000.0,
    "cool_demand_J": 70000000.0,
    "dhw_demand_J": 25000000.0,
    "heat_served_by_rmh_J": 90226240.0,
    "cool_served_by_labyrinth_J": 41979600.0,
    "dhw_served_by_rmh_J": 14976000.0,
    "heat_unmet_J": 29773760.0,
    "cool_unmet_J": 28020400.0,
    "dhw_unmet_J": 10024000.0,
    "electric_fallback_J": 29232540.614035085,
    "electric_fallback_kWh": 8.120150170565301,
    "baseline_all_electric_J": 88190789.4736842,
    "baseline_all_electric_kWh": 24.497441520467834,
    "electricity_saved_J": 58958248.85964912,
    "electricity_saved_kWh": 16.377291349902535,
    "reliability_R": 0.92
  }
]
```
