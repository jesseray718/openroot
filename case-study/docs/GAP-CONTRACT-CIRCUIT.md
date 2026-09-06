# Gap → Contract → Ledger → Implementation Circuit
Closes the loop of resources into the Agape system.

## States
1. GAP observed (from SEED-GAP-ANALYSIS or live lowest-node signal)
2. OPPORTUNITY matched (grant draft, in-kind offer, open bounty, or internal surplus)
3. CONTRACT accepted (terms bound by Agape rules)
4. RESOURCES land in the appropriate ledger (case-study / leveling / business)
5. IMPLEMENTATION begins (lowest-node-first tasks)
6. ATTESTATION (benefit measured at recipient, two-node rule when required)
7. GAP closed or reduced → new ranking

## Local (already possible) implementation
- Gaps live in case-study/docs/SEED-GAP-ANALYSIS.md and survival/mesh seeds
- Opportunities live in case-study/grants/ drafts + any incoming offers
- Acceptance = explicit entry in the case-study ledger:
  event: "contract_accept"
  fields: gap_id, opportunity_id, amount_or_in_kind, terms_hash, timestamp
- Resources recorded as contribute / invest into the correct pool
- Implementation tasks written as ordered actions (survival cards already show the pattern)
- Attestation recorded as separate ledger events pointing at recipients

## Smart-contract mirror (future, optional)
When a public chain is used, the same states become:
- GapRegistry (hash of gap description + severity)
- OpportunityRegistry (grant/bounty/in-kind terms)
- Accept(gap, opportunity, terms) only if Agape constraints pass
- Escrow or direct mint into a public-good vault controlled by multi-attestation
- Release on attestation that benefit landed on designated lowest nodes
- No owner keys; upgrade path requires broad attestation, not a privileged admin

## Circuit-closing rule
No resource is accepted that:
- creates an owner above the ledger
- restricts open licensing
- cannot show a path to a measured lowest-node yield

When a gap is matched to an opportunity that satisfies the rule, the system is authorized to accept and implement. That is the closed loop.
