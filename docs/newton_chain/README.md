# Newton Chain Evidence Ledger

A local-first, content-addressed, typed framework for organizing evidence-backed
claims, models, derivations, experiments, and verification receipts.

## Governing rule

No conclusion without a visible derivation path.
No derivation without declared inputs.
No verification without a reproducible context.
No cross-domain transfer without a typed mapping and stated limits.

## Universal flow

Definition / primitive
→ axiom / postulate / observation / evidence
→ method / derivation / experiment / analysis
→ claim / theorem / model / prediction / decision
→ test / proof / replication / challenge / receipt

## Receipt reuse

A previous receipt is reusable only when the subject content hash and the
dependency fingerprint still match the recorded receipt. A changed dependency,
claim, or declared input requires a fresh receipt.

## Cross-domain safety

`analogizes` and `maps_to` edges require stated mapping limits. An analogy may
help retrieval and hypothesis generation, but does not constitute proof or
physical identity.

## Non-actions in v1

- No network calls
- No model or Ollama calls
- No automatic embeddings
- No Git commit, push, or remote write
- No deletion operations


## Cached derivation pathways

A verified derivation may be reused when the subject content hash, dependency
fingerprint, inference-rule version, and declared execution environment match
the recorded receipt.

When a definition, assumption, evidence record, rule, or environment changes,
dependent results become stale pending targeted reevaluation. Historical receipts
remain available with their original dependency state.

This allows OpenRoot to reuse verified reasoning pathways rather than repeat
equivalent computation.
