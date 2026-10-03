# OpenRoot

**OpenRoot is an open-source technology commons for designing, testing,
documenting, and improving practical systems that strengthen local capability.**

OpenRoot connects open hardware, engineering research, technical literature,
experimental records, repair knowledge, and reproducible workflows. Its purpose
is to help people inspect, adapt, maintain, and improve useful infrastructure
rather than depend entirely on opaque or distant systems.

The work focuses on practical areas such as thermal energy, communications,
fabrication, repair, food and material resilience, shared tools, and
evidence-preserving technical knowledge. Local-first software, search, and
automation support this work; they are not the project’s primary purpose.

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

## What OpenRoot supports

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

The goal is not to make claims that cannot be tested. The goal is to preserve
the chain from idea to design, design to experiment, experiment to evidence,
and evidence to practical implementation.

See the [Thermal Cascade design packet](designs/thermal-cascade/README.md),
[status](designs/thermal-cascade/STATUS.md),
[safety boundary](designs/thermal-cascade/SAFETY.md), and
[theory and evidence](designs/thermal-cascade/THEORY_AND_EVIDENCE.md).

## Verifiable knowledge workflows

OpenRoot uses versioned files, hashes, structured records, Git history, and local data stores to make technical work inspectable.

```text
Question or need
        │
        ▼
Research, design, and literature review
        │
        ▼
Open hardware / workflow / experiment
        │
        ▼
Measurements, observations, and results
        │
        ▼
Versioned evidence and reproducible records
        │
        ▼
Improved designs and shared practical capability
```

This is the “blockchain” aspect of OpenRoot: not speculation or tokenization, but a durable chain of provenance, evidence, revisions, and accountable collaboration.

## Design principles

### Open by default

Useful knowledge should remain available for people to inspect, learn from, reproduce, adapt, and improve.

### Evidence over assertion

Claims should connect to sources, assumptions, test conditions, measurements, calculations, and versioned records.

### Reproducibility

A design becomes more useful when another person can understand what was done, obtain the needed inputs, repeat the process, and compare results.

### Human authority

Automation may assist with searching, drafting, analysis, routing, and verification. Humans retain authority over safety-critical decisions, physical implementation, publishing, spending, remote access, and irreversible changes.

### Appropriate technology

OpenRoot favors technology that is understandable, repairable, resource-aware, locally adaptable, and capable of improving real conditions.

### Useful-output accounting

A guiding idea is:

```text
η = J_useful / J_human
```

where \(J_{\text{useful}}\) represents useful output and \(J_{\text{human}}\) represents the human effort required to create it.

The purpose is not maximizing computation for its own sake. The purpose is increasing useful, durable capability per unit of human effort and available resources.

## Useful-output accounting

A guiding measurement concept is:

```text
η = J_useful / J_human
```

where \(J_{\text{useful}}\) represents useful output and
\(J_{\text{human}}\) represents the human effort required to create it.

This is a planning and reflection tool, not a universal performance metric or a
claim that outputs can always be measured or compared in one way. Its purpose is
to focus attention on useful, durable capability per unit of human effort and
available resources.

OpenRoot also documents lifecycle inputs and outcomes—including materials, labor, energy, maintenance, costs, failures, and useful service—so communities can evaluate whether a system reduces avoidable dependency under their own conditions.


## Evidence before assertion

OpenRoot uses evidence levels to distinguish between an idea, a documented prototype, a repeated measurement, and a reproducible reference design.

| Level | Meaning |
|---|---|
| L0 | Concept, intake, literature, or hypothesis |
| L1 | Documented bench concept or procedure |
| L2 | Bench prototype with preliminary measurements |
| L3 | Repeated prototype with documented failures and costs |
| L4 | Independently reproduced result |
| L5 | Field-ready reference design with reproducible evidence |

An evidence level is not certification, engineering sign-off, legal compliance, or a safety guarantee. Public claims should remain bounded by the evidence, methods, inputs, dates, uncertainty, and stated limitations available for review.

See [Evidence levels](docs/EVIDENCE_LEVELS.md), [Design packets](docs/DESIGN_PACKETS.md), and [Open hardware status](docs/OPEN_HARDWARE_STATUS.md).

## Explore the ecosystem

OpenRoot is the public hub for a focused ecosystem of open-hardware design packets,
local-first open-source tools, and evidence-preserving practical documentation.

- **[Repository map](docs/REPOSITORIES.md)** — active projects, templates,
  governance/reference material, archive boundaries, and external forks.
