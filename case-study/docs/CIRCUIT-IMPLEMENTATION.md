# Circuit Implementation Details

## Local (live today)
1. Gaps: case-study/docs/SEED-GAP-ANALYSIS.md + mesh-data/*/INDEX.md
2. Opportunities: case-study/grants/* drafts + incoming offers
3. Acceptance: append contract_accept event to case-study ledger
4. Resources: contribute / invest into the matching pool (case-study, leveling, business)
5. Implementation: ordered action lists (survival cards already show the pattern)
6. Attestation: separate ledger events with recipient references
7. Re-rank gaps after each close/reduce

## Bridging to chain (when desired)
- Periodically publish Merkle root of the local ledger (same pattern already used with OpenTimestamps)
- GapRegistry / OpportunityRegistry hold only hashes + severity/domain
- Accept() checks the four Agape predicates
- Escrow can be a simple multi-attestation vault; no admin key
- Attest() accepts a ZK proof or public two-node signatures
- Local nodes remain authoritative for offline operation; chain is a public mirror and settlement layer

## Failure handling
- If chain is unavailable, local ledger continues
- If attestation fails, resources stay reserved or return under published terms
- No path exists that creates a permanent owner
