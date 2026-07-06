> ⚠️ **STATUS: [THEORETICAL] — All performance claims are unvalidated concepts. No physical prototype has been tested. See WBTE-01-TEST-PROTOCOL.md for falsifiable test design.**

# Aerated Glass-Fiber Reinforced Concrete (AE-GFRC-01)
### With Zirconium Substitution for Thermal Applications

© One Human Family — CC-BY-SA-4.0 (docs) / GPL-3.0 (code)

## Overview
Aerated GFRC with open-cell volumetric structure for passive thermal siphon systems. Zirconium replaces silica aggregate for thermal stability.

## Mix Design (Target)
| Component | Proportion | Notes |
|-----------|-----------|-------|
| White Portland cement | 1 part | Binder |
| Zirconium silicate (ZrSiO4) | 2 parts | Replaces silica sand |
| Glass fibers (AR-glass) | 3-5% by wt | Tensile reinforcement |
| Water | 0.35-0.40 w/c ratio | Low water for strength |
| Foaming agent | 2-4% by vol | Creates open-cell voids |
| Superplasticizer | 0.5-1% | Workability at low w/c |

## Porosity Targets
- Void fraction: 60-80%
- Cell structure: Interconnected open cells (not closed)
- Pore size: 0.5-3mm diameter
- Goal: Air contacts entire internal volume, not just channel walls
- Surface area multiplier vs pipe: 100x-1000x

## Thermal Properties (Target)
| Property | Value | Notes |
|----------|-------|-------|
| Thermal conductivity | 0.08-0.15 W/m-K | Low, due to air-filled voids |
| Specific heat | ~0.8 kJ/kg-K | Moderate thermal mass |
| Density | 400-800 kg/m3 | Lightweight vs 2400 normal concrete |
- Low conductivity = slow loss through walls
- Open pores = fast heat transfer TO circulating air

## Compressive Strength
- Target: 2-8 MPa (300-1200 psi)
- Lower than structural concrete by design
- Trade-off: higher porosity = lower strength, higher thermal exchange
- Sufficient for panel geometry, not load-bearing walls

## Zirconium Substitution Rationale
| Issue | Silica (standard) | Zirconium (AE-GFRC) |
|-------|-------------------|---------------------|
| Alkali-silica reaction (ASR) | Major risk over time | Negligible |
| Thermal stability | Degrades above 600C | Stable to 1600C+ |
| Thermal cycling | Microcracking from ASR | No ASR gel formation |
| Cost | Cheap ($0.05/lb) | Expensive ($2-5/lb) |
| Availability | Ubiquitous | Specialty supplier |
- For thermal siphon cycling 35-140F, ASR is the real enemy
- Zirconium eliminates the long-term degradation pathway
- Cost justified by decades-long service life

## Capillary Action
- Open-cell structure creates continuous capillary network
- Water distributes by capillary force without pumps
- Contact angle with cement matrix is low (wetting)
- Enables passive water distribution in wet labyrinth
- No mechanical water feed needed

## Application: Thermal Siphon (WBTE-01)
- Solar stack panels: Blackbody-coated AE-GFRC
- Wet labyrinth: Uncoated AE-GFRC, water-saturated
- Both use open-cell volumetric structure for max air contact
- Panels double as heat absorbers AND heat exchangers
- Eliminates need for separate fin-tube or pipe heat exchangers

## UNE Classification
- System ID: AE-GFRC-01
- UNE: DV.GEN.MT.AG01
- Layer: L3
- Parent: agape-une (Layer 0)
- Dependencies: WBTE-01, CTBS-01, H-003
- License: CC-BY-SA-4.0 / GPL-3.0

## Related
- [WBTE-01](./WBTE-01.md)
- [CTBS-01](./CTBS-01.md)
- [H-003](../hypotheses/H-003.md)
- [Zenodo DOI](https://doi.org/10.5281/zenodo.21210931)
