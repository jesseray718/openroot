# OpenRoot

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20549528.svg)](https://doi.org/10.5281/zenodo.20549528)
[![PoPW ledger](https://img.shields.io/badge/PoPW-v1.2.1-blue)](https://github.com/jesseray718/openroot/releases/tag/v1.2.1-popw-ledger)
[![thermo](https://img.shields.io/badge/thermo-v1.1.0-blue)](https://github.com/jesseray718/openroot/releases/tag/v1.1.0-native-thermo)
[![CI](https://github.com/jesseray718/openroot/actions/workflows/tests.yml/badge.svg)](https://github.com/jesseray718/openroot/actions/workflows/tests.yml)
[![License: GPL v3](https://img.shields.io/badge/code-GPL--3.0-blue.svg)](LICENSE)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/docs-CC--BY--SA--4.0-lightgrey.svg)](LICENSE-docs.md)

Open-source hardware that lives on open-source software.
**Updates are advancements.** The repo is the growing web: each verified file, mix, ledger line, and skill is a node. No patents. Ever.

η = useful_joules / human_joules.
Heat-engine η, act η, EROI, and sim scores are four different quantities (N14).
We never claim greater than 100% thermodynamic efficiency.

**Founded by:** Jesse McMillen — Sikeston, Missouri
**Node Zero:** southeast Missouri
**Archive:** [DOI 10.5281/zenodo.20549528](https://doi.org/10.5281/zenodo.20549528)
**Contact:** jrm8908@proton.me
**GitHub:** https://github.com/jesseray718/openroot

---

## What OpenRoot Is

1. **Open hardware library** — CC-BY-SA 4.0 docs / GPL-3.0 code.
2. **Knowledge commons** — handbook, skills, seeds, workflows. Anyone can run and improve them offline.
3. **PoPW / ACRE** — claims minted only for verified physical work. No pre-mine. No speculation.

Core organs: AeroCement volumetric exchangers, AeroDisk solar stack-effect panels, ferrocement domes and double-catenary stressed-skin shells, Black Locust coppice RMH, UNE computational_flow, fractal lattice, PoPW ledger.

This README is the public map. Load-bearing numbers live in `CLAIMS.md`. What talks to what lives in `INTEGRATION.md`. What this tree is lives in `MANIFEST.md`.

---

## Premise (architecture, not gadget)

Grid mechanical work from fuel is typically \~10–26% after plant, line, and motor conversions. That is an architecture tax, not a law of nature.

OpenRoot architecture:

- Capture solar (or coppice fire) as **heat**, not as grid electricity first.
- Move air by **stack effect**. Gravity is free. The sun (or the RMH) makes the density difference.
- Store in **dirt and water**. Two tanks. Never one.
- Use latent heat of water as a **transport mechanism**, not as a second sun.
- Extract shaft work from ΔT (Stirling + flywheel). Electricity only where electricity is required.
- Use heat as heat. Cold as cold. Work as work.

That is the whole argument. Everything else is organs, mix, and measurement.

---

## AeroCement — Open-Cell Volumetric Material

Opencell (AeroCement) is related to aircrete but does not collapse at critical foam mass.

A thixotropic surfactant gel locks the matrix when ordinary aircrete bubbles would pop and the pour would fall in. Mix direction (already documented): xanthan in alcohol + Dawn Ultra + water → gel. Nighthawkinlight method is the public reference. Ratio **1 part gel : 2 parts cement**. Agitation entrains air. At the old collapse point the gel holds shape. Voids stay interconnected. The pour becomes a stable, breathable open-cell heat exchanger that can be cast, pumped, or printed.

**Stator-motor mixing + closest packing.**
A rotor-stator drives bubble diameter down and bubble count up toward densest equal-sphere packing (HCP / FCC, coordination 12, packing fraction π/(3√2) ≈ 74%). Real foam is polydisperse, so true close-pack is a target, not a claim. Halving radius doubles surface area per volume. Finer cells raise capillary area and spread stress.

**Alkali-resistant glass fiber, ≥20% zirconium.**
AR-GFRC in the paste. Combined with the open-cell matrix the mix can be lighter and stronger than ordinary concrete, and potentially pumpable over long distances with less labor.

**Activated-carbon / charcoal load.**
Carbon in the matrix raises solar absorptivity and IR emissivity. Prototype charcoal-infused open-cell pours exist. α = 0.98 is a **design target**, not a published ASTM E903 hang.

That single material change turns a failed insulation foam into high-S/V thermal mass and structure.

### Design-range material table (unmeasured ranges stay ranges)

| Property | Design range | Status |
| --- | --- | --- |
| Compressive strength | H1 target ≥15 MPa after 21-day wet cure | OPEN until ASTM C39 |
| Dry density | 50–90 lb/ft³ foamed; AE-GFRC structural target ≤ 1,200 kg/m³ | OPEN |
| Open-cell porosity | 65–80% interconnected | OPEN |
| Pore diameter | 0.5–5 mm typical | OPEN |
| Thermal conductivity | 0.15–0.40 W/(m·K) vs \~1.7 for ordinary concrete | OPEN |
| Solar absorption α | target 0.98 carbon-doped | OPEN (ASTM E903 / C1371) |
| Permeability | 10⁻⁸–10⁻⁶ m² class | OPEN |
| Water absorption | 15–25% by weight (wet labyrinth) | OPEN |
| Internal S/V | target 500–2,000 m²/m³ in the filled labyrinth | OPEN |

**Mix direction per cubic yard (starting recipe, not a certified mix):**
Portland I/II 400–500 lb · fine sand passing #8 800–1,200 lb · water 200–250 lb (w/c 0.45–0.55) · pre-formed protein foam 6–8 cu ft · activated carbon 20–30 lb · optional silica fume 5–10% of cement · AR glass fiber 2–5% by volume for AE-GFRC.

Foam is **pre-formed**. Never dump foaming agent into the mixer. Paste first, fold foam. Over-mix collapses cells. One continuous lift. Cover and keep wet **21 days**. N13 is not optional.

Full notes: [`MATERIAL_SCIENCE_NOTES.md`](https://github.com/jesseray718/openroot/blob/main/library/kai-sandbox/openroot-ecosystem/aerocement/docs/MATERIAL_SCIENCE_NOTES.md) · [wiki](https://github.com/jesseray718/openroot/wiki/Material-Science)
Handbook seed: [`OPENROOT_HANDBOOK.md`](https://github.com/jesseray718/openroot/blob/main/OPENROOT_HANDBOOK.md) §4 (AERO-GFRC-001) · [wiki](https://github.com/jesseray718/openroot/wiki/Handbook)

---

## Thermal Cascade (Heat / Cold / Work)

Same open-cell matrix, three jobs. Passive after construction. No grid fans. No pumps on the thermal loop.

1. **Heat**
   Paint the open-cell surface black or load activated charcoal. Volumetric absorber. Air flows **through** the matrix, not over a plate. Phi-spiral / stack path. Dump heat into a copper coil inside an insulated ferrocement tank (Hot Tank A).
2. **Cold**
   Same matrix, kept wet, air dried first by desiccant. Evaporative area is every pore, not only tunnel walls. Store cold in a **second** insulated ferrocement tank (Cold Tank B). Two tanks. Never combined.
3. **Work**
   The ΔT drives a Stirling + flywheel for shaft work and a TEG only where electricity is actually required.

**Hard geometry of the loop**

Fresh air → desiccant → underground labyrinth **FILLED SOLID** with wet AeroCement (target 500–2,000 m²/m³) → Cold Tank B (radiative night-sky lid) → hot side / AeroDisk or RMH absorber → Hot Tank A → Stirling → back to desiccant.

At \~10 ft in temperate ground, soil is near 55°F year-round. That is the cold sink class. Output air aims at ground temperature on a hot day. Sub-wet-bulb numbers (35°F / 2°C) are an **evaporative target**, not a hang. Same physics class as a ground-source heat pump plus evaporative assist. We do not claim magic COP.

### Why desiccant is not optional

If humid air enters the wet labyrinth:

1. Evaporative driving force collapses.
2. Confined humidity rusts steel.
3. Mold is a habitable-space failure.

Desiccant sits between hot-side outlet and labyrinth inlet. Regen from surplus heat, not from the useful cold stream.

### Black Locust coppice RMH (carbon-negative heat source)

Replace or back the solar absorber with a rocket mass heater fired on **coppiced Black Locust**. Locust coppice is easier to harvest than conventional firewood and regenerates. Same open-cell cascade: RMH supplies the hot end; labyrinth + wet AeroCement still do cold and storage; Stirling still takes the ΔT. Fuel is a renewable coppiced input — not a grid.

RMH + labyrinth comparison and H-003 live in `projects/aerocement/` and the aerocement calc package (`calc_solar` uses 931 W/m² as the locked net-to-air design constant).

---

## Energy ledger — First Law first (N14)

Peak AM1.5 design point, per m² of collector face. These are **model numbers**. They are not a pad measurement.

| Step | Quantity | Value | Grade |
| --- | --- | --- | --- |
| 1 | Incident solar | 1000 W | design AM1.5 |
| 2 | Absorbed at α=0.98 | 980 W | OPEN (needs spectral hang) |
| 3 | Net to airflow after \~5% face loss | **931 W** | design constant used by `aerocement_calc` |
| 4 | Latent transport at 0.5 kg/h evaporation | \~314 W | transport, **not new energy** |
| 5 | First-Law budget from the sun | **931 W in = work + heat-to-ground + loss** | conservation |

**Do not add 931 + 314 and call it “1245 W created.”**
The 314 W of latent enthalpy is solar energy that changed form when dry air evaporated water off wet pores. When that vapor condenses, the same joules reappear as heat. Net water-cycle energy added to the closed books is zero. The benefit is **enhanced transport** and the chance of sub-wet-bulb air — not a second sun.

**Do not add heat + cooling + shaft work and call it 2197 W or “220% efficiency.”**
Moving 854 W of heat into ground mass is one physical stream. Calling that same stream “heating service” in winter and “cooling service” in summer is a **service count**. Service count is allowed in a grant packet if labeled as service. It is forbidden as thermodynamic efficiency (N14).

Honest split of the 931 W:

- Shaft work from a low-ΔT Stirling is a **slice** of the heat that actually crosses the engine, at a fraction of Carnot. Carnot for 350 K / 275 K is 21.4%. 60% of Carnot is 12.9% of the heat that goes through the engine — not 12.9% of 931 W unless you prove that much heat crosses the working fluid.
- Remainder is heat dumped to ground / Hot Tank A.
- Friction at 0.1 W is a placeholder, not a measured duct loss.

**Passive transport ratio** (heat moved / electrical watts on the loop) can be large because electrical watts on the loop are designed to be near zero. That ratio is **not** a heat-engine efficiency and must not be written as COP = 21,972 in a sentence that a reviewer will read as perpetual motion.

Replication math for builders: use 931 W/m² net-to-air and the two-tank geometry. Ignore headline multipliers.

Corrected ledger script: `projects/aerocement/aerocement_ledger.py`.

---

## AeroDisk — separate organ (solar stack-effect panels)

AeroDisk is **not** the underground labyrinth and **not** the RMH.

It is a panel / disk absorber for **stack-effect solar air**. Dark, high-S/V open-cell or plated faces sit in sun. Heated air rises through a designed throat. Chimney / stack effect is the pump. No fan.

Use AeroDisks:

- as the hot-side collector feeding Hot Tank A
- as roof or wall panels that preheat the cascade
- as ACRE-0001 “Seed Core + Aero-Disc absorption” artifacts

Do not pour the labyrinth and call it an AeroDisk. Disks are above-grade solar stack panels. The labyrinth is below-grade wet volumetric exchanger.

Order-of-magnitude stack drive (design, not hang):
ρ(27°C) ≈ 1.177 kg/m³, ρ(77°C) ≈ 1.028 kg/m³.
ΔP = g · H · (ρ_c − ρ_h) ≈ 14.6 Pa at H = 10 m.
Mass flow from Q = ṁ c_p ΔT at 931 W and ΔT ≈ 50 K is \~0.018 kg/s per m² if that ΔT is actually achieved. Duct velocity target 1–3 m/s so loss stays under stack pressure.

Ledger pointer: [`seed-core/ledger/eta_ledger.jsonl`](https://github.com/jesseray718/openroot/blob/main/seed-core/ledger/eta_ledger.jsonl)

---

## Shelter — ferrocement, domes, catenary stress-skin

- Cardboard geodesic panels (acetone + silicone treated, flanged triangles): 1v emergency shelter to large geodesic.
- **Double-catenary stressed-skin ferrocement shells** — pure compression geometry. AeroCement as core inside the skins.
- Thin ferrocement tanks and domes as the insulated vessels on both sides of the cascade.
- GFRC skin: 3/8–1/2 in, \~5% AR glass, 6–8 ksi class compressive as a design range.
- Ferrocement tanks: 1–1.5 in mortar, 2–3 layers 1 in mesh, pneumatic hog-ring ties.

Monolithic stress-skin catenary arch: self-supporting shell, no frame. The open-cell core is fill, not the compression skin.

---

## Life — food organs (supporting pillar)

Not a thermal claim. Separate hangs.

- **Black Locust keystone guild** — coppice fuel + nitrogen + fence + bee forage. Same species that fires the RMH.
- **Vertical quail towers** — high protein per footprint, manure to aquaponics.
- **Ferrocement aquaponics** — closed loop on the same tank skill as Cold Tank B / Hot Tank A.
- **Heirloom seed bank** — offline, local, forkable.

Food joules do not get added to the 931 W solar ledger.

---

## Hypotheses (falsifiable, not slogans)

Primary material (charcoal open-cell) is prototyped. These supporting claims stay OPEN until the named test exists.

| ID | Claim | Falsifier |
| --- | --- | --- |
| H1 | AE-GFRC with ≥20% Zr-class binder sub, air voids as aggregate, ≥15 MPa and ASTM C1550 toughness at dry density ≤ 1,200 kg/m³, pumpable 1,609 m without segregation | fails C39 / C1550 / C1716 at that density or distance |
| H2 | Spherical voids beat mined lightweight aggregate on strength-to-weight at equal or lower cement | measured specific strength below LWAC control |
| H3 | Purpose-built pneumatic placement ≥300 m³ per operator-hour | sustained rate stays in the 30–50 m³/h foam-pump class |
| H4 | N pumps place volume V in T = V/(300N) with zero hand placement | labor or blockage dominates |
| H5 | Delta-T vehicle: drag-cooled open-cell radiator sustains a useful Stirling ΔT | wind-tunnel + bench Stirling cannot hold work-positive ΔT |
| H6 | Purpose-built AE-GFRC pump ≥300 m³/h at ≤30 bar | foam collapses under sustained pressure |
| H-003 | Instrumented solar + labyrinth node in Sikeston climate matches the 931 W/m² class closely enough to beat a measured electrical baseline on η_act | pad sensors show otherwise |

Nulls H01 / H05 / H06 stay published next to the claims. A rejected hang is data.

Required tests: ASTM C39, C1550, C138, C231/C457, C1716, E903, C1371, wind tunnel 5/15/25 m/s, Stirling bench, 100→500→1000→1609 m pump trial.

**H5 numbers in old drafts (180–300 kW, 1500 kW radiator exchange) are upper-bound arithmetic, not a vehicle.** Do not reprint them as performance.

---

## Case pattern (why this repo exists)

Centralized economic, regulatory, and professional power repeatedly creates or intensifies problems that already have simple, low-tech, decentralized answers — then obstructs those answers. OpenRoot’s counter is not a complaint. It is dependency-free tooling:

- Benefit measured at the recipient.
- Lowest node first (N07).
- Unnecessary suffering is the error signal.
- Cooperation voluntary.
- Knowledge forkable and offline.

---

## ACRE / PoPW

Work is measured in joules. Verified physical work mints ACRE claims. Two independent validators. Replicating a known node in an already-validated climate earns 0 new knowledge mint.

Building the first node in a new climate zone, fixing a documented flaw, shipping a new tool, or writing a new skill doc is mintable. Copying node #47 in a climate already validated is real work and zero new-knowledge mint.

ACRE token deployment is **conceptual**. No pre-mine. No airdrop. Spec: `tokens/ACRE_SPECIFICATION.md`.
Release: [v1.2.1-popw-ledger](https://github.com/jesseray718/openroot/releases/tag/v1.2.1-popw-ledger)

Bounty board is a map of unmet needs, not a live payroll.

---

## Stack (sovereign edge)

| Node | Role |
| --- | --- |
| Samsung A15 + Termux | Governor, file bus, light inference, ACRE claims |
| OptiPlex 3060 | nomic-embed-text :11434 · qwen2.5-coder :8080 · FTS5-first SQLite RAG |
| Syncthing | Phone ↔ box. No unique-ID theatre when folders are Up to Date |

Related public trees: `openroot` · `openroot-foundation` · `openroot-thesis` · `wisdom-scaffold` · `agape-une` / `une` · `black-locust-rmh` · `agape-primitives`

Phone-first live paths (absolute):

- `/data/data/com.termux/files/home/openroot`
- `/storage/emulated/0/openroot`
- Box: `/home/jesse/openroot`
- Calc: `/data/data/com.termux/files/home/aerocement/aerocement_calc/`

---

## Hard Rules

1. Never claim greater than 100% thermodynamic efficiency.
2. 21-day wet cure — non-negotiable (N13).
3. Tunnel FILLED SOLID — never lined or walled.
4. Two separate tanks — never combined.
5. Desiccant at intake only.
6. AeroDisk ≠ labyrinth ≠ RMH. Name the organ you are building.
7. Latent heat is transport. Do not add it to solar input.
8. Service-count ≠ First Law. Do not sum heat+cold+work against one watt of sun and call it efficiency.
9. No patents. Ever.
10. Failures are data — document honestly.
11. Serve the least first.

---

## Build sequence (Node Zero, compressed)

**Days 1–3.** Survey south aperture. Mark 5–15° tilt. Excavate labyrinth trench \~10 ft. Pour porous floor. Sump at low point. Start 21-day clock.
**Days 4–24.** Walls and baffles of wet-capable AeroCement. Capillary / drip feed. Desiccant housing. Ferrocement cold tank + copper coil. R-19 between hot and cold ducts. Backfill with no voids. Cast AeroDisk / panel faces on the same clock.
**Days 4–14 concurrent.** Frame panels. Series stack if you need chimney height. Connect: panel → desiccant → Stirling hot → labyrinth → cold coil → return.
**Days 25–35.** Stirling on the real ΔT, belt, optional alternator / TEG. Measure RPM, torque, ΔT_hot, ΔT_cold, airflow. No brochure η.
**Days 25–50.** Dome pad. Treated cardboard 1v (or specified frequency). Flanged click. AeroCement or ferrocement skin. 21-day cure per lift.

Instrument before you advertise. Cheap sensors beat another manifesto.

---

## Status

Theoretical physics of the cascade documented. Mixes documented. Charcoal open-cell pours exist. First **instrumented** prototype waits on a southeast Missouri build site.

Workshop offer: free or materials-at-cost for anyone in the region who will measure and share results.

---

## Permanently published

- Zenodo: https://doi.org/10.5281/zenodo.20549528
- IPFS CID: `QmcMjnAVN9FbQ77VbwMPMCteb93U7W4REdZmZbPqoMBE4F`

Skills: [`library/kai-sandbox/skills/`](https://github.com/jesseray718/openroot/tree/main/library/kai-sandbox/skills) · [wiki](https://github.com/jesseray718/openroot/wiki/Skills)
Workflows: [`workflow/`](https://github.com/jesseray718/openroot/tree/main/workflow)
Handbook: [`OPENROOT_HANDBOOK.md`](https://github.com/jesseray718/openroot/blob/main/OPENROOT_HANDBOOK.md) · [wiki](https://github.com/jesseray718/openroot/wiki/Handbook)

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

## Gate files

- `MANIFEST.md` — what this tree is
- `CLAIMS.md` — every load-bearing number, graded
- `INTEGRATION.md` — sister trees and live paths
- `INTEGRATION_CHECKLIST.md` — four boxes

## Support

**SimpleX:** https://smp9.simplex.im/a#vklZrSjZTQdgXBqW_sLK1h5FeajDoa7wTaSWGSw62Sw

| Solana | 3fF26gcj1ednMUASxJxo1dt5rQ2ZegXbH7k4ynJazerk |
| Bitcoin | bc1qq69dze04yul5cl5lgv3hakg4scxfzq3swje6ey |
| Ethereum | 0x8eA4dBF495ef2Ab6E4371C75060390563b79c138 |

The project succeeds when it no longer needs Jesse McMillen.

One pour. One node. One warrior at a time.

*CC-BY-SA 4.0 (Hardware) | GPL v3 (Software) | No Patents. Ever.*
