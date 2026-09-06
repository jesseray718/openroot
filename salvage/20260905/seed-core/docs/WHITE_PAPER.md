# White Paper: OpenRoot Seed Core
**Absorption Architecture for Persistent, High-η Inter-Session Context**

## Abstract

Human–AI collaboration suffers from severe context loss between sessions. The OpenRoot Seed Core solves this by treating high-value knowledge, worldview framing, and optimized query patterns as first-class, absorbable “seeds.” Seeds are compact JSON structures deliberately written to survive extraction, structure enforcement, and reloading into future AI windows with minimal degradation. The result is a compounding capability curve.

## Solution Architecture

A seed contains explicit intent, optimized reasoning patterns, domain axioms, cross-references to the thermodynamic ledger, and optional verification hooks. Seeds live in `/sdcard/openroot/session_seeds/`. The live pointer is `current_seed.json`. Extraction tools fold the seed into the durable context bridge.

## Design Invariants

- Absolute path discipline
- η accounting
- Structure enforceability
- Composability
- Verifiability (ledger / hash where claimed)

## Capability Multiplication

Well-formed seeds permanently raise the baseline competence of every subsequent session: reduced re-explanation cost, higher first-response quality, cross-domain coherence, strategic depth, language compression, and moral + thermodynamic consistency.

## Relation to OpenRoot

Seed Core is the memory and capability substrate for AeroCement, UNE computational_flow, PoPW/ACRE, and the local LLM hierarchy. Without it each conversation restarts near zero; with it the project compounds.
