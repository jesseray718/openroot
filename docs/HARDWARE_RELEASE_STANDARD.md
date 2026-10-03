# Hardware Release Standard

OpenRoot publishes physical work as an open-hardware design packet. A packet
allows people to distinguish a concept, a prototype, a reproducible build,
and a validated result.

## Required Packet Contents

A public design packet should include:

| Item | Purpose |
|---|---|
| `README.md` | Purpose, scope, status, and entry point |
| `STATUS.md` | Current maturity and claim-status labels |
| `SYSTEM.md` | System description and boundaries |
| `BOM.md` | Bill of materials, quantities, substitutions, and sourcing notes |
| `BUILD.md` | Build sequence and required tools |
| `SAFETY.md` | Hazards, constraints, PPE, and conditions not to use |
| `MEASUREMENTS.md` | What is measured, units, instruments, and data handling |
| `TEST_PLAN.md` | Test method, success criteria, failure criteria, and limitations |
| `PROVENANCE.md` | Source, prior art, adaptations, and evidence traceability |
| `LICENSE.md` | Hardware/documentation/software licensing notice |
| `metadata.yaml` | Machine-readable identity and status metadata |

## Status Requirements

Every packet must identify what is:

- `demonstrated`
- `documented`
- `proposed`
- `speculative`

A prototype should not be described as a validated product. A measurement
should state conditions and uncertainty. A design packet should distinguish
its own observations from cited external information.

## Release Checks

Before public release, review:

- Build completeness and missing dependencies.
- Mechanical, thermal, electrical, chemical, and field hazards.
- Materials and sourcing assumptions.
- Units, measurement methods, and calibration needs.
- Third-party drawings, data, images, and licensing.
- Reproducibility by someone outside the original workspace.
- Clear version/status identification.

## Existing Packet

The [Thermal Cascade packet](../designs/thermal-cascade/README.md) provides
the initial OpenRoot packet structure. It should be interpreted according to
its own `STATUS.md`, safety documentation, measurements, and test plan.
