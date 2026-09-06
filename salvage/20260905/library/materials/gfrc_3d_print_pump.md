# Nanoscopic GFRC — Open/Closed Cell, 3D Print & Long-Distance Pump
**UNE:** DV.CON.MAT.GFRC.3DP.001  
**Status:** hypothesis  
**η note:** ≥20 % Zr AR glass + nanoscopic bubbles + controllable set for robotic placement.

## Open-cell vs Closed-cell (nanoscopic)

| Property              | Open-cell (target for thermal) | Closed-cell                  |
|-----------------------|--------------------------------|------------------------------|
| Vapor movement        | High                           | Almost none                  |
| Insulation (dry)      | Good                           | Excellent                    |
| Strength potential    | Competitive if bubbles uniform | Usually higher at same density |
| Pumpability           | Good when well dispersed       | Good                         |
| 3D-print suitability  | High (can be tuned)            | High                         |
| Best use in OpenRoot  | Labyrinth / desiccant / breathable shells | Structural cores, waterproof layers |

Both can use the same ≥20 % zirconium AR glass. The difference is mainly bubble topology and surfactant/gel package.

## 3D Printing & Pumping
- High-shear pre-mix (stator or blender) produces the fine bubble structure.
- Once mixed, the material can be pumped significant distances or vertically if rheology is controlled (plasticizers + thixotropic agents).
- Baking soda (sodium bicarbonate) or other accelerators can produce near flash-set at the nozzle. This allows the material to leave the nozzle fluid and gain green strength within seconds to minutes — essential for printing overhangs or vertical elements without formwork.
- Different mixes can be switched for outer skin (higher density / closed-cell / more fiber) versus inner fill (lower density / open-cell).

## Practical Constraints
- Dispersion of AR glass and any graphene/graphite must survive pumping.
- Flash-set window must be tuned carefully; too fast = blocked hoses.
- First tests should be small-scale extrusion before any long-distance claim.

## Next physical action
1. Produce two small batches (open-cell and closed-cell) with ≥20 % Zr AR glass.
2. Test hand extrusion and simple accelerator response.
3. Measure green strength vs time after accelerator addition.

## Related
- library/materials/aerated_nanobubble_gfrc.md
- library/materials/gfrc_open_cell_bl.md
