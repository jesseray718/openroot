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

