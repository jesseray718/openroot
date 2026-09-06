# AX.NWB.FRACT.002 — Modular Atomic Composition for Verified Efficiency

**Date:** 2026-07-17  
**Status:** Revised (v2) — Scoped to verifiable claims  
**Author:** Jesse Ray McMillen  
**Related:** H-003, ACRE (PoI), UNE, compute/n0/ layer

## Core Claim (Revised)

Atomic, single-purpose local functions can be composed into chains that deliver **measurable efficiency and reliability gains** over monolithic models **on bounded, verifiable task classes**, when paired with external verifiers.

Recursive (fractal) composition is useful **only up to the depth where error compounding and verifier strength allow**, not as an unbounded scaling strategy.

## Key Shifts from v1

- Removed claim of "emergent capability rivaling frontier models on open-ended work".
- Added explicit requirement for **external verifiers** (not self-critique).
- Added error-compounding limits on composition depth.
- Reframed success metric from "emergence" to **"verified efficiency + reliability per task class"**.
- Tied directly to measurable PoPW/ACRE via efficiency/reliability deltas.

## Architecture Principles

1. **Atomic First** — Every unit does one thing with a clear I/O contract.
2. **Verifier-Gated Composition** — Chains only deepen when a sound external verifier exists for that task class.
3. **Measurable at Every Level** — Every n0 and c1 unit must be instrumented for tokens, energy, latency, and verifier score.
4. **Depth Discipline** — Maximum useful depth is bounded by per-step verified reliability and target end-to-end reliability.

## Integration with OpenRoot

- **compute/n0/** = Level 0 atomic functions.
- **C1 reasoner** = Level 1 verified chain (generator + external verifier + ledger).
- **fractal-scale** = Controlled composition engine with depth limits and measurement.
- **ACRE / PoPW** = Efficiency and reliability deltas at each level become mintable Proof-of-Insight events.
- **H-003** = Can apply the same modular + verified pattern to multi-physics optimization and ledgering.

## Success Criteria (Falsifiable)

- On ≥3 bounded task classes with sound verifiers, the modular stack achieves ≥ baseline quality at ≤ 70% energy/task.
- Composition depth is capped using the error-compounding formula rather than grown indefinitely.
- Self-critique loops are replaced by external verifiers.
