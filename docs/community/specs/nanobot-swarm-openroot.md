# Nanobot Swarm Specification — OpenRoot Thermal Systems (H-003)

## Primary Objective
Build and validate a volumetric open-cell blackbody concrete solar collector with underground labyrinth thermal storage and Stirling/TEG discharge — an open-loop system capturing ~98% of incident solar energy on first pass, storing heat in insulated ground batteries for nighttime power generation.

## Validation Status
- [x] Simulation completed (thermal_cascade_v2.py — H-003 Rev-C validated)
- [x] Dataset published (Zenodo DOI: 10.5281/zenodo.21225683)
- [ ] Peer review initiated
- [ ] Hardware prototype built
- [ ] Field tests scheduled
- [ ] Independent replication

## Validated Metrics (Simulation — Unverified by Physical Experiment)
| Parameter | Value |
|-----------|-------|
| Nightly capture (per m2) | 12.91 kWh/m2 |
| 7-night cumulative (10m2 array) | 82.98 kWh |
| Stirling discharge capacity | 24.89 kWh @ 3.11 kW |
| Passive loss rate | 1.056 kWh/day |
| Solar first-pass absorption | ~98% (volumetric open-cell concrete) |
| System architecture | Open-loop (breathes ambient, exhausts to atmosphere) |

## Scientific Questions Requiring Peer Review

### 1. Thermodynamics — Carnot Ceiling Boundary Conditions
Current calculation uses 3K deep space cold sink giving 99.14% efficiency, which overstates realizable efficiency for atmospheric system. Need corrected model using effective sky temperature (250-270K typical for radiative cooling to atmosphere at night).

Current: eta_Carnot = 1 - 3/350 = 0.9914 (99.14%)
Ambient baseline: 1 - 300/350 = 14.3%

Ask: Verify corrected Carnot ceiling with realistic radiative sky temp. Deliver equation with citations. Time: 1-2 hrs.

### 2. Heat Transfer — Pore-Scale Convection Model
Underground labyrinth filled with open-cell concrete forces air through pores. Current model assumes massive surface-area gain but lacks CFD validation. Need: effective Nusselt number for forced convection through open-cell foam concrete (porosity 60-80%), residence time vs heat transfer, pressure drop across porous medium.

Ask: CFD simulation or analytical derivation validating pore-level heat exchange. Time: 3-5 hrs.

### 3. Materials Science — AE-GFRC Pumpability
Autonomous pneumatic pumping of aerated GFRC with zirconium substitution requires verified pressure curves. Need: mix design protocol, slump flow test, pump trial, compressive strength cubes, thermal conductivity test (ASTM C177).

Ask: Lab procedure + predictive pump pressure model. Time: 5-8 hrs.

## How to Contribute
| Expertise Area | Contribution Type | Time | Output |
|---------------|-------------------|------|--------|
| Thermodynamics | Carnot ceiling w/ sky temp | 1-2 hr | Verified equation |
| Heat Transfer | Pore-scale CFD model | 3-5 hr | Simulation or proof |
| Concrete/Materials | AE-GFRC pump protocol | 5-8 hr | Lab test procedure |
| Electrical Eng | TEG/Stirling generator BOM | 2-3 hr | Component spec |
| Structural Eng | Ferrocement tank wall calc | 2 hr | Thickness spec sheet |
| Systems Review | Full-cycle integration audit | 2 hr | Gap list + critique |

## Data Package
- Validated Dataset: https://doi.org/10.5281/zenodo.21225683
- Initial Dataset: https://doi.org/10.5281/zenodo.21210931
- Main Repo: https://github.com/jesseray718/openroot
- Thermal Repo: https://github.com/jesseray718/aerocement
- IPFS: QmVJxfQmFoTVDp1GRui8bEKJ7x7J154h8RX3EmxQBcCrBt
- Sim Code: research/thermal-systems/thermal_cascade_v2.py
- Spec Docs: WBTE-01.md, CTBS-01.md, AE-GFRC-01.md

## System Architecture (One Integrated Cycle)
Sun -> Volumetric Panel (98% capture) -> Underground Labyrinth (open-cell concrete pores) -> Insulated Ground Battery (thermal storage) -> Stirling/TEG Discharge (power generation) -> Exhaust to Atmosphere (open-loop) -> Pre-cooling Desk (conditions inlet air)

## Attribution and Licensing
- Co-authorship offered for significant contributions
- CHANGELOG.md credit for minor fixes
- Copyright: One Human Family (collective)
- Docs: CC-BY-SA 4.0 | Code: GPL v3

## Contact
- GitHub: @jesseray718
- Issue: #3 Call to Builders
- Email: jrm8908@proton.me

Generated: 2026-07-07
Spec Version: 0.2-beta
