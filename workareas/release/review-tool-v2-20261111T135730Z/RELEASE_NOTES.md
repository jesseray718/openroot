# Review Tool v2 — Release Notes

## Scope

Sandbox-only, noncanonical workflow evaluation and review-event ledger.

This release does **not** replace, modify, or promote any live OpenRoot
ledger, pod schema, Newton chain, POPW ledger, or pathway cache.

## What is included

- `review_tool.py` — sandbox review/evaluation tool v2
- `test_review_tool.py` — 11 automated unit/integration tests
- `README.md` — operational boundary and commands
- `INSTALL_RECEIPT.json` — installation artifact hashes
- `ACCEPTANCE_*.json` — operational acceptance receipt
- `WORKFLOW_TEST_RECEIPT.json` — isolated CLI workflow test receipt
- `MILESTONE_SANDBOX_LATTICE_EVALUATOR_V1.json` — prior evaluator milestone
- `LATTICE_EVALUATOR_V1.md` — evaluator documentation
- `CANONICAL_PROMOTION_GATE_V1.md` — promotion-gate design
- `test_pathway_cache.jsonl` — fresh native pathway-cache test ledger
- `native_record_output.txt` — native CLI record output
- `native_verify_output.txt` — native CLI verify output
- `SHA256SUMS.txt` — release artifact hashes

## Verification status

- 11 local tests passed.
- Operational acceptance passed.
- Isolated CLI workflow tests passed (13 checks).
- Native pathway-cache test ledger verified.
- Legacy A15 sandbox chain verified (3 entries).
- Legacy staging chain rejected as invalid and preserved unchanged.
- Live OpenRoot tree and live ledgers unmodified.

## What this is not

- Not a canonical ledger.
- Not a canonical claim.
- Not scientific verification.
- Not authenticated human approval.
- Not a replacement for the native OpenRoot foundation.
- Not authorized for automatic promotion into any live ledger.

## Native integration

The workflow was recorded through the existing native
`bin/pathway_cache_v1.py record` interface into a fresh test ledger:

`test_pathway_cache.jsonl`

The native `verify` command validated that test ledger. No live
`data/pathway_cache.jsonl` was written.

## Next boundary

Canonical integration requires a separate, human-approved adapter that
targets the existing native writer and schema. Sandbox review events must
not be automatically imported as canonical evidence.
