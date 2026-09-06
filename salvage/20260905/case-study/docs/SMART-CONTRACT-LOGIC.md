# Smart-Contract Logic for the Gap → Resource Circuit
Agape constraints are non-negotiable.

## Core state machine
GapOpen → OpportunityMatched → ContractAccepted → ResourceEscrowed → ImplementationStarted → Attested → GapClosed / GapReduced

## Required predicates before Accept
1. terms_do_not_create_owner == true
2. knowledge_license_open == true
3. lowest_node_yield_path_exists == true
4. attestation_rule == "benefit measured at recipient" (+ two-node when required)

## Minimal contract surface
- registerGap(gapHash, severity, domain)
- registerOpportunity(oppHash, source, amountOrInKind, termsHash)
- accept(gapId, oppId, termsHash)  // only if predicates pass
- escrow / recordResource(pool, amount, ref)
- startImplementation(gapId, actionRoot)
- attest(gapId, recipientRoot, proof)
- closeGap(gapId, remainingSeverity)

## Zero-knowledge exploration
What ZK can usefully hide while still proving the Agape rules:

Useful ZK targets:
- Prove “benefit landed on a recipient set that satisfies lowest-node criteria” without revealing personal identities of the recipients
- Prove “attestors are distinct and not the claimant” without revealing attestor identities on-chain
- Prove “termsHash matches a public Agape template” without publishing every local negotiation detail

What should remain public:
- Gap domain and severity class
- That a contract was accepted under Agape predicates
- Aggregate resource movement into public-good pools
- Final gap-closed / reduced status

What ZK should not be used for:
- Hiding the existence of owners or preferential claims
- Obscuring whether knowledge remains open

Practical path:
- Phase 0 (now): pure ledger events (already defined) — full transparency, zero chain dependency
- Phase 1: public chain registry of gap/opportunity hashes + accept events
- Phase 2: selective ZK attestation layer only for recipient privacy and attestor distinctness
