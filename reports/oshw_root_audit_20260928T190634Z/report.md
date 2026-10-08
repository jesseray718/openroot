# OpenRoot OSHW Root Audit

- Generated: `2026-09-28T14:06:34-05:00`
- Host: `optiplex3060`
- Repo: `/home/jesse/openroot`
- Mode: read-only audit; no source edits, no staging, no commit, no push, no GitHub mutation, no service/process mutation.
- Hold: `/home/jesse/openroot/data/operator_holds/HUMAN_HOLD`

## Repository identity and public remotes

```text
/home/jesse/openroot
main
HEAD=2e9c68398fb4d2be67c08bde2441bf8826925788
DATE=2026-09-27T23:58:33-05:00
SUBJECT=[FIX] handoff: fill PR #9 URL placeholder (AI-assisted, human-gated)
Reh1t	https://github.com/Reh1t/openroot.git (fetch)
Reh1t	https://github.com/Reh1t/openroot.git (push)
origin	git@github.com:jesseray718/openroot.git (fetch)
origin	git@github.com:jesseray718/openroot.git (push)
upstream	https://github.com/jesseray718/openroot.git (fetch)
upstream	https://github.com/jesseray718/openroot.git (push)
MM .gitignore
A  bin/concept_sweep_v1.sh
A  bin/doc_gap_scan_v1.py
A  bin/mistake_index_v1.py
 M bin/refine_next.sh
A  bin/tidbit_registry_v1.py
A  context_bridge/concepts/a_language_agape_v1.md
A  context_bridge/concepts/modular_turing_tidbit_v1.md
A  context_bridge/handoffs/session-20260928_004510-superlinear-instruments.md
A  context_bridge/handoffs/session-20260928_010158-concepts-banked-corrected-sweep.md
?? bin/a15_courier_endpoint_v1.py
?? bin/dedup_pipeline_v1.py
?? bin/expertise_orchestrator_v1.py
?? bin/lumo_relay_full_v1.py
?? bin/openroot_deepdive_v1.sh
?? bin/openroot_local_loop_v2.sh
?? bin/quarantine_pyfails_final_v2/
?? bin/refine_next.sh.bak_20260928_051638
?? bin/run_expertise_auto_v1.py
?? bin/vision_all_v1.sh
?? context_bridge/compost-20260926_053011.md
?? context_bridge/compost-20260926_160713.md
?? context_bridge/compost-20260926_160847.md
?? context_bridge/compost-20260926_160848.md
?? context_bridge/compost-20260927_144218.md
?? context_bridge/compost-20260927_224935.md
?? context_bridge/compost-20260928_053006.md
?? context_bridge/composted_scripts_20260927/
?? context_bridge/concept_mining/
?? context_bridge/concept_sweeps/
?? context_bridge/concepts/core_atomic_enum_draft.md
?? context_bridge/court-v6-report-20260926_040026.md
?? context_bridge/court-v6-report-20260927_144215.md
?? context_bridge/court-v6-report-20260928_040010.md
?? context_bridge/gov_promote_proofs_20260928_041935/
?? context_bridge/gov_smoke_final_20260928_045548/
?? context_bridge/governor_promote_20260928_041935.md
?? context_bridge/grep_sweep_20260927_205737/
?? context_bridge/grep_sweep_20260927_205916/
?? context_bridge/handoffs/session-20260926_225700-ladder-7of8.md
?? context_bridge/handoffs/session-20260927_230746-fusion-sealed-2265c4aa.md
?? context_bridge/handoffs/session_20260926T221516Z_c6f0d97375d6355b.md
?? context_bridge/handoffs/session_20260926T221629Z_6916f7ea0432b4f2.md
?? context_bridge/handoffs/session_20260926T221842Z_d97bcefd328c622f.md
?? context_bridge/handoffs/session_20260926T221843Z_c6414b332a20e5d7.md
?? context_bridge/handoffs/session_20260926_215535_55b7ba7c.md
?? context_bridge/handoffs/session_20260926_215639_69ae6e70.md
?? context_bridge/handoffs/session_20260926_220435_6c2d280e.md
?? context_bridge/handoffs/session_20260926_220617_80fa6c9e.md
?? context_bridge/handoffs/session_20260926_220805_6953c9af.md
?? context_bridge/handoffs/session_20260928T040209Z_d7e48356999db7ff.md
?? context_bridge/handoffs/session_session_20260926T221132+0000_7c2056b18e27b61c.md
?? context_bridge/handoffs/session_session_20260926T221133+0000_5a4cf6fec1712d95.md
?? context_bridge/hive_canonical_20260928_041449/
?? context_bridge/kai_deep_harvest_20260928_024955/
?? context_bridge/lumo_inbox/
?? context_bridge/mistake_solutions/06ad87aa44efc30b.md
?? context_bridge/mistake_solutions/193af16dcf503af5.md
?? context_bridge/mistake_solutions/27ab944372909f1c.md
?? context_bridge/mistake_solutions/a71a4e72670407be.md
?? context_bridge/mistake_solutions/ab68e66064bffdd0.md
?? context_bridge/mistake_solutions/afbd8ad75c5a820b.md
?? context_bridge/mistake_solutions/e579225f90e59b48.md
?? context_bridge/relay-recovery-20260926_040359.md
?? context_bridge/session-handoff-20260928-0456/
?? context_bridge/tree_optiplex_home.txt
?? context_bridge/tree_optiplex_openroot.txt
?? context_bridge/tree_optiplex_src.txt
?? context_bridge/tree_snapshot_latest.txt
?? context_bridge/turing_tidbits/
?? data/kai_import_20260928_015017.tar.gz
?? data/ladder_diagnostics/
?? data/openroot_knowledge/
?? data/operator_holds/
?? data/superlinear/
?? data/turing_tidbits/
?? hash_assign_smoke/
?? hash_assign_v1.sh
?? quarantine_compile_fails_20260926_142638/
?? quarantine_handoff_corrupt/
```

## Human mutation hold

```text
-rw------- 1 jesse jesse 657 Sep 28 08:06 /home/jesse/openroot/data/operator_holds/HUMAN_HOLD
```

## Exact OSHW manifest

