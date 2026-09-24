# OpenRoot

**OpenRoot is an open-source technology commons for preserving, validating, improving, and implementing knowledge that can materially improve the world.**

The project is building a verifiable coordination layer for open hardware, engineering research, technical literature, experimental records, workflows, local computation, and practical infrastructure.

OpenRoot is not only a software repository. It is an effort to make useful technology easier to study, reproduce, improve, share, and put into practice.

## Mission

OpenRoot exists to help keep high-value technical knowledge open and actionable.

Many important ideas are fragmented across documents, conversations, prototypes, local machines, abandoned repositories, and closed platforms. Even when a design is publicly visible, it is often difficult to determine:

- What the design actually claims.
- Which assumptions it depends on.
- What was tested.
- What changed between versions.
- Which materials, energy, labor, and tools are required.
- Whether someone else can reproduce or improve it.
- How it connects to related systems and evidence.

OpenRoot is being developed to provide durable, transparent records for that work.

## What OpenRoot supports

OpenRoot is intended to support:

- Open hardware designs and build documentation.
- Engineering notes, scientific literature, and technical references.
- Reproducible experiments and measured results.
- Design iteration, version history, and evidence trails.
- Workflows for fabrication, testing, repair, and maintenance.
- Distributed collaboration around practical technology.
- Local-first computing, AI-assisted research, and knowledge retrieval.
- Resource, energy, cost, labor, and usefulness accounting.
- Open technology that strengthens local and community-scale capability.

## Thermal Cascade

A central example is the **Thermal Cascade**: an appropriate-technology system intended to improve how thermal energy is captured, transferred, stored, and used.

OpenRoot provides a place to develop and protect the surrounding knowledge commons:

- Design rationale and system architecture.
- Thermal models and assumptions.
- Build methods, materials, and constraints.
- Measurements, tests, failures, and revisions.
- Literature references and prior art.
- Implementation workflows and maintenance knowledge.
- Open collaboration without losing provenance.

The goal is not to make claims that cannot be tested. The goal is to preserve the chain from idea to design, design to experiment, experiment to evidence, and evidence to real-world implementation.

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

## Local-first infrastructure

OpenRoot uses local-first tools to support the knowledge commons:

- Local AI models for research assistance, drafting, coding, review, and analysis.
- SQLite and JSONL records for durable structured state.
- Shared context tools for coordination across local terminals and work windows.
- Git-reviewed source, designs, and documentation.
- Human-gated operations for commits, pushes, recovery actions, remote access, and other consequential changes.

The automation serves the work. It does not replace human responsibility for evidence, safety, implementation, or governance.

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

## Current status

OpenRoot is an active experimental build.

Current work includes local coordination tools, shared context, reproducible records, AI-assisted research workflows, ledger reconciliation, and documentation for appropriate-technology systems. The project is still evolving, and published material should be read as an open working system rather than finished engineering certification.

## Contributing

Contributions are welcome from people working in:

- Open-source software and local AI.
- Open hardware and fabrication.
- Thermal systems, energy, shelter, food, water, and resilient infrastructure.
- Engineering research and technical documentation.
- Scientific literature review and reproducible experiments.
- Distributed systems, mesh networks, and decentralized coordination.
- Knowledge management, archival systems, and evidence provenance.

Please keep contributions specific, documented, testable where possible, and respectful of the project’s open licensing and evidence-first approach.

## Licensing

OpenRoot uses a dual-license model:

- **Code and software:** GPL-3.0-or-later.
- **Documentation, research, open-hardware designs, technical literature, workflows, diagrams, and other non-code project material:** CC BY-SA 4.0.

This keeps the software free and copyleft while ensuring that the knowledge, documentation, and design commons remain shareable and share-alike.

See [LICENSE](LICENSE) and project file headers for the applicable license.
