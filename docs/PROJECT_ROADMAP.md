<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# OpenRoot Project Roadmap

This roadmap connects GitHub milestones to durable repository artifacts.
Milestones organize work; they do not promote evidence or establish physical
performance claims.

## M0 — Evidence Intake and Artifact Inventory

### Objective

Locate, classify, and link actual existing notes, measurements, design files,
photos, calculations, source code, and sourcing records.

### Expected artifacts

- Completed `INTAKE.md`
- Artifact inventory with revision/date and source location
- Claim boundary
- Known unknowns register
- Public-safe/redaction review

### Completion criteria

- Each material claim links to evidence or is labeled as an assumption.
- No unverified performance claim is presented as a measured result.

## M1 — Thermal Cascade L0/L1 Boundary

### Objective

Define the design hypothesis, system boundary, flows, constraints, hazards,
and excluded claims without representing the design as physically validated.

### Expected artifacts

- System architecture sketch or flow map
- Assumptions and formulas
- BOM seed
- Safety and stop-condition planning
- Router context and review report

### Completion criteria

- The packet is internally consistent.
- Evidence level and language agree.
- The router may correctly return `HOLD_FOR_HUMAN_REVIEW`.

## M2 — First Safe Bench Measurement

### Objective

Run one bounded, appropriately safe, documented test that reduces a high-value
uncertainty.

### Expected artifacts

- Test protocol
- Conditions and instrument record
- Raw data
- Results summary
- Caveats and failures
- Updated evidence-level assessment

### Completion criteria

- The measurement can be inspected and repeated.
- Stop conditions and hazards are documented.
- Results do not exceed what the evidence supports.

## M3 — Reproducible Prototype Packet

### Objective

Prepare a versioned, reviewable packet that another capable builder can inspect
and reproduce within stated constraints.

### Expected artifacts

- Versioned drawings, CAD, or calculations
- BOM and sourcing substitutes
- Build instructions
- Operation and maintenance instructions
- Test protocol and results
- Known limitations and repair path

### Completion criteria

- A defined prototype configuration is reproducible.
- Dependencies, tools, materials, and safety limits are explicit.
- The packet remains honest about untested areas.

## M4 — Field Validation and Revision

### Objective

Document operating conditions, maintenance burden, failures, adaptations, and
repeatability in actual use contexts.

### Expected artifacts

- Dated field logs
- Environmental and operating conditions
- Maintenance and failure records
- Measured outcomes
- Revision rationale
- Updated replication notes

### Completion criteria

- Field evidence is traceable to a configuration and revision.
- Claims remain bounded by documented measurements.
- Failure modes and constraints are published alongside successes.