```text
CONTRIBUTING.md                                 contribution_guide        1559   PRESENT
designs/thermal-cascade/bom/BOM.csv             measurement_data          429    PRESENT
designs/thermal-cascade/bom/BOM.csv             thermal_bom_csv           429    PRESENT
designs/thermal-cascade/BOM.md                  thermal_bom_markdown      1468   PRESENT
designs/thermal-cascade/BUILD.md                thermal_build             1432   PRESENT
designs/thermal-cascade/INTAKE.md               thermal_intake            2149   PRESENT
designs/thermal-cascade/LICENSE.md              thermal_license           451    PRESENT
designs/thermal-cascade/MEASUREMENTS.md         thermal_measurements      1162   PRESENT
designs/thermal-cascade/metadata.yaml           thermal_metadata          598    PRESENT
designs/thermal-cascade/PROVENANCE.md           thermal_provenance        3139   PRESENT
designs/thermal-cascade/README.md               thermal_readme            1319   PRESENT
designs/thermal-cascade/release-manifest.json   measurement_data          550    PRESENT
designs/thermal-cascade/release-manifest.json   thermal_release_manifest  550    PRESENT
designs/thermal-cascade/router_context.json     measurement_data          1291   PRESENT
designs/thermal-cascade/SAFETY.md               thermal_safety            1679   PRESENT
designs/thermal-cascade/STATUS.md               thermal_status            535    PRESENT
designs/thermal-cascade/SYSTEM.md               thermal_system            4388   PRESENT
designs/thermal-cascade/TEST_PLAN.md            thermal_test_plan         1691   PRESENT
designs/thermal-cascade/THEORY_AND_EVIDENCE.md  thermal_theory_evidence   3719   PRESENT
docs/DESIGN_PACKETS.md                          design_packet_standard    532    PRESENT
docs/EVIDENCE_LEVELS.md                         evidence_standard         526    PRESENT
docs/LICENSING.md                               licensing_guidance        378    PRESENT
docs/OPEN_HARDWARE_STATUS.md                    oshw_status               1426   PRESENT
docs/RELEASE_PROCESS.md                         release_process           3396   PRESENT
docs/REPOSITORIES.md                            ecosystem_map             4565   PRESENT
LICENSE                                         repository_license        35149  PRESENT
path                                            type                      bytes  status
README.md                                       hub_readme                8365   PRESENT
SECURITY.md                                     security_policy           108    PRESENT
```

## Thermal Cascade source artifact inventory

```text
2026-09-25 21:18:39.8133408820	429	designs/thermal-cascade/bom/BOM.csv
2026-09-25 21:18:39.8367609340	418	designs/thermal-cascade/bom/BOM.md
2026-09-25 21:18:39.8588730200	451	designs/thermal-cascade/LICENSE.md
2026-09-25 21:18:39.9047096710	1319	designs/thermal-cascade/README.md
2026-09-25 21:18:39.9269800330	341	designs/thermal-cascade/release/REPRODUCE.md
2026-09-25 21:18:39.9491892290	451	designs/thermal-cascade/docs/system-architecture.md
2026-09-25 21:18:39.9710356660	535	designs/thermal-cascade/docs/safety.md
2026-09-25 21:18:39.9936229940	300	designs/thermal-cascade/docs/results.md
2026-09-25 21:18:40.0162185470	551	designs/thermal-cascade/docs/build-instructions.md
2026-09-25 21:18:40.0380774100	280	designs/thermal-cascade/docs/problem.md
2026-09-25 21:18:40.0602080510	587	designs/thermal-cascade/docs/test-protocol.md
2026-09-25 21:18:40.0820898360	209	designs/thermal-cascade/docs/maintenance.md
2026-09-25 21:18:40.1043055820	386	designs/thermal-cascade/docs/operation.md
2026-09-25 21:18:40.1262102980	227	designs/thermal-cascade/docs/replication-notes.md
2026-09-25 21:18:40.1487983810	203	designs/thermal-cascade/calculations/formulas.md
2026-09-25 21:18:40.1707424210	227	designs/thermal-cascade/calculations/assumptions.md
2026-09-25 21:18:40.1928919170	535	designs/thermal-cascade/STATUS.md
2026-09-26 00:24:04.0265894360	2149	designs/thermal-cascade/INTAKE.md
2026-09-26 01:02:14.1753338490	1291	designs/thermal-cascade/router_context.json
2026-09-26 01:02:14.7191339070	598	designs/thermal-cascade/metadata.yaml
2026-09-26 18:32:27.2868570640	1468	designs/thermal-cascade/BOM.md
2026-09-26 18:32:27.2898570250	1432	designs/thermal-cascade/BUILD.md
2026-09-26 18:32:27.2928569870	1691	designs/thermal-cascade/TEST_PLAN.md
2026-09-26 18:32:27.2958569480	1162	designs/thermal-cascade/MEASUREMENTS.md
2026-09-26 18:32:27.2988569090	1679	designs/thermal-cascade/SAFETY.md
2026-09-26 21:30:30.3826212960	4388	designs/thermal-cascade/SYSTEM.md
2026-09-26 21:47:43.4249479910	3139	designs/thermal-cascade/PROVENANCE.md
2026-09-26 21:47:43.4305154160	3719	designs/thermal-cascade/THEORY_AND_EVIDENCE.md
2026-09-26 22:25:27.1623829740	550	designs/thermal-cascade/release-manifest.json
```

## Editable design sources only

```text
```

## Measurement data candidates

```text
2026-09-25 21:18:39.8133408820	429	designs/thermal-cascade/bom/BOM.csv
```

## Evidence and safety boundary excerpts

