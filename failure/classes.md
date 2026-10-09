
## F-ASSERT-NOT-VERIFIED
- **name**: commit-message/seal-doc claim with no verified backing
- **symptom**: push_finish_v1.sh committed "registered via ledger manifests" while zero rows were written ([stage:singles] short-circuited on absent ghost files + missing parent dir); session seal claimed "pushed, remote==local" before first push was rejected
- **cause**: assertions written ahead of verification; [ -f ] && guard swallows the failure path into an [info] echo
- **fix**: greps (or ledger row counts) for the claimed artifact MUST run and pass inside the same script before the commit message is emitted; seal docs are written only after remote==local check prints [banked]

## F-GREP-CASE-MISMATCH (corollary of F-PLACEHOLDER-LITERAL)
- **name**: gate grep literal differs in case from document text
- **symptom**: window_bank_v2_20261009.sh exited silently at gate — grep -q 'smoke runs...' vs doc "Smoke runs..."; set -e + grep -q = zero diagnostics
- **fix**: greps over prose must use -i, or match a short anchor token, never a hand-retyped sentence; a gate that dies silently is indistinguishable from a gate that passed
