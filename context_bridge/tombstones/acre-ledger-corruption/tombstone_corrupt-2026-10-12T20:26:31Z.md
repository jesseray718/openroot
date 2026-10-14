---
tombstone_id: acre-ledger-corruption-20261012T202631Z
timestamp: "2026-10-12T20:26:31Z"
canary: CANARY:OPENROOT-ACRE-FINAL-REPAIR-V1
---
# Acre Ledger Corruption Record

**Corrupted File:** `LEDGER.jsonl.bak.1785547700` (9 records)
**SHA256:** 69fdc687bd2354924dd73eb03a494dea0038a6ed3c840bda3772823b53444d5c

## Symptoms
- Only genesis record carried a `hash` field
- Records 2–9 lacked self-hashes despite `previous_hash` being set
- Record 9's `previous_hash = ea045215...` matched sha256(raw-line) of record 8
- Conclusion: writer computed hashes but failed to persist them into `hash` field

## Root Cause
Serialization bug in original ledger writer: computed `sha256(raw-json-line)` but only persisted to genesis record.

## Repair Action
Regenerated self-hashes for all 9 records using the same recipe (sha256 of compact JSON line), verified linkage integrity.

## Lessons
- Instrumentation failures compounded schema defects across 4 verifier attempts
- Field-name confusion (prev vs previous_hash)
- Genesis sentinel tolerance too narrow
- Empty previous_hash on non-genesis treated as pass rather than defect
- Chain verification must check BOTH directions (self-hash exists AND prev-links match)
