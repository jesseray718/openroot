# Runbook

## Evaluate without recording

python3 review_tool.py evaluate --task <task.json>

## Evaluate and record review event

python3 review_tool.py evaluate --task <task.json> --record

## Verify review-event chain

python3 review_tool.py verify

## Stage a sandbox claim for review

python3 promote_sandbox_claim_v1.py stage \
  --sandbox-entry-hash <full 64-char hash>

## Seal requires separate human approval

Do not run seal without explicit human approval and a reviewed staging hash.

python3 promote_sandbox_claim_v1.py seal \
  --staging-entry-hash <full 64-char hash> \
  --approver <name>

## Verify native test pathway ledger

python3 bin/pathway_cache_v1.py verify \
  --root /home/jesse/openroot \
  --ledger <release_dir>/test_pathway_cache.jsonl
