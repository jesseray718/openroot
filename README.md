# OpenRoot

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20549528.svg)](https://doi.org/10.5281/zenodo.20549528)
[![PoPW ledger](https://img.shields.io/badge/PoPW-v1.2.1-blue)](https://github.com/jesseray718/openroot/releases/tag/v1.2.1-popw-ledger)
[![thermo](https://img.shields.io/badge/thermo-v1.1.0-blue)](https://github.com/jesseray718/openroot/releases/tag/v1.1.0-native-thermo)
[![CI](https://github.com/jesseray718/openroot/actions/workflows/tests.yml/badge.svg)](https://github.com/jesseray718/openroot/actions/workflows/tests.yml)
[![License: GPL v3](https://img.shields.io/badge/code-GPL--3.0-blue.svg)](LICENSE)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/docs-CC--BY--SA--4.0-lightgrey.svg)](LICENSE-docs.md)

Open-source hardware that lives on open-source software.  
**Updates are advancements.** The repo is the growing web: each verified file, mix, ledger line, and skill is a node. No patents. Ever.

η = useful_joules / human_joules. We never claim greater than 100% thermodynamic efficiency.

**Founded by:** Jesse McMillen — Sikeston, Missouri  
**Archive:** [DOI 10.5281/zenodo.20549528](https://doi.org/10.5281/zenodo.20549528)  
**Contact:** jrm8908@proton.me

---

## What OpenRoot Is

1. **Open hardware library** — CC-BY-SA 4.0 docs / GPL-3.0 code.
2. **Knowledge commons** — handbook, skills, seeds, workflows. Anyone can run and improve them offline.
3. **PoPW / ACRE** — claims minted only for verified physical work. No pre-mine. No speculation.

Core organs: AeroCement volumetric exchangers, AeroDisk solar stack-effect panels, ferrocement domes and double-catenary stressed-skin shells, Black Locust coppice RMH, UNE computational_flow, fractal lattice, PoPW ledger.

---

## AeroCement — Open-Cell Volumetric Material

Opencell (AeroCement) is related to aircrete but does not collapse at critical foam mass.

A thixotropic surfactant gel locks the matrix when ordinary aircrete bubbles would pop and the pour would fall in. Mix direction (already documented): xanthan in alcohol + Dawn Ultra + water → gel. Ratio **1 part gel : 2 parts cement**. Agitation entrains air. At the old collapse point the gel holds shape. Voids stay interconnected. The pour becomes a stable, breathable open-cell heat exchanger that can be cast, pumped, or printed.

**Stator-motor mixing + closest packing.**  
A rotor-stator drives bubble diameter down and bubble count up toward densest equal-sphere packing (HCP / FCC, coordination 12, packing fraction π/(3√2) ≈ 74%). Real foam is polydisperse, so true close-pack is a target, not a claim. Halving radius doubles surface area per volume. Finer cells raise capillary area and spread stress.

**Alkali-resistant glass fiber, ≥20% zirconium.**  
AR-GFRC in the paste. Combined with the open-cell matrix the mix can be lighter and stronger than ordinary concrete, and potentially pumpable over long distances with less labor.

That single material change turns a failed insulation foam into high-S/V thermal mass and structure.

Full notes: `library/kai-sandbox/openroot-ecosystem/aerocement/docs/MATERIAL_SCIENCE_NOTES.md`  
Handbook seed: `OPENROOT_HANDBOOK.md` §4 (AERO-GFRC-001)

---

## Thermal Cascade (Heat / Cold / Work)

Same open-cell matrix, three jobs. Passive after construction. No grid fans. No pumps on the thermal loop.

1. **Heat**  
   Paint the open-cell surface black or load activated charcoal. Volumetric absorber. Phi-spiral air path. Stack effect + turbulence. Dump heat into a copper coil inside an insulated ferrocement tank.

2. **Cold**  
   Same matrix, kept wet, air dried first by desiccant. Evaporative area is every pore, not only tunnel walls. Store cold in a **second** insulated ferrocement tank. Two tanks. Never combined.

3. **Work**  
   The ΔT drives a Stirling + flywheel for shaft work and a TEG only where electricity is actually required. Heat as heat. Cold as cold. Work as work.

**Hard geometry of the loop**

Fresh air → desiccant → underground labyrinth **FILLED SOLID** with wet AeroCement (target 500–2,000 m²/m³) → Cold Tank B (radiative night-sky lid) → hot side / absorber → Hot Tank A → Stirling → back to desiccant.

Output air aims at ground temperature on a hot day. Same physics class as a ground-source heat pump. We do not claim magic COP.

### Black Locust coppice RMH (carbon-negative heat source)

Replace or back the solar absorber with a rocket mass heater fired on **coppiced Black Locust**. Locust coppice is far easier to harvest than conventional firewood and regenerates. Same open-cell cascade: RMH supplies the hot end; labyrinth + wet AeroCement still do cold and storage; Stirling still takes the ΔT. Heat, cold, and shaft work stay in one loop. Fuel is a renewable, coppiced input — not a grid.

RMH + labyrinth comparison and H-003 live in `projects/aerocement/` and the aerocement calc package.

---

## AeroDisk — separate organ (solar stack-effect panels)

AeroDisk is **not** the underground labyrinth and **not** the RMH.

It is a panel / disk absorber for **stack-effect solar air**. Dark, high-S/V open-cell or plated faces sit in sun. Heated air rises through a designed throat. Chimney / stack effect is the pump. No fan.

Use AeroDisks:

- as the hot-side collector feeding Hot Tank A
- as roof or wall panels that preheat the cascade
- as ACRE-0001 “Seed Core + Aero-Disc absorption” artifacts

Do not pour the labyrinth and call it an AeroDisk. Disks are above-grade solar stack panels. The labyrinth is below-grade wet volumetric exchanger.

Ledger pointer: `seed-core/ledger/eta_ledger.jsonl`

---

## Shelter — ferrocement, domes, catenary stress-skin

- Cardboard geodesic panels (acetone + silicone treated, flanged triangles): 1v emergency shelter to large geodesic.
- **Double-catenary stressed-skin ferrocement shells** — pure compression geometry. AeroCement as core inside the skins.
- Thin ferrocement tanks and domes as the insulated vessels on both sides of the cascade.

Monolithic stress-skin catenary arch: self-supporting shell, no frame. The open-cell core is fill, not the compression skin.

---

## ACRE / PoPW

Work is measured in joules. Verified physical work mints ACRE claims. Two independent validators. Replicating a known node in an already-validated climate earns 0 new knowledge mint.

Release: [v1.2.1-popw-ledger](https://github.com/jesseray718/openroot/releases/tag/v1.2.1-popw-ledger)

---

## Hard Rules

1. Never claim greater than 100% thermodynamic efficiency
2. 21-day wet cure — non-negotiable
3. Tunnel FILLED SOLID — never lined or walled
4. Two separate tanks — never combined
5. Desiccant at intake only
6. AeroDisk ≠ labyrinth ≠ RMH. Name the organ you are building.
7. No patents. Ever.
8. Failures are data — document honestly
9. Serve the least first

---

## Status

Theoretical physics of the cascade documented. Mixes documented. First instrumented prototype waits on a southeast Missouri build site.

Workshop offer: free or materials-at-cost for anyone in the region who will measure and share results.

## Permanently published

- Zenodo: https://doi.org/10.5281/zenodo.20549528
- IPFS CID: `QmcMjnAVN9FbQ77VbwMPMCteb93U7W4REdZmZbPqoMBE4F`

Skills: `/home/jesse/openroot/skills-library` and `library/kai-sandbox/skills/`  
Workflows: `workflow/`  
Handbook: `OPENROOT_HANDBOOK.md`

> There shall come a time when the earth is weeping and the animals are suffering, and from all corners of the earth shall come a tribe of all colors, classes, and creeds, and through their actions they shall make the earth green again.
> — Hopi prophecy

## Wiki

- [Handbook](https://github.com/jesseray718/openroot/wiki/Handbook)
- [Material science](https://github.com/jesseray718/openroot/wiki/Material-Science)
- [AeroCement](https://github.com/jesseray718/openroot/wiki/AeroCement)
- [Thermal cascade + RMH](https://github.com/jesseray718/openroot/wiki/Thermal-Cascade)
- [AeroDisk](https://github.com/jesseray718/openroot/wiki/AeroDisk)
- [Shelter](https://github.com/jesseray718/openroot/wiki/Shelter)
- [Skills](https://github.com/jesseray718/openroot/wiki/Skills)
- [Offline 7B coder](https://github.com/jesseray718/openroot/wiki/Offline-7B-Coder)
