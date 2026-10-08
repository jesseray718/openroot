<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# OpenRoot Open Hardware Preview

## Scope

This is a read-only readiness preview. It does not establish physical performance, safety, build readiness, or release approval.

## Repository

- Generated: 2026-09-26T06:10:40+00:00
- Branch: `main`
- HEAD: `4fa0bc64`
- Origin: `git@github.com:jesseray718/openroot.git`

## Design packet overview

| Packet | Evidence | Documentation | Build | Evidence | Release | Router |
|---|---|---:|---:|---:|---:|---|
| `thermal-cascade` | L0 | 49 | 70 | 30 | 100 | configured |

## thermal-cascade

- Packet path: `designs/thermal-cascade`
- Evidence level: `L0`
- Router configured: `True`
- Router context kind: `intake`
- Metadata observed:
  - `claim_boundary`: `>-`
  - `code`: `GPL-3.0-or-later`
  - `design_id`: `THERMAL_CASCADE`
  - `documentation`: `CC-BY-SA-4.0`
  - `evidence_level`: `L0`
  - `hardware`: `CERN-OHL-S-2.0`
  - `last_reviewed`: `2026-09-25`
  - `licenses`: ``
  - `maintainer`: `Jesse Ray McMillen`
  - `name`: `OpenRoot Thermal Cascade`
  - `schema_version`: `1.0`
  - `slug`: `thermal-cascade`
  - `status`: `draft`
  - `version`: `0.1.0`

### Artifact inventory

- design definition: `INTAKE.md`, `README.md`, `metadata.yaml`
- status and governance: `LICENSE.md`, `STATUS.md`, `docs/safety.md`
- design files: _none found_
- build information: `bom/BOM.csv`, `bom/BOM.md`, `docs/build-instructions.md`
- test and evidence: `docs/results.md`, `docs/test-protocol.md`

### Review gates

- Evidence remains conceptual/documentary. Do not represent this packet as a validated physical system.

### Upgrade path

- Create a bounded non-pressurized or otherwise appropriately safe test protocol with conditions, instruments, stop conditions, raw-data location, and caveats.
- Add versioned design artifacts: system sketch, CAD/drawing, schematic, simulation, or reproducible calculation.

## Release policy

A design-packet release may publish documentation and clearly bounded evidence. It must not claim physical validation beyond the packet's documented evidence level.

Use pre-1.0 tags for evolving frameworks and experimental packets. Semantic Versioning defines a minor version as backward-compatible added functionality and a patch as a backward-compatible fix; stable major releases should wait for an interface and evidence boundary that users can actually rely on.

## Autonomous operation boundary

The router and CI may observe, validate, score, generate reports, and propose. A human must approve physical actions, evidence-level changes, Git commits, pushes, releases, milestone changes, and public claims.
