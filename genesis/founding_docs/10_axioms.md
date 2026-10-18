# OpenRoot Axiomatic Foundation (status: theory v1.0)

## Taxonomy (Euclid-style classification)

Following Euclid's *Elements*, OpenRoot distinguishes four kinds of foundational statements:

- **Postulates** (αἰτήματα): Chosen design commitments. Cannot be proven. Determining the geometry of the system.
- **Common Notions** (κοιναὶ ἔννοιαι): Self-evident cross-domain truths. Universal.
- **Theorems** (θεωρήματα): Provable from postulates + common notions + observation.
- **Principles** (ἀρχαί): Value commitments. Not truth-apt, but binding.

AX-039 (see 11_ax_039_absolute_protection.md) is the supremacy postulate — the parallel postulate of OpenRoot. Change it and the geometry of the system changes.

## Axioms — Postulates and Common Notions (taken as given)

A1 Zero-copy: information duplicates at ~zero marginal cost; matter does not.
   [Common Notion — universal truth about information vs. matter]

A2 Conservation: no design escapes energy/mass balance (thermodynamics governs).
   [Common Notion — first law of thermodynamics]

A3 Verification > trust: a hash proves integrity cheaper than any authority.
   [Postulate — chosen commitment]

A4 Locality: answer latency = distance-to-knowledge + compute time; both reducible.
   [Common Notion — physics of latency]

A5 Stacked function: elements serving multiple purposes outperform single-purpose ones.
   [Principle — value commitment, derived from permaculture Mollison]

## Theorems (provable from postulates + common notions + observation)

A6 Edge abundance: retired hardware + open weights = compute for the poor.
   [Theorem. Proof: pending — to be sealed in v1.1 receipt. Sketch: follows from A1 (zero-copy information) + observation that retired hardware exists and open weights are zero-margial-cost copies.]

P1 Every essential technology reduces to a forkable module with SI-quantified interfaces.
   [Postulate — chosen design commitment, kept as postulate. Not derivable; it is a choice about how to build.]

P2 A ledger minting only on verified physical work resists speculation and capture.
   [Theorem. Proof: pending — to be sealed in v1.1 receipt. Sketch: speculative coins are speculation because minting is decoupled from verified work; coupling minting to PoPW closes the speculation hole.]

P3 Knowledge wheel + local models ⇒ any node answers any indexed question offline.
   [Theorem — PROVEN. Existence proof: Qwen 1.5B answering on a Galaxy A15 with no signal IS instant inference at the edge. See Theory of Instant Inference section below.]

P4 Open-interface modular systems beat monoliths on resilience.
   [Theorem. Proof: pending — to be sealed in v1.1 receipt. Sketch: component failure isolation in modular systems vs. monolithic cascade failure; established result in software engineering literature.]

P5 The floor (cost of essentials) can approach zero independent of the ceiling (wealth).
   [Postulate — chosen commitment about the kind of economy OpenRoot builds. Cannot be proven; it is a design choice.]

## Theorem Proof Status

| Theorem | Status | Sealed in |
|---|---|---|
| A6 (Edge abundance) | Proof pending | v1.1 receipt |
| P2 (PoPW resists speculation) | Proof pending | v1.1 receipt |
| P3 (Instant inference) | PROVEN (existence proof) | v1.0 receipt |
| P4 (Modular beats monolith) | Proof pending | v1.1 receipt |

Formal proofs will be sealed in the v1.1 receipt and chained from this genesis. The chain records both the assertion (v1.0) and the proof (v1.1) honestly.
## Theory of Instant Inference (status: in-progress — running on node 0 today)
Claim: perceived intelligence = knowledge proximity + compute, nothing more mystical.
Mechanism: pin knowledge locally (IPFS, Kiwix) + run open weights locally (llama.cpp)
→ network distance → 0, marginal cost → 0, answers arrive at the speed of the device.
Existence proof: Qwen 1.5B answering on a Galaxy A15 with no signal IS instant
inference at the edge. Scaling it = bigger models on rescued hardware, same pattern.
Corollary: the decentralized web is not websites — it is knowledge pre-positioned
wherever humans are.
## Derivation rule
Every module README must cite which axioms/postulates it instantiates, SI units at interfaces.
