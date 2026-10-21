# OpenRoot Repository Map

OpenRoot is the public hub for an open-source appropriate-technology ecosystem: independently buildable physical systems, local-first software, evidence-preserving documentation, and practical field learning.

## Start Here

- **OpenRoot** is the ecosystem map, evidence standard, and integration hub.
- **Design-packet template** defines how an open-hardware project becomes buildable and reviewable.
- **Active hardware repositories** hold concrete materials, thermal, shelter, and energy systems.
- **Active software repositories** hold calculators, protocols, local tools, and coordination components.
- **Experimental, archived, and external-fork repositories** are preserved references, not equivalent production projects.

## Public Hub

| Repository | Role | Current purpose |
|---|---|---|
| [openroot](https://github.com/jesseray718/openroot) | Hub | Ecosystem map, evidence model, design-packet standards, local-first coordination tools |
| [jesseray718](https://github.com/jesseray718/jesseray718) | Profile | Human-readable entry point to active OpenRoot work |
| [.github](https://github.com/jesseray718/.github) | Shared standards | Shared issue templates, contribution guidance, and reusable workflows |
| [openroot-design-packet-template](https://github.com/jesseray718/openroot-design-packet-template) | OSHW template | Reproducible design-packet baseline for physical systems |
| [openroot-spoke-template](https://github.com/jesseray718/openroot-spoke-template) | Repository template | Baseline for a focused OpenRoot component repository |

## Active Open Hardware

| Repository | System | Maturity statement |
|---|---|---|
| [aerocement](https://github.com/jesseray718/aerocement) | Lightweight foamed-concrete / AR-GFRC construction research | Active OSHW candidate; claims must remain tied to documented methods and measurements |
| [black-locust-rmh](https://github.com/jesseray718/black-locust-rmh) | Black Locust rocket-mass-heater thermal cascade | Active OSHW candidate; require safety, build, and measured-performance documentation |
| [OpenCell-Thermal-System](https://github.com/jesseray718/OpenCell-Thermal-System) | OpenCell concrete thermal system | Active OSHW candidate; needs a precise public build/evidence boundary |

## Active Open Software

| Repository | Capability | Maturity statement |
|---|---|---|
| [aerocement-calc](https://github.com/jesseray718/aerocement-calc) | Material and construction calculations | Active OSS candidate |
| [und-protocol](https://github.com/jesseray718/und-protocol) | Universal Native Descriptor / offline edge computation protocol | Active OSS candidate |
| [une](https://github.com/jesseray718/une) | Universal Native Economy / energy and coordination concepts | Active OSS candidate; experimental claims require explicit status and testable interfaces |

## Governance and Reference

| Repository | Role | Public boundary |
|---|---|---|
| [openroot-canon](https://github.com/jesseray718/openroot-canon) | Governance/reference material | Reference only unless a specific current standard is linked from OpenRoot |
| [openroot-thesis](https://github.com/jesseray718/openroot-thesis) | Thesis/reference material | Context and theory, not a substitute for measured design evidence |

## Classification Queue

The following repositories need a deliberate one-by-one decision: retain as an active component, merge into a focused repository, reframe as reference, or archive with a redirect notice.

- agape-coordination
- agape-crossover-key
- agape-ipfs
- agape-primitives
- agape-une
- agapenet
- agaperesonance
- canonical
- fractallattice
- openroot-ecosystem
- openroot-foundation
- openroot-product
- oscillation-mesh
- renaissance-protocol
- wisdom-scaffold
- axiom-library
- etaledger

## External Forks

External forks are retained for upstream reference and experimentation. They are not OpenRoot-owned product repositories and should not be treated as official OpenRoot releases:

- firmware
- MeshCore
- tinyGS
- LXMF
- RNode_Firmware
- markor
- Reticulum

## Evidence Rules

A public project must distinguish:

1. **Measured** — linked method, inputs, dates, evidence, uncertainty, and results.
2. **Buildable** — BOM, drawings or dimensions, procedure, safety constraints, and verification step exist.
3. **Experimental** — plausible but unverified; explicitly labeled.
4. **Reference** — retained context or theory; not a current implementation claim.

No repository is promoted to a release solely because code, notes, or a concept exists.
