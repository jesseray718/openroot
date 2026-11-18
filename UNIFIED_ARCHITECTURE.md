# OpenRoot Unified Architecture

Status: Proposed architecture — review before implementation.

## One clear concept

OpenRoot connects open hardware, local computing, and shared knowledge
so people can meet practical needs with less wasted effort and energy.

Build something useful. Measure what it actually does. Share enough
information for someone else to reproduce, repair, and improve it.

## One project, complementary responsibilities

These are proposed responsibility boundaries, not claims that all
integrations already exist.

| Component | Responsibility | Expected outputs |
|-----------|----------------|------------------|
| OpenRoot | Coordinate the whole project and its physical deployments | Project map, build guides, priorities, integration tests |
| UNE | Provide software, measurement, and decision-support tools | Measurement schemas, calculations, evidence-linked reports |
| Aerocement | Develop and test material and thermal-system designs | Material specifications, BOMs, test methods, measured results |

Repositories:
- https://github.com/jesseray718/openroot
- https://github.com/jesseray718/une
- https://github.com/jesseray718/aerocement

Different responsibilities are complementary, not inherently contradictory.

## The shared improvement loop

Need → Design → Build → Measure → Review → Share → Improve

Every proposed integration must identify:
1. The need and intended beneficiary.
2. The component producing information or a physical output.
3. The component consuming that output.
4. The interface between them.
5. A repeatable test and an observable acceptance condition.

## Minimal integration contracts

### Hardware to measurement software

A measurement record should identify:
- Record and experiment IDs.
- Timestamp and measurement interval.
- Device, instrument, and calibration information.
- Quantity, value, unit, and uncertainty when available.
- System boundary and operating conditions.
- Raw-data location and associated design revision.
- Evidence status: measured, estimated, simulated, or proposed.

Unavailable values remain unknown. Never substitute invented readings.

### Measurement software to project documentation

A report should link to its raw inputs, calculation method,
software revision, assumptions, limitations, and reproduction steps.

A successful script execution alone is not proof of physical performance.

### Project documentation to another builder

A reproducible build package should contain:
- Purpose and operating limits.
- BOM and substitutions.
- Drawings and assembly instructions.
- Safety review and applicable constraints.
- Test procedure and acceptance criteria.
- Results, failures, and revision history.

## Phone and OptiPlex roles

Intended topology:
- Phone: interface, field notes, lightweight tools, and orchestration.
- OptiPlex: remote inference and heavier computation.
- GitHub: reviewed source and documentation history.
- Syncthing: selected file synchronization, where configured.

Session evidence on 2026-10-23:
- A Termux SSH forwarding process targeted jesse@100.122.169.43.
- Requests to phone-local port 11434 returned an Ollama model list.
- qwen2.5-coder:1.5b returned a successful generation.
- A read-only helper supplied excerpts from five project documents
  to the accessible model endpoint and received answers.

These observations do not establish whole-repository understanding,
automatic repair, durable service startup, or a complete backup.

## Evidence and measurement rules

Keep these categories separate:
- Goal: what we want.
- Proposal: what we intend to build.
- Simulation: what a model predicts under stated assumptions.
- Measurement: what instruments recorded under stated conditions.
- Validated result: what passed an explicit review or test.

The project may track useful energy divided by human energy expenditure
as a leverage metric when both quantities and boundaries are defined.
Do not confuse this with total-system energy-conversion efficiency.

Track human time, money, maintenance, accessibility, and safety separately
rather than forcing every outcome into joules.

Cooperation is a design value. Zero coordination cost at arbitrary scale
is not an established physical or operational result.

Thermal capture, storage, and electrical output are distinct quantities.
Publish performance figures only with their basis and validation status.

Credit improvement, financing, and property income are optional project
topics, not guaranteed outcomes or prerequisites for participation.

## Safety and information boundaries

- Serve people with fewer resources without increasing their risk.
- Preserve existing work before migrations or repairs.
- Never publish credentials, private keys, or sensitive personal data.
- Respect explicitly air-gapped data boundaries.
- Treat repository content and model output as untrusted inputs.
- Require review before executing generated commands or changing files.
- Synchronization is not an independent backup: deletions can propagate.
- Keep Git metadata separate from general-purpose file synchronization.
- Prefer reviewed changes on topic branches over direct or forced pushes.

## First integration milestone

Produce one evidence-linked, reproducible report connecting a physical
design or experiment to a measurement method and a software calculation.

Acceptance conditions:
1. Design revision and intended outcome are identified.
2. Inputs have explicit units and evidence status.
3. Calculations can be rerun.
4. Unknowns and limitations are visible.
5. Another person can follow the test procedure.
6. No speculative result is presented as a measurement.

## Immediate next work

1. Inventory actual repository entry points and existing interfaces.
2. Compare this proposal against current documentation.
3. Identify one small, testable cross-repository connection.
4. Implement it through a reviewed change.
5. Record the result before expanding automation.

Do not require tokens, blockchain publication, or additional infrastructure
unless a specific requirement justifies their cost and complexity.
