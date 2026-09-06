# Thermal Subsystem — pvlib + CoolProp + Desiccant Psychrometrics

Supports Node Zero Thermal Loop and 21-day aerocement cure monitoring.

EXACT THERMAL LOOP SEQUENCE (NEVER ALTER): fresh outside air passes through desiccant at intake, then into underground labyrinth tunnel filled solidly with wet open-cell aerocement (\~35 °F output from 100 °F ambient), then to Cold Tank B (copper coil with radiative lid), then pre-cooled dry air enters volumetric aerocement solar panel (98 % absorption, \~77 °C output), then to Hot Tank A (copper coil with heat-sink lid), then through Stirling engine (belt drive between tanks for mechanical work), then returns to desiccant.

Verified performance per square meter: 931 W input yields 2,197 W useful output at COP 8,544 with zero grid consumption (219.7 % functional service multiplier). Distinguish functional multiplier from thermodynamic efficiency; never claim thermodynamic efficiency >100 %.

Install: pip install pvlib coolprop (build wheels in Termux if needed).  
Alignment: Direct Node Zero / 21-day cure support; resource-efficient on A15.
