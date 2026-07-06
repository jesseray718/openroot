# Cascading Thermal Battery System (CTBS-01)
### Modular Thermal Energy Storage via Staged Water Tanks

© One Human Family — CC-BY-SA-4.0 (docs) / GPL-3.0 (code)

## Overview
Two symmetric cascades ensure zero waste. Air exits at room temp (~75°F).

| Cascade | Input | Process | Output |
|---------|-------|---------|--------|
| Hot | 140°F (solar stack) | 3-stage water tanks | 75°F |
| Cold | 35°F (wet labyrinth) | 3-stage water tanks | 75°F |

## Hot Cascade
| Stage | Air In | Air Out | Target |
|-------|--------|---------|--------|
| 1 | 140°F | ~110°F | 140°F charging |
| 2 | ~110°F | ~90°F | 110°F charging |
| 3 | ~90°F | ~75°F | 90°F charging |
| Exit | ~75°F | — | Zero waste |

## Cold Cascade
| Stage | Air In | Air Out | Target |
|-------|--------|---------|--------|
| 1 | 35°F | ~50°F | 35°F charging |
| 2 | ~50°F | ~62°F | 50°F charging |
| 3 | ~62°F | ~75°F | 62°F charging |
| Exit | ~75°F | — | Zero waste |

## Battery Unit
- Tank: 50gal polyethylene, R-20+ foam
- Heat exchanger: 3/4" copper coil
- Fluid: water (4.186 J/g/K)
- Probe: DS18B20 (1-Wire, $2)
- Energy per tank: 189kg x 4.186 x 11K = 8696kJ = 2.41 kWh

## Scaling
| Scale | Tanks | Thermal | Elec @10% |
|-------|-------|---------|-----------|
| 1m2 3-tank | 3 | 7.23 kWh | 0.72 kWh |
| 10m2 6-tank | 6 | 14.46 kWh | 1.45 kWh |
| 10m2 12-tank | 12 | 28.92 kWh | 2.89 kWh |
| 50m2 30-tank | 30 | 72.3 kWh | 7.23 kWh |

## Integration
[Solar Stack]->[Hot Cascade]->[Stirling]->[Cold Cascade]->[Wet Labyrinth]
    140F          140->75F      dT=105F      35->75F          35F

Stirling draws from hottest tank, rejects to coldest. Cascade auto-stages.

## UNE Classification
- System ID: CTBS-01
- UNE: DV.GEN.TH.CB01
- Layer: L3
- Parent: agape-une (Layer 0)
- Dependencies: WBTE-01, AE-GFRC, H-003
- License: CC-BY-SA-4.0 / GPL-3.0

## Related
- [WBTE-01](./WBTE-01.md)
- [AE-GFRC Spec](./AE-GFRC-01.md)
- [H-003](../hypotheses/H-003.md)
- [Zenodo DOI](https://doi.org/10.5281/zenodo.21210931)
