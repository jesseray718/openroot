# Canonical Promotion Gate v1

## Purpose

Prevent sandbox experiments from silently becoming canonical OpenRoot
evidence. A sandbox entry may become a canonical claim only after
explicit human approval and a separate staged-promotion step.

## States

| State | Meaning |
|---|---|
| `sandbox_proposal_only` | Evaluator produced a result; no ledger write |
| `sandbox_ledger_appended` | Approved write to sandbox-only ledger |
| `canonical_staging_pending` | Human selected an eligible sandbox entry for review |
| `canonical_staging_approved` | Human approved promotion into staging ledger |
| `canonical_claim_sealed` | Human approved final promotion into canonical ledger |

## Required fields

Every promotion must preserve:

- `sandbox_entry_hash`
- `task_sha256`
- `rules_version`
- `eta_score`
- `merkle_root`
- `claim_eligible`
- `approval_timestamp`
- `approver`
- `staging_entry_hash`
- `canonical_entry_hash`
- `source_path`
- `destination_path`

## Rules

1. Only entries with `claim_eligible: true` may be selected.
2. The sandbox chain must verify before selection.
3. Promotion must be explicit; no automatic promotion.
4. Staging and canonical ledgers must be separate files.
5. The canonical ledger must not be modified by the sandbox evaluator.
6. Every promotion must produce a receipt.
7. No push, commit, deletion, or paid API call may occur without separate human approval.

## First implementation target

Create `promote_sandbox_claim_v1.py` with two explicit modes:

- `--stage --sandbox-entry-hash HASH`
- `--seal --staging-entry-hash HASH`

Both modes must require explicit human-provided hashes and must refuse
to operate on a sandbox entry that is ineligible or whose chain does not
verify.
