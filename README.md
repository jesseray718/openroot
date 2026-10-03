# OpenRoot


## Public Project Map

OpenRoot is a curated public systems-design and open-hardware repository.
It publishes reviewed documentation, evidence standards, schemas, design
packets, examples, and selected reusable tools.

- Start with the [public documentation map](docs/PUBLIC_MAP.md).
- Read the [public boundary](docs/PUBLIC_BOUNDARY.md) before using or
  contributing material.
- Physical work is released as a documented design packet, beginning with
  the [Thermal Cascade packet](designs/thermal-cascade/README.md).
- Review the [claim-status standard](docs/CLAIM_STATUS.md) before treating
  a project statement as established.
- Use the [hardware release standard](docs/HARDWARE_RELEASE_STANDARD.md)
  for physical designs and experimental prototypes.

**OpenRoot is an open-source technology commons for designing, testing,
documenting, and improving practical systems that strengthen local capability.**

OpenRoot connects open hardware, engineering research, technical literature,
experimental records, repair knowledge, and reproducible workflows. It helps
people inspect, adapt, maintain, and improve useful infrastructure through
evidence-preserving, local-first coordination.

The work includes thermal energy, communications, fabrication, repair, shared
tools, resource-aware documentation, and practical infrastructure. Local-first
software, search, and automation support this work; they are not the project’s
primary purpose.

OpenRoot is a public hub—not a claim that every idea here is finished, measured,
safe, build-ready, affordable, certified, lawful in every jurisdiction, or ready
for deployment. Each project should state what is known, what is assumed, what
remains experimental, and what evidence would change its status.

## Mission

Important practical knowledge is often fragmented across notes, prototypes,
local machines, conversations, abandoned repositories, closed platforms, and
undocumented work. Even when a design is public, it can be difficult to
determine:

- What the design actually does.
- What evidence supports a claim.
- What assumptions, costs, hazards, and limits apply.
- Whether another person can reproduce, repair, test, or improve it.
- What materials, labor, energy, maintenance, and governance it requires.
- How the work connects to related systems and contributors.

OpenRoot exists to make that chain clearer:

```text
need → research → design → experiment → evidence → revision → practical implementation
```

The project explores whether open designs, shared technical knowledge, repairable
systems, and local stewardship can strengthen community capability. It does not
promise self-sufficiency, savings, safety, performance, or replacement of
existing institutions. Those outcomes must be demonstrated by documented
evidence for each specific system.

## Evidence workflow

```text
capture -> SHA-256 inventory -> report-only dedupe
        -> local SQLite FTS5 + semantic retrieval
        -> bounded routing -> validation
        -> Newton Chain receipt -> human-reviewed GitHub promotion
```

Automation can inspect, propose, and validate bounded work. Human review
controls commits, pushes, public publication, physical implementation, and
other consequential actions.

## Public repository boundary

This repository contains reusable source code, tests, schemas, documentation,
and redacted examples. It intentionally excludes personal documents, live
SQLite databases, model files, embeddings, archives, logs, device exports,
credentials, and machine-specific runtime state.

## Appropriate technology

OpenRoot is intended to support:

- Open-hardware designs, design packets, and build documentation.
- Thermal, solar, storage, heat-transfer, and energy-use research.
- Resilient communications and local coordination tools.
- Engineering notes, technical references, and reproducible experiments.
- Evidence trails for assumptions, measurements, revisions, failures, hazards,
  and limits.
- Workflows for fabrication, testing, repair, maintenance, preservation, and
  adaptation.
- Shared tools, workshops, repair-oriented systems, and community-scale
  practical infrastructure.
- Lifecycle-cost, material, maintenance, and useful-output documentation.
- Open collaboration around practical, repairable, locally adaptable technology.

These areas describe the project’s scope, not a claim that every design is
complete, validated, safe, build-ready, economical, lawful in every
jurisdiction, or ready for field deployment.

## Thermal Cascade

