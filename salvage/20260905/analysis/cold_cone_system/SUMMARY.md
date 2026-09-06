# Optimized Conical Cold-Tank System — Analytical Summary

Environment: T_amb = 300 K, T_sky ≈ 250 K (clear night), dry-ish.

## Key observations from the model
- Taller cones (higher aspect ratio) build stronger stratification.
- Top-plate radiative cooling preferentially chills the upper water while the point protects the coldest fluid.
- With good side/bottom insulation the system compounds cold night after night.
- Air-breathing term is kept small; its main role is humidity management, not primary cooling.
- The same ΔT physics appears here (cold reservoir + sky radiator) that appears inverted in Cloud Nine v0.1 (hot absorber + sky radiator).

## Graph-ready data
See results.json for time series of T_plate, T_top_water, T_bottom_water, Q_stored.
Plot Q_stored vs time for each aspect ratio to see compounding.
Plot (T_top – T_bottom) vs time to see stratification strength.
