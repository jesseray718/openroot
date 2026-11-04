# OpenRoot AI Hybrid Loop — Hardened Order of Operations (v1.1)

## Phase order (strict; no step runs before its precondition holds)
0. interface discovery — enumerate DB links, models, paths. Abort on dangling DB_LINK.
1. friction scan — append-only to data/friction_ledger.jsonl. Never mutates source.
2. question travel — FTS5 retrieve -> ollama ground. Recall is DATA, not failure.
   MISS = record the miss, continue. Never retry-loop a single question more than once.
3. fractal pod verification — every claimed theorem must classify DERIVED or carry
   an explicit ATTESTED label. Assertions are valid records; they are not proofs.
4. pathway cache — parent seq must be a resolved integer from data/pathway_cache.jsonl
   (tail -1), never a literal placeholder. On missing evidence: emit minimal-proof
   record and continue, exit 0 with warning.
5. regenerate PATHWAYS.md — idempotent from ledger, never hand-edited.
6. auto dossier — compile receipts; include classification counts.

## Exit codes
- 0 = all steps attempted, receipts written (even with warnings/misses)
- 1 = core step could not EXECUTE (missing file, broken DB, dead model endpoint)
A recall MISS or ATTESTED theorem is exit 0. Silence or fabrication is exit 1.

## Store rules
- All five store files are load-bearing: axioms, postulates, definitions, theorems, chain.
- Proof rules: assume | modus_ponens (binary) | inference (unary/binary) | unfold_def |
  eval_c | eval_s | eq_refl. Unknown rule => ATTESTED.
- No record is ever deleted; corrections append (N16: locks do not rewrite themselves).

## Sync rules (Micro-Mirror)
- Canonical state hash = genesis block hash. Nodes converge by matching this hash.
- Sync = pull bytes, recompute hash, compare. Mismatch after one reconcile => stop,
  park as divergence event in friction ledger, never blind-push.