A central OpenRoot research area is the **Thermal Cascade**: a family of
appropriate-technology concepts for capturing, transferring, storing, and using
thermal energy.

The current public Thermal Cascade packet is at **L0: concept and intake**.
It does not establish physical performance, safety, certification, code
compliance, cost savings, durability, field readiness, or suitability for any
specific use.

Current work may include design rationale, system architecture, thermal models
and assumptions, materials and constraints, measurement plans, test methods,
failures, revisions, literature references, and maintenance knowledge.

The research hypothesis is that carefully documented thermal collection,
storage, and heat-transfer systems may provide useful bounded stationary
services, such as heating, drying, or thermal buffering. Any claim about
electricity generation, cooling performance, mechanical work, mobility, cost,
emissions, safety, durability, or deployment requires direct evidence from a
specific documented design and test condition.

See the [Thermal Cascade design packet](designs/thermal-cascade/README.md),
[status](designs/thermal-cascade/STATUS.md),
[safety boundary](designs/thermal-cascade/SAFETY.md), and
[theory and evidence](designs/thermal-cascade/THEORY_AND_EVIDENCE.md).


## Evidence before assertion

OpenRoot uses evidence levels to distinguish between an idea, a documented
prototype, a repeated measurement, and a reproducible reference design.

| Level | Meaning |
|---|---|
| L0 | Concept, intake, literature, or hypothesis |
| L1 | Documented bench concept or procedure |
| L2 | Bench prototype with preliminary measurements |
| L3 | Repeated prototype with documented failures and costs |
| L4 | Independently reproduced result |
| L5 | Field-ready reference design with reproducible evidence |

An evidence level is not certification, engineering sign-off, legal compliance,
or a safety guarantee. Public claims remain bounded by the evidence, methods,
inputs, dates, uncertainty, and stated limitations available for review.

See [Evidence levels](docs/EVIDENCE_LEVELS.md), [Design packets](docs/DESIGN_PACKETS.md),
and [Open hardware status](docs/OPEN_HARDWARE_STATUS.md).


## Newton chains

OpenRoot develops **Newton chains**: reusable, inspectable reasoning paths from
definitions and assumptions through evidence and inference to bounded
conclusions. They are designed so people and future AI collaborators can
propose, inspect, challenge, reuse, and extend work without requiring hidden
context.

A conclusion in a Newton chain is conditional: it records what follows under
its stated definitions, assumptions, evidence inputs, and inference rules. When
declared dependencies remain unchanged, a verified pathway can be reused. When
a dependency changes, related conclusions can be revisited while their history
remains available.

See the [Newton Chain contract](docs/NEWTON_CHAIN.md) and
[Newton Chain foundations](docs/newton_chain/README.md).


## Project maps

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Routing contract](docs/ROUTING.md)
- [Newton Chain contract](docs/NEWTON_CHAIN.md)
- [Newton Chain foundations](docs/newton_chain/README.md)
- [Newton Chain elements](docs/newton_chain/ELEMENTS.md)
- [Newton Chain schema](docs/newton_chain/SCHEMA.yaml)
- [Newton Chain inference rules](docs/newton_chain/INFERENCE_RULES.md)
- [Newton Chain thermal example](docs/newton_chain/EXAMPLES/thermal_energy_bound.yaml)
- [Security policy](SECURITY.md)

## Contributing

Contributions are welcome in open hardware, documentation, software,
measurements, literature review, local-first tooling, repairable systems, and
reproducible experiments.

Useful contributions are specific, sourced, testable where possible, and
explicit about uncertainty. Please do not present an idea, simulation, or draft
as a measured result.

Start with [Contributing](CONTRIBUTING.md), then review the relevant design
packet, evidence level, and issue or milestone.

## Licensing

- Code and software: GPL-3.0-only unless a file states otherwise.
- Documentation and design material: CC BY-SA 4.0 unless a file states otherwise.

See [LICENSE](LICENSE) and applicable file headers.