```text
--- designs/thermal-cascade/STATUS.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Status — OpenRoot Thermal Cascade

## Evidence level

`L0 — Concept`

## Known

- Add evidence-supported facts only.

## Assumed

- List assumptions separately from measurements.

## Unknown

- List unanswered questions and risks.

## Known limitations

- No independent replication yet.
- No field-performance guarantee.
- Safety-sensitive systems require qualified review.

## Next smallest validation step

Describe one low-risk, reversible test that would increase confidence.

--- designs/thermal-cascade/MEASUREMENTS.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Measurements

## Current status

**No accepted physical measurements are recorded in this packet.**

The packet remains at **L0**. Existing notes, scripts, calculations, archives, simulations, or historical files are not entered as measured physical evidence until they are individually identified, reviewed for provenance, and linked to a documented method and configuration.

## Measurement register

| Test ID | Date | Revision | Claim | Result | Unit | Evidence | Status |
|---|---|---|---|---|---|---|---|
| — | — | — | No accepted measurement yet | — | — | — | L0 |

## Evidence admission rule

Add a result only when it includes:

- The tested configuration and revision
- Test method and conditions
- Instrument identity and known accuracy/calibration
- Raw or inspectable source data
- Units and calculation method
- Uncertainty, limitations, and deviations
- A conservative interpretation

## Prohibited inference

Do not turn archive recovery, simulation output, a design hypothesis, a copied script, or an undocumented historical number into a physical-performance claim.

--- designs/thermal-cascade/SAFETY.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Safety Boundary

## Status

**No safety approval is granted by this packet.** This is an L0 documentation boundary and not professional engineering, electrical, structural, plumbing, pressure-vessel, fire, food-safety, health, legal, or regulatory advice.

## Do not proceed without qualified review

Stop and seek appropriate qualified review before work involving:

- Structural loads or occupied structures
- Pressure, steam, compressed gas, sealed vessels, or vacuum
- High temperature, hot surfaces, molten materials, or fire risk
- Hazardous electricity, batteries, mains power, or unattended controls
- Combustion, fuels, flue gases, carbon monoxide, or indoor air quality
- Potable water, wastewater, food, biological materials, or sanitation
- Toxic, corrosive, reactive, or unknown materials
- Public deployment or use by untrained people

## Future safety record requirements

A future prototype packet must document:

| Requirement | Evidence needed |
|---|---|
| Hazards | Identified hazards and exposed people/materials |
| Controls | PPE, guards, supervision, ventilation, containment, shutdown |
| Limits | Temperature, pressure, electrical, structural, chemical, and operating limits |
| Stop conditions | Observable triggers for immediate shutdown |
| Incident record | Failures, near misses, damage, and corrective action |
| Review | Appropriate independent or qualified review where required |

## Public claim boundary

Do not call the Thermal Cascade safe, certified, code-compliant, field-ready, proven, or suitable for any specific use without documented evidence and appropriate review.

--- designs/thermal-cascade/PROVENANCE.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Provenance Register

## Purpose

This register maps canonical Thermal Cascade architecture and model sources.
It preserves their identity and claim type. Inclusion does not convert a target,
assumption, simulation, code default, or design statement into a measured
physical-performance, safety, certification, build-readiness, or deployment claim.

## Canonical source map

| ID | Source | Role | Current claim type |
|---|---|---|---|
| TC-ARCH-README | `docs/README.md` — SHA-256 `46dfda5a736b2d63e247374a95794397fe006ee9b9c1480095a0cc960125fa87` | Cross-project Heat / Cold / Work architecture | Canonical design architecture |
| TC-SYSTEM-ARCH | `designs/thermal-cascade/docs/system-architecture.md` — SHA-256 `2023c352b07f5ecec277266b9bdafe3727e0cdcdcb4f3e3031ded19e3d37bf21` | Packet system-architecture record | Design architecture |
| TC-HEAT-BALANCE | `docs/research/cascade-heatbalance.md` — SHA-256 `db0a8a73651cda954fbc99ee19e08db73462def94ab757f98982dea23f683bb3` | Heat-balance rationale | Theory/model |
| TC-OPENCELL-ABSORBER | `docs/research/opencell-absorber.md` — SHA-256 `d7c8c426b58e5e6341c1ee01a68090be8bac0bfcd266161b83744ca456204185` | Absorber research/protocol | Measurement protocol; claims pending experiment |
| TC-AEROCEMENT-TRIAD | `bin/0670_aerocement_triad_v1.py` — SHA-256 `dba758fac4044bd3c716fcb31544abfef66bd49f911e2722e648b0c1d8dfbddf` | Latent-water/generation model | Model |
| TC-DESICCANT | `bin/0672_desiccant_module_v1.py` — SHA-256 `b06510ee884c9c63f00071aa71c1ba0a8868c0869d0e1936db4f6fbc6290d1da` | Desiccant sizing/regeneration model | Model |
| TC-COLD-BATTERY | `bin/0679_thermal_battery_check.py` — SHA-256 `dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf` | Cold-side calculation | Model |
| TC-THERMAL-BATTERY | `bin/0708_thermal_battery_system.py` — SHA-256 `6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa` | Tank/coil/stratification model | Model |
| TC-HIGH-T-STEAM | `bin/thermal_balance_v63.py` — SHA-256 `3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335` | Solar/steam/Stirling branch | High-hazard model branch |

## Admission rule

A theoretical artifact can support a documented model rationale after review of
its author/source, revision, assumptions, units, calculation method, validity
domain, and limitations. It can support a physical-performance claim only when
the claimed configuration has traceable documented testing, conditions,
instruments, raw data, uncertainty, and appropriate review.

## Excluded material

Backup, recovery, archive, duplicate, generated, cache, and quarantine material
may be used to locate source leads. It is not automatically canonical evidence
and cannot independently promote an evidence level.

## Current conclusion

Thermal Cascade has identified canonical architecture and model sources.
This register does not itself establish a measured cooling capacity, heating
capacity, electricity output, efficiency, safety status, construction approval,
certification, field readiness, or deployment result.

--- designs/thermal-cascade/THEORY_AND_EVIDENCE.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Theory and Evidence

## Theory is proof within stated premises

Theoretical mathematical physics is a legitimate form of proof. A correct
derivation proves what follows from its equations, assumptions, boundary
conditions, parameter values, and definitions.

For Thermal Cascade, valid theoretical work can establish energy conservation,
dimensional consistency, heat/mass-transfer relationships, psychrometric bounds,
stack-pressure limits, storage calculations, and thermodynamic limits within
the stated model.

## Identified model artifacts

| Model area | Source | Correct classification |
|---|---|---|
| OpenCell latent heat / water / generation tradeoff | `bin/0670_aerocement_triad_v1.py` — SHA-256 `dba758fac4044bd3c716fcb31544abfef66bd49f911e2722e648b0c1d8dfbddf` | Model with explicit defaults and accounting boundary |
| Desiccant sizing and regeneration | `bin/0672_desiccant_module_v1.py` — SHA-256 `b06510ee884c9c63f00071aa71c1ba0a8868c0869d0e1936db4f6fbc6290d1da` | Model with desiccant-capacity and heat-input assumptions |
| Cold-side thermal value check | `bin/0679_thermal_battery_check.py` — SHA-256 `dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf` | Calculation/model |
| Ferrocement tank, coil, freezing, and stratification | `bin/0708_thermal_battery_system.py` — SHA-256 `6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa` | Model with stated tank, coil, weather, and U-value inputs |
| Solar/steam/Stirling branch | `bin/thermal_balance_v63.py` — SHA-256 `3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335` | Separate high-hazard model branch |
| Architecture and heat-balance rationale | `docs/README.md` — SHA-256 `46dfda5a736b2d63e247374a95794397fe006ee9b9c1480095a0cc960125fa87`; `docs/research/cascade-heatbalance.md` — SHA-256 `db0a8a73651cda954fbc99ee19e08db73462def94ab757f98982dea23f683bb3` | Design architecture and mathematical rationale |

## Proof layers

| Layer | Establishes | Does not establish alone |
|---|---|---|
| Mathematical proof | What follows from explicit premises | That a constructed system satisfies those premises |
| Model or simulation | Predicted behavior inside a stated parameter domain | Correct geometry, material behavior, losses, controls, or field performance |
| Controlled measurement | A documented configuration’s observed behavior | General reliability, replication, certification, or universal suitability |
| Field validation | Behavior across recorded actual-use conditions | Safety certification or performance outside documented conditions |

## Required accounting boundaries

- Latent heat transport is not a second energy source.
- Do not add solar-face input and a latent-transport term as energy created.
- Do not add heat service, cooling service, and shaft/electrical output as one thermodynamic-efficiency numerator.
- Treat open-loop exhaust as a mass and enthalpy outlet.
- Keep direct thermal service, stored energy, and work conversion in distinct accounting columns.
- Keep the high-pressure steam branch separate from the wet-labyrinth system.

## Evidence status

The repository contains specific architecture and model artifacts. This review
does not itself classify every artifact as admitted L1 evidence or identify a
complete L2 physical record. Any public claim must cite the exact source,
revision, configuration, method, units, conditions, and limitation that support it.

The OpenCell absorber document is explicitly a manuscript skeleton whose claims
await experiment: `docs/research/opencell-absorber.md` — SHA-256 `d7c8c426b58e5e6341c1ee01a68090be8bac0bfcd266161b83744ca456204185`.

--- docs/EVIDENCE_LEVELS.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# OpenRoot Evidence Levels

| Level | Meaning |
|---|---|
| L0 | Concept with explicit unknowns and claim boundary |
| L1 | Desk model with assumptions and calculations |
| L2 | Bench prototype with preliminary measurements |
| L3 | Repeated prototype with documented failures and costs |
| L4 | Independent replication |
| L5 | Field-ready reference design with reproducible evidence |

No level is certification, engineering sign-off, legal compliance, or a safety guarantee.

--- docs/OPEN_HARDWARE_STATUS.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# OpenRoot Open Hardware Status

This page provides a conservative public status view of OpenRoot design packets.

The presence of a packet means its documentation is being organized. It does
not mean the system is build-ready, safe, certified, measured, field-tested,
or suitable for any specific use.

## Design packets

| Design | Status | Evidence | Current boundary | Next evidence step |
|---|---|---|---|---|
| OpenRoot Thermal Cascade | Draft | L0 | Concept/intake only; no physical performance, safety, or deployment claim | Define a bounded safe measurement protocol and document real evidence |

## Interpreting status

| Label | Meaning |
|---|---|
| Draft | Documentation is incomplete or under active review |
| L0 | Concept, hypothesis, or intake |
| L1 | Documented source, calculation, simulation, or design rationale |
| L2 | Documented controlled physical measurement |
| L3 | Replicated measurement |
| L4 | Documented field validation |
| L5 | Independent replication or mature validation |

## Publication discipline

OpenRoot publishes useful uncertainty.

A design packet may contain an idea, diagram, calculation, BOM seed, or test
plan long before it contains a validated prototype. Readers should use the
packet's evidence level, result records, hazards, and stated limitations—not a
repository release or CI badge—as the basis for any decision.


```

