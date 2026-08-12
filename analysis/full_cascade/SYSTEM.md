# Full Cascading Thermal System — OpenRoot
# Locked description 2026-08-12

## Loop (one air mass, continuous natural draft)

1. Driver (stack effect)
   - Black Locust Rocket Mass Heater **or** high-absorptivity solar panel with spiral / multi-spiral turbulence geometry
   - Creates natural draft; air is heated and rises
   - Multiple inlets at the base possible; single optimized outlet to avoid bottleneck

2. Hot storage battery
   - Insulated ferro-cement tank
   - Copper coil (insulated until entry) spirals through the tank
   - Air gives up heat → leaves near ambient
   - Water stratifies (hottest at top)

3. Pre-drying (optional but important)
   - Desiccant or residual heat used to dry the air before the cold labyrinth

4. Cold labyrinth (evaporative flash stage)
   - Underground wet open-cell aerocement (high m²/m³ surface area)
   - Hot dry air contacts cold wet volumetric surface
   - Latent heat of vaporization is extracted → strong cooling flash
   - This is the high-exergy moment of the cold side

5. Cold storage battery
   - Conical ferro-cement tank, point down
   - Sides + bottom insulated
   - Top: aluminum (or equivalent) heat-sink plate dipping into water, upper surface high-ε and sky-facing (radiative rejection toward cold sky / 3 K window)
   - Stratification: coldest fluid protected at the point
   - Copper coil extracts cold before air continues

6. Return / continuation
   - Air, now nearer ambient and partially dried or re-humidified according to design, is available to be drawn again by the stack
   - The same draft that drives the hot side moves the equal volume through the cold side

## Simultaneous processes
- Hot battery is charged by the driver
- Cold battery is charged by evaporative flash + radiative rejection to sky
- ΔT between the two batteries is the stored resource
- Heat is the long-term storage medium; cold is actively maintained by radiation to the sky

## Optimization questions answered by the model
- Ratio of hot-battery volume : cold-battery volume : labyrinth surface area : driver aperture
- How stored ΔT compounds over successive days/nights
- What happens when the stored ΔT is itself used to drive a second stage
- Where compounding saturates (the practical autonomous limit)
