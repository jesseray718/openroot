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