## BOM and build readiness excerpts

```text
--- designs/thermal-cascade/bom/BOM.csv ---
reference,part_name,description,quantity,unit,specification,material_or_grade,manufacturer_part_number,source_or_make,cost_estimate_usd,currency,alternatives,design_file,criticality,notes
EX-001,Example component,Replace with actual component,1,each,Required dimensions/rating,Material or grade,Part number,Local/source/make,0.00,USD,Document alternatives,designs/drawings/example.svg,required,Document verification requirements

--- designs/thermal-cascade/BOM.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade BOM Seed

## Status

**L0 — concept and intake only.** This is not a procurement list, construction specification, or validated design. No quantities, dimensions, prices, structural loads, temperatures, pressures, electrical ratings, or performance claims are established here.

## Purpose

Capture categories of inputs that must be specified and reviewed before a buildable prototype can be defined.

## Required specification categories

| Category | Required future evidence | Current status |
|---|---|---|
| Thermal source | Source type, temperature range, duty cycle, hazard review | Unknown |
| Heat-transfer path | Working medium, containment, fittings, insulation, interfaces | Unknown |
| Thermal storage | Material, mass, enclosure, compatibility, temperature limits | Unknown |
| Structure/enclosure | Dimensions, loads, mounting, fire and weather exposure | Unknown |
| Instrumentation | Sensor type, calibration, placement, logging method | Unknown |
| Controls and shutdown | Manual control, emergency stop, fault detection | Unknown |
| PPE and safety equipment | Hazard-specific selection and operating procedure | Unknown |

## Procurement boundary

Do not purchase, fabricate, connect, pressurize, energize, heat, or operate a system from this file. A future L1/L2 packet must provide bounded drawings, material specifications, a safety review, and a reviewed test protocol first.

--- designs/thermal-cascade/BUILD.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Build Boundary

## Status

**No build procedure exists at L0.** The current packet does not authorize construction, assembly, heating, electrical work, pressurization, combustion, occupied-structure integration, potable-water use, or field deployment.

## Preconditions for a future build procedure

A build procedure may be drafted only after the packet contains:

1. A defined system boundary and intended test configuration.
2. Drawings or dimensions sufficient for the bounded prototype.
3. A reviewed BOM with material compatibility and substitutions.
4. Identified hazards, operating limits, PPE, and stop conditions.
5. A test protocol with calibrated or characterized instruments.
6. A public-safe review of sources, licensing, privacy, and evidence claims.

## Required future build record

Any future build entry must state:

- Date, builder, revision, and location context
- Materials and dimensions actually used
- Tools and PPE
- Deviations from drawings or procedure
- Inspection and stop points
- Photographs or sketches of the as-built configuration
- Explicit statement of what was not tested

## Stop boundary

Stop work and seek qualified review for structural loads, occupied structures, pressure, steam, high temperature, hazardous electricity, potable water, wastewater, food, combustion, fuels, toxic materials, or other safety-critical work.

--- designs/thermal-cascade/TEST_PLAN.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Test Plan

## Status

**L0 planning only.** This file defines a future test-planning boundary; it does not authorize a physical test.

## Question

What is the smallest safe, bounded measurement that can reduce uncertainty about one defined thermal-transfer or thermal-storage behavior without implying whole-system performance?

## Preconditions

Before any physical test:

- Select one claim with a unit, boundary, and falsifiable result.
- Define a non-safety-critical test article and safe operating range.
- Document hazards, PPE, supervision, shutdown method, and stop conditions.
- Record instrument type, calibration/accuracy, placement, sampling interval, and time base.
- Obtain appropriate review for any condition involving heat, pressure, electricity, fuels, combustion, structures, water quality, or hazardous materials.

## Minimum test record

| Field | Required record |
|---|---|
| Test ID | Unique identifier |
| Revision | Packet/design revision under test |
| Question | One bounded claim |
| Inputs | Values and units |
| Conditions | Ambient conditions, duration, configuration |
| Instruments | Type, range, accuracy/calibration |
| Raw data | Original observations or logs |
| Result | Measured result with units |
| Uncertainty | Known error sources and limitations |
| Deviations | Any departure from the planned method |
| Stop event | Whether a stop condition occurred |

## Non-claims

A simulation, calculation, single observation, or CI pass is not physical validation. Do not infer system efficiency, safety, durability, field readiness, certification, or deployability from an L0/L1 record.

--- designs/thermal-cascade/docs/build-instructions.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Build Instructions

## Prerequisites

- Required tools:
- Required skills:
- Personal protective equipment:
- Required drawing revision:
- Required BOM revision:

## Steps

1. Replace with one observable assembly action.
2. Reference BOM IDs and drawing files.
3. Record required measurements, orientation, spacing, cure time, torque, or calibration.

## Acceptance checks

- [ ] Build matches referenced drawings.
- [ ] Critical component IDs are visible and recorded.
- [ ] Deviations are recorded.

--- designs/thermal-cascade/docs/test-protocol.md ---
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Test Protocol

## Objective

State the exact function or hypothesis being tested.

## Setup

- Design version:
- BOM revision:
- Instruments and calibration:
- Ambient conditions:
- Operator:
- Date:
- Safety controls:

## Procedure

1. Record starting conditions.
2. Apply one defined input.
3. Record measurements with units and timestamps.
4. Record deviations, faults, and unexpected conditions.
5. Stop when a safety threshold is reached.

## Acceptance criteria

State measurable pass/fail criteria or write `not yet established`.

```

