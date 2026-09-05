# AX-020, AX-021 & PO-016 — Kingdom Engine v0.3 Review (newtonchain)

Source: newtonchain.md (Kingdom Engine v0.3). Status: code exists [in-progress]; core formula broken [tested — crashes]; this doc records the audit.

## Axioms

AX-020: Every term in a composite metric carries an explicit NOMEN dimension, and a composite may be compared or targeted only if dimensionally coherent. (The NOMEN table already implies this; the code must obey it.)

AX-021: Verified benefit per unit input is a monotone good. No constant — φ included — is a target for a benefit/cost ratio. Efficiency has no optimum short of the physical limit of the substrate.

## Postulate

PO-016: Reward compounding must key on epochs of sustained multi-party verification, never on count of ledger entries. Entry-count compounding is Goodhart-vulnerable and self-inflating: it pays for logging, not for cooperating. [tested — 50 solo entries with zero cooperators produced φ^50 ≈ 2.8×10¹⁰ under the v0.3 code]

## Audit findings [all tested by execution, 2026-07-04]

1. compound_reward() raises NameError (phi_inv referenced, never bound in scope). The compound formula, comfort_index, and kingdom_report have never successfully executed. Everything previously claimed from them is status concept.
2. epochs = sum over entries → see PO-016. Fix: track per-node consecutive verified epochs.
3. resonance_deviation pattern recommends "increase costs" when benefit/cost exceeds φ. A system at 5× benefit/cost scores 0.0 alignment — worse than one at 0.5×. This contradicts AX-017 and AX-021 and is removed. Replacement: monotone score ratio/(ratio+φ), rising toward 1, no optimum.
4. Hexagonal packing score does not detect hexagonal packing: any equidistant point pair (including square lattices) scores 1.0. The honeycomb conjecture is real mathematics — hexagonal partition minimizes perimeter per area (Hales, 1999–2001) — but this test does not measure it. Score demoted to decorative until replaced with an actual lattice-order metric.
5. DIVINE_HARMONICS ships earth_schumann (7.83 Hz), dna_pitch, and "sacred geometry" angles as "resonance targets." Schumann resonance is real electromagnetics; it is not a target for an economic ledger. These constants are unused by any working math and are removed from the engine. Credibility note: shipping them in a grant-facing repo reads as numerology and damages the tested claims around them.

## What survives review

- The truth ledger + pattern detection design is genuinely good: temporal clustering, spatial decay cascade, and knowledge stagnation checks are Observe & Interact and Accept Feedback implemented as code. Keep and extend. [in-progress]
- The lineage DAG (Newton → Shannon → Fuller → Borlaug → ...) is a legitimate citable knowledge graph. Newton's actual line — "If I have seen further it is by standing on the shoulders of giants" (letter to Hooke, 1675/6) — anchors it. Hash-chain it like NOMOS: prior art is Haber & Stornetta (1991) linked timestamping, the direct ancestor of blockchain.
- Fibonacci emergence: phyllotaxis is real (Douady & Couder, 1996 — golden angle emerges from growth dynamics), but asset/reward/lineage COUNTS following Fibonacci ratios has no basis. Term demoted to decorative. General φ caution: most golden-ratio-in-everything claims are myth (Markowsky, "Misconceptions about the Golden Ratio," 1992).

## Permaculture mapping

- Apply Self-Regulation & Accept Feedback — pattern detection engine
- Observe & Interact — spatial decay cascade detection before intervention
- Produce No Waste — slump-as-entropy drag on every score is the right instinct
- Design from Patterns to Details — NOMEN dimensional table before formulas (AX-020 enforces the order)

## Evaluation rule verdict

Fixes cost minutes (three line-level patches), prevent public credibility damage, and restore consistency with AX-017. good/input very high. ACCEPT. Retaining φ-targets or Schumann constants: benefit ≈ 0, credibility cost high. REJECT.

Status: engine [in-progress]; compound formula [concept — code broken]; pattern detection [in-progress]; hexagonal + Fibonacci scores [decorative until replaced].
