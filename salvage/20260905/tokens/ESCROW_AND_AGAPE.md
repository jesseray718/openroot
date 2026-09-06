# Escrow Design + Agape Rule

**Date:** 2026-07-24  
**Status:** Concept for Advancement Engine / STEP

---

## Agape Rule (Exact)

Benefit is measured at the recipient, never the actor.

A unit of good exists only where someone other than the claimant received it.

A benefit claim (WORK, STEP, SKILL, or ACRE) enters the ledger only when attested by at least two nodes other than the claimant.

This is the non-negotiable filter against self-dealing.  
No amount of self-reported data is enough. Two independent attestations are required before any mint or escrow release.

---

## Escrow Design (Practical, Layered)

### Goals
- Transparent
- Minimal trust
- Works before full on-chain ACRE / WORK is live
- Releases only on thermodynamic proof + agape attestation
- Handles disputes without politics

### Layer 1 — Pre-mainnet (now)

1. **STEP is proposed** with clear success criteria and expected η gain.  
   Proposal is published as a GitHub issue + IPFS hash of the full brief.

2. **Contributions** are sent to a transparent multi-party address or recorded in a public ledger file (`ledger/escrow_log.jsonl`).  
   Each contribution records: amount, currency, timestamp, STEP ID, contributor (optional anonymity).

3. **Escrow hold** is visible to everyone.  
   No single person can release funds.

4. **Release conditions** (all must be true):
   - Open-source solution published (CC-BY-SA / GPL)
   - Full Capture → Store → Exert data + hash published
   - At least L2 thermodynamic proof
   - Two independent nodes (not the solver) attest under the agape rule
   - Solution meets the original success criteria

5. **Release** happens by 2-of-3 (or 3-of-5) multi-sig / multi-party approval once the above is verified.  
   Early implementation can use existing multi-sig tools or a simple community-held key set documented in the STEP brief.

6. **Timeout / dispute**:
   - If no valid claim after a published deadline, funds can be returned or rolled into the next STEP by the same multi-party set.
   - Disputes are resolved by additional independent attestations, not by vote of the original funders.

### Layer 2 — On-chain (future, once Solana ACRE/WORK is live)

- Native escrow smart contract.
- Contributions lock tokens or stablecoins against a STEP ID.
- Release is triggered by an oracle that checks:
  - IPFS / on-chain hash of the solution + data
  - Two agape attestations (signed by known validator keys)
  - Measured η delta above the threshold stated in the STEP
- Automatic percentage flow of future WORK savings can be programmed as ongoing claims.

### Minimal Trust Principle

The escrow never trusts the solver’s word alone.  
It trusts the combination of:
- Published open data
- Physical energy conservation (Capture → Store → Exert)
- Two independent human/node attestations (agape)

That is the highest-efficiency verification path available with current tools.

---

## Integration with Tokens

- Successful escrow release → STEP is minted to the solver.
- The humans who performed physical validation / installation earn SKILL tagged to the same event.
- The η record is written to the thermodynamic ledger and can multiply or qualify ACRE.
- Ongoing measured work savings can continue to mint small WORK streams that may flow back to original contributors according to the STEP terms.

---

*No escrow release without agape.  
No mint without measured useful joules.*