## OSHW claim language requiring evidence review

```text
designs/thermal-cascade/MEASUREMENTS.md:9:The packet remains at **L0**. Existing notes, scripts, calculations, archives, simulations, or historical files are not entered as measured physical evidence until they are individually identified, reviewed for provenance, and linked to a documented method and configuration.
designs/thermal-cascade/MEASUREMENTS.md:21:- The tested configuration and revision
designs/thermal-cascade/MEASUREMENTS.md:31:Do not turn archive recovery, simulation output, a design hypothesis, a copied script, or an undocumented historical number into a physical-performance claim.
designs/thermal-cascade/release-manifest.json:2:  "name": "thermal-cascade-docs-v0.3.1",
designs/thermal-cascade/release-manifest.json:4:  "tag": "v0.3.1-thermal-cascade-docs",
designs/thermal-cascade/release-manifest.json:7:    "designs/thermal-cascade/PROVENANCE.md",
designs/thermal-cascade/release-manifest.json:8:    "designs/thermal-cascade/SYSTEM.md",
designs/thermal-cascade/release-manifest.json:9:    "designs/thermal-cascade/THEORY_AND_EVIDENCE.md"
designs/thermal-cascade/release-manifest.json:14:    "measured performance",
designs/thermal-cascade/release-manifest.json:15:    "safety certification",
designs/thermal-cascade/metadata.yaml:5:slug: "thermal-cascade"
designs/thermal-cascade/metadata.yaml:18:  This packet is an early design record. It is not a field-validated
designs/thermal-cascade/metadata.yaml:19:  performance guarantee and is not professional structural, electrical,
designs/thermal-cascade/metadata.yaml:20:  plumbing, pressure-vessel, food-safety, health, legal, or safety guidance.
designs/thermal-cascade/BUILD.md:18:6. A public-safe review of sources, licensing, privacy, and evidence claims.
designs/thermal-cascade/BUILD.md:30:- Explicit statement of what was not tested
designs/thermal-cascade/BUILD.md:34:Stop work and seek qualified review for structural loads, occupied structures, pressure, steam, high temperature, hazardous electricity, potable water, wastewater, food, combustion, fuels, toxic materials, or other safety-critical work.
designs/thermal-cascade/README.md:22:This packet is an early design record. It does not establish a performance guarantee, certification, code compliance, structural approval, electrical approval, pressure-vessel approval, food-safety approval, water-safety approval, or professional safety advice.
designs/thermal-cascade/README.md:27:2. Read `docs/safety.md`.
designs/thermal-cascade/README.md:36:docs/          Purpose, safety, build, test, operation, maintenance
designs/thermal-cascade/router_context.json:5:  "description": "Early design-packet intake for a thermal cascade concept. This context represents an unvalidated hypothesis and documentation workflow only. It does not authorize construction, physical testing, performance claims, safety claims, or evidence-level promotion.",
designs/thermal-cascade/router_context.json:31:  "safety_review_complete": false,
designs/thermal-cascade/router_context.json:36:    "thermal-cascade",
designs/thermal-cascade/SAFETY.md:7:**No safety approval is granted by this packet.** This is an L0 documentation boundary and not professional engineering, electrical, structural, plumbing, pressure-vessel, fire, food-safety, health, legal, or regulatory advice.
designs/thermal-cascade/SAFETY.md:22:## Future safety record requirements
designs/thermal-cascade/SAFETY.md:37:Do not call the Thermal Cascade safe, certified, code-compliant, field-ready, proven, or suitable for any specific use without documented evidence and appropriate review.
designs/thermal-cascade/PROVENANCE.md:9:assumption, simulation, code default, or design statement into a measured
designs/thermal-cascade/PROVENANCE.md:10:physical-performance, safety, certification, build-readiness, or deployment claim.
designs/thermal-cascade/PROVENANCE.md:17:| TC-SYSTEM-ARCH | `designs/thermal-cascade/docs/system-architecture.md` — SHA-256 `2023c352b07f5ecec277266b9bdafe3727e0cdcdcb4f3e3031ded19e3d37bf21` | Packet system-architecture record | Design architecture |
designs/thermal-cascade/PROVENANCE.md:22:| TC-COLD-BATTERY | `bin/0679_thermal_battery_check.py` — SHA-256 `dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf` | Cold-side calculation | Model |
designs/thermal-cascade/PROVENANCE.md:23:| TC-THERMAL-BATTERY | `bin/0708_thermal_battery_system.py` — SHA-256 `6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa` | Tank/coil/stratification model | Model |
designs/thermal-cascade/PROVENANCE.md:24:| TC-HIGH-T-STEAM | `bin/thermal_balance_v63.py` — SHA-256 `3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335` | Solar/steam/Stirling branch | High-hazard model branch |
designs/thermal-cascade/PROVENANCE.md:30:domain, and limitations. It can support a physical-performance claim only when
designs/thermal-cascade/PROVENANCE.md:43:This register does not itself establish a measured cooling capacity, heating
designs/thermal-cascade/PROVENANCE.md:44:capacity, electricity output, efficiency, safety status, construction approval,
designs/thermal-cascade/release/REPRODUCE.md:7:3. Read `STATUS.md` and `docs/safety.md`.
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:22:| Cold-side thermal value check | `bin/0679_thermal_battery_check.py` — SHA-256 `dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf` | Calculation/model |
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:23:| Ferrocement tank, coil, freezing, and stratification | `bin/0708_thermal_battery_system.py` — SHA-256 `6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa` | Model with stated tank, coil, weather, and U-value inputs |
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:24:| Solar/steam/Stirling branch | `bin/thermal_balance_v63.py` — SHA-256 `3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335` | Separate high-hazard model branch |
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:32:| Model or simulation | Predicted behavior inside a stated parameter domain | Correct geometry, material behavior, losses, controls, or field performance |
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:34:| Field validation | Behavior across recorded actual-use conditions | Safety certification or performance outside documented conditions |
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:40:- Do not add heat service, cooling service, and shaft/electrical output as one thermodynamic-efficiency numerator.
designs/thermal-cascade/THEORY_AND_EVIDENCE.md:42:- Keep direct thermal service, stored energy, and work conversion in distinct accounting columns.
designs/thermal-cascade/INTAKE.md:36:- Useful thermal service:
designs/thermal-cascade/INTAKE.md:45:| Artifact | Existing file / note / photo | Revision/date | What it proves | Public-safe? |
designs/thermal-cascade/docs/safety.md:9:Stop work and seek qualified review for structural loads, occupied structures, pressurized systems, steam, high temperature, hazardous electricity, potable water, wastewater, food, combustion, fuels, toxic materials, or other safety-critical work.
designs/thermal-cascade/docs/safety.md:11:Do not call this design safe, certified, compliant, field-ready, or proven without documented evidence and appropriate review.
designs/thermal-cascade/docs/test-protocol.md:7:State the exact function or hypothesis being tested.
designs/thermal-cascade/docs/test-protocol.md:25:5. Stop when a safety threshold is reached.
designs/thermal-cascade/docs/operation.md:11:1. Replace with safe, observable operating steps.
designs/thermal-cascade/docs/operation.md:17:Describe a safe normal shutdown and an emergency stop procedure.
designs/thermal-cascade/BOM.md:7:**L0 — concept and intake only.** This is not a procurement list, construction specification, or validated design. No quantities, dimensions, prices, structural loads, temperatures, pressures, electrical ratings, or performance claims are established here.
designs/thermal-cascade/BOM.md:23:| PPE and safety equipment | Hazard-specific selection and operating procedure | Unknown |
designs/thermal-cascade/BOM.md:27:Do not purchase, fabricate, connect, pressurize, energize, heat, or operate a system from this file. A future L1/L2 packet must provide bounded drawings, material specifications, a safety review, and a reviewed test protocol first.
designs/thermal-cascade/STATUS.md:24:- No field-performance guarantee.
designs/thermal-cascade/SYSTEM.md:9:It does not claim a completed, measured, safe, certified, build-ready, or
designs/thermal-cascade/SYSTEM.md:10:field-validated installation.
designs/thermal-cascade/SYSTEM.md:14:Thermal Cascade is an open-loop, multi-organ thermal system built around
designs/thermal-cascade/SYSTEM.md:25:→ controlled thermal-exchange branch
designs/thermal-cascade/SYSTEM.md:28:  ├─ direct thermal-use load
designs/thermal-cascade/SYSTEM.md:49:not evidence that every source operates in one validated installation.
designs/thermal-cascade/SYSTEM.md:70:where electricity is actually required. Direct thermal use remains distinct from
designs/thermal-cascade/SYSTEM.md:78:- **Hot Tank A** and **Cold Tank B** are separate thermal reservoirs.
designs/thermal-cascade/SYSTEM.md:90:- cooling service, thermal storage capacity, work output, and efficiency.
designs/thermal-cascade/SYSTEM.md:95:- `designs/thermal-cascade/docs/system-architecture.md` — SHA-256 `2023c352b07f5ecec277266b9bdafe3727e0cdcdcb4f3e3031ded19e3d37bf21`
designs/thermal-cascade/TEST_PLAN.md:11:What is the smallest safe, bounded measurement that can reduce uncertainty about one defined thermal-transfer or thermal-storage behavior without implying whole-system performance?
designs/thermal-cascade/TEST_PLAN.md:18:- Define a non-safety-critical test article and safe operating range.
designs/thermal-cascade/TEST_PLAN.md:41:A simulation, calculation, single observation, or CI pass is not physical validation. Do not infer system efficiency, safety, durability, field readiness, certification, or deployability from an L0/L1 record.
docs/SUPERLOOP.md:14:It improves recall, repeatability, and error recovery. It does not replace human responsibility for structural, electrical, thermal, water, food, safety, security, licensing, publishing, or deployment decisions.
docs/SUPERLOOP.md:20:- JSON / JSONL: portable derived records and validated policy configuration
docs/SUPERLOOP.md:45:- Treat model output as verified engineering, medical, legal, safety, or security guidance
docs/SUPERLOOP.md:62:- Catch and store energy: cache known-good routes and verified solutions
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md:2:## How open, decentralized, joule-verified contribution solves engineered problems that centralized systems profit from leaving unsolved
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md:19:built what, when, to what measured effect. When a build's value is verifiable
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md:82:- Vacuum chamber core (black-painted for thermal absorption)
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md:157:minted **only** against verified physical work (PoPW) — fuel mass burned,
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md:162:efficiency — is structurally forbidden, not merely discouraged.
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md:171:| AeroCement H-003 | Solar-thermal cascade | 12.91 kWh/m² nightly (sim) | Sim validated |
docs/markdown/PYTHON_FILES.md:13:| `efficiency_coefficient.py` | `bin/` | Energy ETA calculator |
docs/README.md:13:| AeroCement | Open-cell cement volumetric exchangers — thermal mass that breathes | `aerocement/` |
docs/README.md:18:| UNE / PoPW | Computational flow and verified-work ledger | `computational_flow/`, `PoPW ledger` |
docs/README.md:44:η = useful_joules / human_joules. Heat-engine η, actuator η, EROI, and simulation scores are four different quantities (N14). **We never claim greater than 100% thermodynamic efficiency.** Where the system delivers more than the sunlight that strikes the collector, it is because it also moves environmental heat — the same accounting a ground-source heat pump uses, and we state the boundary openly.
docs/README.md:48:Claims are minted only for verified physical work. No pre-mine, no speculation. Each hypothesis carries its falsifier:
docs/README.md:53:| H2 | Spherical voids beat mined lightweight aggregate on strength-to-weight | measured specific strength below LWAC control |
docs/README.md:81:**Updates are advancements.** The repo is the growing web: each verified file, mix, ledger line, and skill is a node. No patents. Ever.
docs/README.md:85:We never claim greater than 100% thermodynamic efficiency.
docs/README.md:99:3. **PoPW / ACRE** — claims minted only for verified physical work. No pre-mine. No speculation.
docs/README.md:164:Do not print 1.34 as thermodynamic efficiency (N14). Do not add latent 314 W into the 4.84 MJ pile. 2°C / 35°F air is a target, not this table. Steam / RMH boiler is a separate organ and a separate book.
docs/README.md:183:That single material change turns a failed insulation foam into high-S/V thermal mass and structure.
docs/README.md:185:### Design-range material table (unmeasured ranges stay ranges)
docs/README.md:202:Gel, per \~1 L batch (volume, not a certified mix):
docs/README.md:208:activated carbon / charcoal in the paste for α · AR glass fiber ≥20% Zr, 2–5% by volume · rotor-stator if you are chasing finer cells · optional sand later (NightHawkInLight has tested sand:cement up to 2:1 by volume; that is his update, not a hang here).
docs/README.md:221:Same open-cell matrix, three jobs. Passive after construction. No grid fans. No pumps on the thermal loop.
docs/README.md:271:**Do not add heat + cooling + shaft work and call it 2197 W or “220% efficiency.”**
docs/README.md:272:Moving 854 W of heat into ground mass is one physical stream. Calling that same stream “heating service” in winter and “cooling service” in summer is a **service count**. Service count is allowed in a grant packet if labeled as service. It is forbidden as thermodynamic efficiency (N14).
docs/README.md:278:- Friction at 0.1 W is a placeholder, not a measured duct loss.
docs/README.md:280:**Passive transport ratio** (heat moved / electrical watts on the loop) can be large because electrical watts on the loop are designed to be near zero. That ratio is **not** a heat-engine efficiency and must not be written as COP = 21,972 in a sentence that a reviewer will read as perpetual motion.
docs/README.md:325:Not a thermal claim. Separate hangs.
docs/README.md:343:| H2 | Spherical voids beat mined lightweight aggregate on strength-to-weight at equal or lower cement | measured specific strength below LWAC control |
docs/README.md:348:| H-003 | Instrumented solar + labyrinth node in Sikeston climate matches the 931 W/m² class closely enough to beat a measured electrical baseline on η_act | pad sensors show otherwise |
docs/README.md:354:**H5 numbers in old drafts (180–300 kW, 1500 kW radiator exchange) are upper-bound arithmetic, not a vehicle.** Do not reprint them as performance.
docs/README.md:362:- Benefit measured at the recipient.
docs/README.md:372:Work is measured in joules. Verified physical work mints ACRE claims. Two independent validators. Replicating a known node in an already-validated climate earns 0 new knowledge mint.
docs/README.md:374:Building the first node in a new climate zone, fixing a documented flaw, shipping a new tool, or writing a new skill doc is mintable. Copying node #47 in a climate already validated is real work and zero new-knowledge mint.
docs/README.md:404:1. Never claim greater than 100% thermodynamic efficiency.
docs/README.md:411:8. Service-count ≠ First Law. Do not sum heat+cold+work against one watt of sun and call it efficiency.
docs/README.md:504:| [AeroCement](../aerocement) | Triple-utility solar-thermal concrete panels |
docs/README.md:505:| [OpenRoot](../openroot) | Ferrocement domes + thermal labyrinths |
docs/README.md:517:it does not prove physical performance, safety, field readiness, certification,
docs/RELEASE_PROCESS.md:11:A release is not proof that an associated physical system is validated,
docs/RELEASE_PROCESS.md:12:safe, certified, deployable, or appropriate for every environment.
docs/RELEASE_PROCESS.md:23:- Public performance, safety, or readiness claims
docs/RELEASE_PROCESS.md:53:a narrowly selected, redacted, reproducible artifact:
docs/RELEASE_PROCESS.md:78:It must not represent an L0/L1 packet as physically validated.
docs/RELEASE_PROCESS.md:80:| Evidence level | Release-safe statement |
docs/PERMACULTURE_ROUTER.md:18:- detect hard safety and evidence gates
docs/PERMACULTURE_ROUTER.md:27:- make safety claims
docs/PERMACULTURE_ROUTER.md:37:→ activate routes → recommend smallest safe reversible step
docs/PERMACULTURE_ROUTER.md:49:| L0 | Concept, hypothesis, or unverified idea |
docs/PERMACULTURE_ROUTER.md:57:system performance, safety, regulatory compliance, or field readiness.
docs/PERMACULTURE_ROUTER.md:78:  data/router_examples/thermal-cascade-l0.json \
docs/PERMACULTURE_ROUTER.md:79:  --output .ci/permaculture/thermal-cascade.report.json
docs/PERMACULTURE_ROUTER.md:86:  .ci/permaculture/thermal-cascade.report.json
docs/PERMACULTURE_ROUTER.md:135:- safety
docs/OPEN_INVITATION.md:7:2. **Grading**: measured data > bench test > reasoned hypothesis. No hype, no >100% thermo.
docs/OPEN_INVITATION.md:9:4. **Non-recompute**: verified solutions are SHA-256 paired with their mistakes — your win compounds for everyone after you.
docs/README.draft.md:3:**A self-sustaining network leveraging physical infrastructure and computational swarm to maximize thermal, material, and food yield while minimizing waste.**
docs/README.draft.md:6:> Every cycle must close on real thermal, material, or food yield.
docs/README.draft.md:13:[![Thermal Ledger](https://img.shields.io/badge/Thermal%20Ledger-12.91%20kWh/m²%2Fnight-blue?style=flat-square&logo=thermal)]  
docs/README.draft.md:45:OpenRoot leverages the `lb_loop` 21-cached-passes proof to ensure that each computational cycle is optimized for energy efficiency and minimal waste. This proof is a key component of our thermodynamic ledger, which tracks every joule of useful work performed by the network.
docs/README.draft.md:54:| **Energy** | Passive solar-thermal, storage | Black Locust coppice + RMH, H-003 thermal cascade |
docs/README.draft.md:87:- **Subterranean thermal storage** — 35°F cooling from 120°F inlet
docs/README.draft.md:88:- **Target:** 12.91 kWh/m² nightly capture (validated simulation)
docs/README.draft.md:93:- **85-95% combustion efficiency** vs 50-70% conventional stoves
docs/README.draft.md:94:- **12-24 hour thermal mass storage** — one burn cycle heats a day
docs/OPEN_HARDWARE_STATUS.md:8:not mean the system is build-ready, safe, certified, measured, field-tested,
docs/OPEN_HARDWARE_STATUS.md:15:| OpenRoot Thermal Cascade | Draft | L0 | Concept/intake only; no physical performance, safety, or deployment claim | Define a bounded safe measurement protocol and document real evidence |
docs/OPEN_HARDWARE_STATUS.md:34:plan long before it contains a validated prototype. Readers should use the
docs/UNIFIED_ARCHITECTURE.md:16:| black-locust-rmh    | Living systems           | Black Locust permaculture + thermal cascade   |
docs/PROJECT_ROADMAP.md:7:performance claims.
docs/PROJECT_ROADMAP.md:22:- Public-safe/redaction review
docs/PROJECT_ROADMAP.md:27:- No unverified performance claim is presented as a measured result.
docs/PROJECT_ROADMAP.md:34:and excluded claims without representing the design as physically validated.
docs/PROJECT_ROADMAP.md:54:Run one bounded, appropriately safe, documented test that reduces a high-value
docs/PROJECT_ROADMAP.md:90:- A defined prototype configuration is reproducible.
docs/PROJECT_ROADMAP.md:91:- Dependencies, tools, materials, and safety limits are explicit.
docs/PROJECT_ROADMAP.md:92:- The packet remains honest about untested areas.
docs/DESIGN_PACKETS.md:5:A design packet is the durable public format for an OpenRoot idea, invention, experiment, BOM, blueprint, or reproducible system.
docs/DESIGN_PACKETS.md:10:./scripts/new_design_packet.sh thermal-cascade "OpenRoot Thermal Cascade" "Jesse Ray McMillen"
docs/DESIGN_PACKETS.md:13:A local note, superloop record, AI draft, or raw experiment is not automatically public knowledge. Promote it only after review for correctness, licensing, privacy, safety, and reproducibility.
docs/REPOSITORIES.md:9:- **Active hardware repositories** hold concrete materials, thermal, shelter, and energy systems.
docs/REPOSITORIES.md:28:| [black-locust-rmh](https://github.com/jesseray718/black-locust-rmh) | Black Locust rocket-mass-heater thermal cascade | Active OSHW candidate; require safety, build, and measured-performance documentation |
docs/REPOSITORIES.md:29:| [OpenCell-Thermal-System](https://github.com/jesseray718/OpenCell-Thermal-System) | OpenCell concrete thermal system | Active OSHW candidate; needs a precise public build/evidence boundary |
docs/REPOSITORIES.md:44:| [openroot-thesis](https://github.com/jesseray718/openroot-thesis) | Thesis/reference material | Context and theory, not a substitute for measured design evidence |
docs/REPOSITORIES.md:85:2. **Buildable** — BOM, drawings or dimensions, procedure, safety constraints, and verification step exist.
docs/REPOSITORIES.md:86:3. **Experimental** — plausible but unverified; explicitly labeled.
docs/SCOPE.md:8:- Passive energy: aerocement absorbers, thermal labyrinths, low-delta-T Stirling
docs/SCOPE.md:19:Every published number is either (a) measured with instrument + uncertainty stated, or (b) marked hypothesis. Current known-degenerate: agape_cascade v1.x (floor cap 100x100 < SOL 300x100 — tier structure never activates). Fix precedes any v2 claim.
docs/LESSON_RECORD_SCHEMA.md:9:- status: draft | verified | superseded  (graduation to verified is human-gated)
docs/LESSON_RECORD_SCHEMA.md:16:- safety_notes: conditions and boundaries
docs/EVIDENCE_LEVELS.md:12:| L5 | Field-ready reference design with reproducible evidence |
docs/EVIDENCE_LEVELS.md:14:No level is certification, engineering sign-off, legal compliance, or a safety guarantee.
README.md:17:- What was tested.
README.md:31:- Reproducible experiments and measured results.
README.md:41:A central example is the **Thermal Cascade**: an appropriate-technology system intended to improve how thermal energy is captured, transferred, stored, and used.
README.md:53:The goal is not to make claims that cannot be tested. The goal is to preserve the chain from idea to design, design to experiment, experiment to evidence, and evidence to real-world implementation.
README.md:72:Versioned evidence and reproducible records
README.md:90:The automation serves the work. It does not replace human responsibility for evidence, safety, implementation, or governance.
README.md:108:Automation may assist with searching, drafting, analysis, routing, and verification. Humans retain authority over safety-critical decisions, physical implementation, publishing, spending, remote access, and irreversible changes.
README.md:130:Current work includes local coordination tools, shared context, reproducible records, AI-assisted research workflows, ledger reconciliation, and documentation for appropriate-technology systems. The project is still evolving, and published material should be read as an open working system rather than finished engineering certification.
README.md:140:  the reproducible baseline for open-hardware projects.
README.md:154:- Scientific literature review and reproducible experiments.
README.md:176:it does not prove physical performance, safety, field readiness, certification,
```

