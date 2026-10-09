
## F-ASSERT-NOT-VERIFIED
- **name**: commit-message/seal-doc claim with no verified backing
- **symptom**: push_finish_v1.sh committed "registered via ledger manifests" while zero rows were written ([stage:singles] short-circuited on absent ghost files + missing parent dir); session seal claimed "pushed, remote==local" before first push was rejected
- **cause**: assertions written ahead of verification; [ -f ] && guard swallows the failure path into an [info] echo
- **fix**: greps (or ledger row counts) for the claimed artifact MUST run and pass inside the same script before the commit message is emitted; seal docs are written only after remote==local check prints [banked]