- **[Design-packet template](https://github.com/jesseray718/openroot-design-packet-template)** —
  the reproducible baseline for open-hardware projects.
- **[Open hardware status](docs/OPEN_HARDWARE_STATUS.md)** — current public
  maturity boundaries for hardware work.
- **[Design packets](docs/DESIGN_PACKETS.md)** — the evidence-gated path from
  concept to a buildable, testable public design.

## Project status and release discipline

OpenRoot is an active experimental build. Work may be documentation, research,
a bounded prototype, a reproducibility method, or a hypothesis awaiting safe
measurement or independent replication.

Public claims should remain bounded by documented evidence, methods, inputs,
dates, uncertainty, limitations, and explicit safety notes. A passing workflow
or completed documentation check does not prove physical performance, safety,
field readiness, certification, regulatory compliance, profitability, or
deployment status.

- [Open hardware status](docs/OPEN_HARDWARE_STATUS.md)
- [Design packets](docs/DESIGN_PACKETS.md)
- [Evidence levels](docs/EVIDENCE_LEVELS.md)
- [Project roadmap](docs/PROJECT_ROADMAP.md)
- [Release process](docs/RELEASE_PROCESS.md)
- [Repository map](docs/REPOSITORIES.md)
- [Changelog](CHANGELOG.md)


## Local-first and human-governed workflows

OpenRoot uses local-first infrastructure to preserve continuity and reduce
repeated work:

```text
observe → retain evidence → classify → retrieve → test → review → improve
```

Automation can help retrieve, draft, analyze, route, and verify. It does not
replace human responsibility for evidence, safety, physical implementation,
publishing, spending, remote access, or irreversible decisions.

The workflow keeps raw operational material private by default and promotes
only reviewed, reproducible, public-safe artifacts into documentation or
releases. See [Superlinear workflow](docs/SUPERLINEAR.md) and
[Superloop governance](docs/SUPERLOOP.md).


## Newton chains

OpenRoot is developing **Newton chains**: reusable, inspectable reasoning paths
from definitions and assumptions through evidence and inference to bounded
conclusions. They are designed so people and future AI collaborators can
propose, inspect, challenge, reuse, and extend work without requiring hidden
context.

A conclusion in a Newton chain is conditional: it records what follows under
its stated definitions, assumptions, evidence inputs, and inference rules.
When those dependencies remain unchanged, a verified pathway can be reused.
When a dependency changes, related conclusions can be revisited while their
history remains available.

See the [Newton-chain design](docs/NEWTON_CHAIN.md) for the current public
architecture, schema, inference-rule draft, and bounded example.

## Contributing

Contributions are welcome in open hardware, documentation, software, measurements, literature review, local-first tooling, repairable systems, and reproducible experiments.

Useful contributions are specific, sourced, testable where possible, and explicit about uncertainty. Please do not present an idea, simulation, or draft as a measured result.

Start with [Contributing](CONTRIBUTING.md), then review the relevant design packet, evidence level, and issue or milestone.

## Licensing

OpenRoot uses a dual-license structure:

- **Documentation, explanatory diagrams, and photographs:** CC-BY-SA-4.0 where marked.
- **Software, firmware, scripts, and simulations:** the applicable GPLv3 SPDX identifier stated in each file.

See [LICENSE](LICENSE), individual file headers, and the
[Licensing map](docs/LICENSING.md). Where repository-wide language and a
file-level SPDX identifier differ, the file-level identifier governs until the
project’s licensing map is reconciled.


## Security and public boundary

Public repositories should contain selected, reviewable, reproducible material—not private operational history.

The following remain out of scope for public release unless separately reviewed and approved:

- Raw logs, handoffs, private notes, and personal correspondence
- Credentials, keys, environment files, device backups, and local paths
- Receipts, expenses, financial records, tax material, and account data
- Recovery exports, vendor trees, build outputs, model artifacts, and unreviewed scripts
- Unsupported performance, safety, legal, financial, or readiness claims

See [Security policy](SECURITY.md) and [Release process](docs/RELEASE_PROCESS.md).

## Contributors
See [CONTRIBUTING.md](CONTRIBUTING.md) for the graded pathway and credit covenant.

- **Rehan Tariq ([@Reh1t](https://github.com/Reh1t))** — Initial LLM & SQLite RAG integration,
  zero-dependency design ([PR #63](https://github.com/jesseray718/openroot/pull/63), issue #53).
  First external code contribution to OpenRoot.

## Roadmap

The path forward is evidence-led:

1. Inventory and classify existing artifacts.
2. Establish safe measurement and stop-condition protocols.
3. Record results, failures, uncertainty, and revision history.
4. Publish reproducible packets with explicit boundaries.
5. Support independent testing, repair, and adaptation.
6. Revise public claims only when evidence changes.

See the full [Project roadmap](docs/PROJECT_ROADMAP.md).


---

*OpenRoot favors useful work over hype: open where possible, evidence-bounded,
repairable, and accountable to the people who need practical technology most.*