## Current OSHW GitHub repository metadata

```text
--- jesseray718/openroot ---
{"defaultBranchRef":{"name":"main"},"description":"Off-grid passive solar + opencell concrete thermal systems — open hardware, permaculture computation, PoPW-verified","isArchived":false,"isPrivate":false,"licenseInfo":{"key":"gpl-3.0","name":"GNU General Public License v3.0","nickname":"GNU GPLv3"},"nameWithOwner":"jesseray718/openroot","pushedAt":"2026-09-28T04:58:35Z","repositoryTopics":[{"name":"appropriate-technology"},{"name":"open-hardware"},{"name":"permaculture"},{"name":"ferrocement"},{"name":"passive-solar"},{"name":"proof-of-physical-work"},{"name":"carbon-negative"},{"name":"energy-sovereignty"},{"name":"local-llm"},{"name":"mesh-network"},{"name":"offline-first"},{"name":"ollama"},{"name":"python"},{"name":"rag"},{"name":"stirling-engine"},{"name":"syncthing"},{"name":"termux"},{"name":"thermal-storage"},{"name":"off-grid-energy"},{"name":"opencell-cement"}],"url":"https://github.com/jesseray718/openroot","visibility":"PUBLIC"}

--- jesseray718/openroot-design-packet-template ---
{"defaultBranchRef":{"name":"main"},"description":"OpenRoot template for reproducible open-hardware and appropriate-technology design packets","isArchived":false,"isPrivate":false,"licenseInfo":{"key":"gpl-3.0","name":"GNU General Public License v3.0","nickname":"GNU GPLv3"},"nameWithOwner":"jesseray718/openroot-design-packet-template","pushedAt":"2026-09-26T23:29:34Z","repositoryTopics":null,"url":"https://github.com/jesseray718/openroot-design-packet-template","visibility":"PUBLIC"}

--- jesseray718/OpenCell-Thermal-System ---
{"defaultBranchRef":{"name":"main"},"description":"[SPOKE of openroot-canon] canonical: https://github.com/jesseray718/openroot-canon","isArchived":false,"isPrivate":false,"licenseInfo":{"key":"other","name":"Other","nickname":""},"nameWithOwner":"jesseray718/OpenCell-Thermal-System","pushedAt":"2026-09-25T23:03:42Z","repositoryTopics":null,"url":"https://github.com/jesseray718/OpenCell-Thermal-System","visibility":"PUBLIC"}

--- jesseray718/aerocement-panel-v0 ---
{"defaultBranchRef":{"name":"main"},"description":"OpenCell aerocement panel v0 — open-source hardware prototype (OpenRoot)","isArchived":false,"isPrivate":false,"licenseInfo":{"key":"gpl-3.0","name":"GNU General Public License v3.0","nickname":"GNU GPLv3"},"nameWithOwner":"jesseray718/aerocement-panel-v0","pushedAt":"2026-09-27T19:58:18Z","repositoryTopics":null,"url":"https://github.com/jesseray718/aerocement-panel-v0","visibility":"PUBLIC"}

--- jesseray718/black-locust-rmh ---
{"defaultBranchRef":{"name":"main"},"description":"Black Locust Rocket Mass Heater (DV.GEN.BL.RMH.001) — carbon-negative thermal cascade for OpenRoot H-003 + AE-GFRC domes","isArchived":false,"isPrivate":false,"licenseInfo":{"key":"other","name":"Other","nickname":""},"nameWithOwner":"jesseray718/black-locust-rmh","pushedAt":"2026-09-25T22:24:04Z","repositoryTopics":[{"name":"appropriate-technology"},{"name":"carbon-negative"},{"name":"openroot"},{"name":"rmh"},{"name":"rocket-mass-heater"},{"name":"thermal"},{"name":"black-locust"}],"url":"https://github.com/jesseray718/black-locust-rmh","visibility":"PUBLIC"}

--- jesseray718/AeroCement_Ecosystem ---
{"defaultBranchRef":{"name":"main"},"description":"[ARCHIVED] merged into github.com/jesseray718/openroot","isArchived":false,"isPrivate":false,"licenseInfo":{"key":"other","name":"Other","nickname":""},"nameWithOwner":"jesseray718/AeroCement_Ecosystem","pushedAt":"2026-09-25T22:24:14Z","repositoryTopics":null,"url":"https://github.com/jesseray718/AeroCement_Ecosystem","visibility":"PUBLIC"}

```
