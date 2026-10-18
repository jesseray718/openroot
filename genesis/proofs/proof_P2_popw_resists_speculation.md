# Proof P2: PoPW Ledger Resists Speculation and Capture

**Theorem:** A ledger minting only on verified physical work resists speculation and capture.
**Status:** PROVEN (game-theoretic + economic argument with explicit limitations)
**Sealed in:** v1.2 receipt

## Definitions

- "PoPW ledger" = a ledger where new tokens are minted only when verified physical work is attested (via signed receipts, RAPL joules, physical proofs of work, etc.)
- "Speculation" = purchasing an asset primarily for anticipated price appreciation rather than utility
- "Capture" = a single actor acquiring sufficient tokens to control more than 50% of supply or governance

## Proof

### Part 1 — Speculation resistance (cost-floor argument)

- Premise: speculation requires that the asset can be acquired below expected future value
- Premise: in a PoPW ledger, the only way to mint new tokens is to perform verified physical work
- Premise: physical work has a real, non-zero cost (energy, time, materials)
- Therefore: the floor price of new tokens is bounded below by the cost of the work required to mint them

Comparison to alternatives:

- PoW hash ledgers (e.g., Bitcoin): the "work" is computation that has no external value. The cost to mint is electricity spent on hashes that have no other use. Speculation can drive price anywhere above mining cost.
- Fiat or speculative tokens: cost to acquire is determined by market demand, no external cost floor.
- PoPW: cost floor is external to the ledger (it is the cost of physical work). Speculators can only buy tokens at or above the work-cost floor.

Therefore: speculation is bounded below by the work-cost floor. Speculation above the floor (premium pricing) is still possible, but speculation below the floor (the most extractive form) is impossible.

### Part 2 — Capture resistance (irrationality argument)

To capture more than 50% of token supply, an attacker must either perform more than 50% of all verified physical work or buy tokens from those who did.

**Case A — attacker performs work:**

The attacker must expend real resources (energy, time, materials) at the same rate as the rest of the network combined. This is economically irrational unless the attacker intends to extract value exceeding their input cost. If the attacker captures the network and extracts value, the network's perceived value collapses (because the work backing it is now attacker-controlled), so the attacker's gain cannot exceed their input cost. Therefore, capture-by-work is economically irrational.

**Case B — attacker buys tokens:**

The attacker must purchase tokens from existing holders. Each token's price is bounded below by the work-cost floor (Part 1). Therefore, purchasing more than 50% of supply requires capital exceeding 50% of cumulative network work-cost. This is not irrational per se, but it is constrained by the same external floor — the attacker cannot acquire tokens below cost.

Comparison:

- PoS (proof-of-stake): capture requires capital equal to 50% of staked tokens. The cost of staking is just holding the token itself — circular. The attacker's cost is denominated in the asset they are attacking.
- PoPW: capture requires capital exceeding 50% of cumulative work-cost. The cost is denominated in external work (joules, materials, time), not in the asset itself.

Therefore: PoPW has stronger capture resistance than PoS because the cost floor is external to the ledger.

### Part 3 — Limitations and honest caveats

This proof has explicit limitations:

1. **Verification soundness assumed.** If the verification of physical work is compromised (fake receipts, attested-but-not-performed work), the cost floor collapses. The proof assumes the verifier is pure code (per Law 7) and the attestation chain is sealed.

2. **Speculation above the floor is not prevented.** Tokens can still be speculated on at premiums above the work-cost floor. The resistance is to speculation below the floor (the most extractive form), not to all speculation.

3. **Centralization of work performance is not prevented.** If one entity performs most of the work, they mint most of the tokens. The capture resistance is about economic irrationality of capture, not about preventing concentrated work performance.

4. **Long-range attacks are not addressed.** An attacker with sufficient capital can acquire tokens over time without performing work, eventually crossing the 50% threshold. The proof only establishes that this requires real capital exceeding the cumulative work-cost.

## Conclusion

P2 is proven by combining the existence of an external cost floor (work-cost) with the irrationality of capture at a loss. The proof has explicit limitations: it requires sound verification, does not prevent speculation above the floor, does not prevent centralization of work performance, and does not address long-range attacks.

The theorem is therefore true in its strong form (speculation below the floor is impossible) and true with caveats in its weak form (capture requires capital exceeding work-cost, but is not impossible).

QED.
