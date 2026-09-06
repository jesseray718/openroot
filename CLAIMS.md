# Claims Registry

One row per load-bearing sentence. Grades: MEASURED | MODEL | DEMO | OPEN | REJECT.

Pane for evidence paths: SSH clone `/home/jesse/src/openroot-integrate` or `/home/jesse/openroot` after fetch. Phone copies are not hangs.

| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| C01 | AM1.5 design irradiance is 1000 W/m² on collector face | MODEL | `projects/aerocement/aerocement_ledger.py` `IRRADIANCE_W_M2` | N14 |
| C02 | Carbon-doped open-cell solar absorptivity α = 0.98 | OPEN | needs ASTM E903 / C1371 hang on a poured coupon | N08 N14 |
| C03 | Face-to-air transfer 0.95 after reflection and edge loss | MODEL | ledger `TRANSFER_EFF`; no duct traverse yet | N14 |
| C04 | Net to airflow at design point is 931 W/m² (1000×0.98×0.95) | MODEL | ledger `q_net_to_air_w`; also `aerocement_calc` locked constant | N14 |
| C05 | First-Law budget is 931 W in = shaft work + heat-to-ground + loss | MODEL | ledger residual `-0.0000 W` | N14 |
| C06 | Latent enthalpy at 0.5 kg/h evaporation is \~314 W/m² of **transport**, not new solar input | MODEL | ledger `q_latent_transport_w`; condensation returns the same joules | N14 |
| C07 | Adding 931 + 314 and calling it 1245 W created | REJECT | water cycle is form change, not a second sun | N14 |
| C08 | Adding heat + cooling + shaft work and calling it 2197 W or 220% efficiency | REJECT | service-count ≠ heat-engine η | N14 |
| C09 | Passive transport ratio written as COP = 21,972 | REJECT | near-zero electrical watts on the loop is a ratio of convenience, not an engine | N14 |
| C10 | Carnot at 350 K / 275 K (77°C / 2°C target pair) is 21.4% | MODEL | ledger `eta_carnot`; 2°C is the evaporative **target**, not ground | N14 |
| C11 | Stirling taken as 60% of that Carnot = 12.9% of heat that crosses the engine | MODEL | ledger `eta_stirling_of_engine_heat`; not 12.9% of 931 W unless that heat is proven through the working fluid | N14 |
| C12 | Model shaft work at this design point is 76.6 W/m² | MODEL | ledger `w_mech_w`; heat-engine η vs incident = 7.66% | N14 |
| C13 | Model heat dumped to ground / Hot Tank A is 854.3 W/m² | MODEL | ledger `q_to_ground_w` | N14 |
| C14 | Temperate-ground sink class at \~10 ft is \~55°F / 12.8°C | MODEL | regional soil class; not a Sikeston well log | N08 |
| C15 | Labyrinth outlet 35°F / 2°C | OPEN | evaporative target; hang or drop | N08 N14 |
| C16 | Duct friction 0.1 W | DEMO | placeholder; replace with measured ΔP·V | N14 |
| C17 | Charcoal-infused open-cell pours exist | DEMO | prototype pours; not a strength hang | N08 |
| C18 | Mix 1 part gel : 2 parts cement holds interconnected voids past ordinary aircrete collapse | OPEN | needs pour series + C138 / C231 or C457 | N08 N13 |
| C20 | AE-GFRC dry density ≤ 1,200 kg/m³ with ≥15 MPa and C1550 toughness | OPEN | H1; C39 + C1550 + C138 | N08 |
| C21 | Open-cell porosity 65–80% interconnected | OPEN | C231 / C457 plus permeability | N08 |
| C22 | Internal S/V 500–2,000 m²/m³ in the filled labyrinth | OPEN | geometry + image analysis on a core | N08 |
| C23 | 21-day wet cure is mandatory | MODEL | N13 rule; not a strength number until C39 exists | N13 |
| C24 | Tunnel filled SOLID with wet AeroCement, never lined | MODEL | geometry rule in README Hard Rules | N08 |
| C25 | Two tanks never combined | MODEL | geometry rule | N08 |
| C26 | Desiccant at intake only; regen from surplus heat | MODEL | moisture rule; no packed-bed hang | N08 |
| C27 | AeroDisk ≠ labyrinth ≠ RMH | MODEL | organ split; do not hang one name on another body | N08 |
| C28 | Stack ΔP ≈ 14.6 Pa at H = 10 m for 27°C / 77°C air | MODEL | ΔP = g·H·(ρ_c−ρ_h); no instrumented chimney | N14 |
| C29 | Design mass flow \~0.0185 kg/s per m² at 50 K air rise | MODEL | ledger `mdot_kg_s` | N14 |
| C30 | H1 AE-GFRC pumpable 1,609 m without segregation | OPEN | C1716 + line trial 100→500→1000→1609 m | N08 |
| C31 | H2 spherical voids beat mined LWAC on specific strength | OPEN | paired C39 at equal cement | N08 |
| C32 | H3 / H6 pneumatic placement ≥300 m³/h at ≤30 bar | OPEN | timed pour; foam-collapse watch | N08 |
| C33 | H5 drag-cooled open-cell radiator holds work-positive Stirling ΔT | OPEN | wind tunnel 5/15/25 m/s + bench engine | N08 N14 |
| C34 | H5 draft figures 180–300 kW vehicle / 1500 kW radiator | REJECT | napkin bound, not a vehicle | N14 |
| C35 | H-003 Sikeston instrumented node matches 931 W/m² class on η_act vs measured electrical baseline | OPEN | pad: irradiance, ΔT_hot, ΔT_cold, airflow, shaft RPM/torque | N08 N14 |
| C36 | ACRE / PoPW mints only on verified physical work | MODEL | spec in `tokens/`; no live mint hang in this row | N09 |
| C37 | No thermodynamic efficiency greater than 100% is claimable | MODEL | N14 cap; any contrary sentence is REJECT | N14 |

## How to move a row

- OPEN → MEASURED: named ASTM or pad file with date, instrument, and raw numbers.
- MODEL → MEASURED: same, plus the script constant is replaced or annotated.
- DEMO → MEASURED: coupon or node id, photo, mass or sensor log.
- REJECT stays. Do not delete C07, C08, C09, C34 to look clean.

## Smallest proof this file is alive

```bash
wc -l /home/jesse/src/openroot-integrate/CLAIMS.md
python3 /home/jesse/src/openroot-integrate/projects/aerocement/aerocement_ledger.py
