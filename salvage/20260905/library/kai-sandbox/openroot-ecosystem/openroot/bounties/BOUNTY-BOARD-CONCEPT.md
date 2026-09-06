# The OpenRoot Bounty Board — A New Model for Directing Human Innovation

**Status:** Concept  
**Author:** Jesse McMillen  
**Date:** 2026-07-05  
**License:** CC-BY-SA 4.0 (docs) | GPL v3 (code) | No patents.  

---

## The Problem

Right now, the direction of human innovation is set by consumerism, greed, and capitalism. What gets funded is what generates profit for the few — not what meets the needs of the many. Necessity is the mother of invention, but the current system decides whose necessity matters, and the answer is always: whoever has money.

Nobody is thinking as a united species. Nobody is asking: what do humans actually need, and what happens if we direct our collective resources at those needs deliberately?

---

## The Concept

The Bounty Board is a structured, open protocol where:

1. **Anyone can propose a bounty** for a solved human need (clean water, zero-fuel transport, affordable shelter, food security)
2. **Anyone can contribute** — $0.20, $1, $5 — any amount, from anyone, anywhere
3. **The bounty is released** to whoever solves it first — openly, verifiably, with published data
4. **The solution becomes open-source** — CC-BY-SA 4.0 / GPL v3 — no patents, no monopoly
5. **The solver earns ACRE** — the innovation token, minted only for verified new knowledge

This is not charity. This is procurement. The species is procuring its own solutions.

---

## How It Differs From Existing Systems

| Model | Who Decides | Who Benefits | Motivation |
|---|---|---|---|
| Venture Capital | Investors | Shareholders | Return on capital |
| Government Grants | Politicians | Selected applicants | Political priorities |
| Prizes (XPRIZE, etc.) | A committee | One winner | Prestige + prize money |
| **OpenRoot Bounty Board** | **Anyone** | **Everyone** | **Human need** |

The key difference: the bounty board is not controlled by a board of directors or a government committee. It is a protocol. Anyone can fund it. Anyone can claim it. The only gate is verifiable, reproducible proof.

---

## The Agape Mathematics Connection

From the agape formalization (AX-018, AX-019):

> Benefit is measured at the recipient, never the actor. A unit of good exists only where someone other than the claimant received it. A benefit claim enters the ledger only when attested by at least two nodes other than the claimant.

The bounty board operationalizes this:
- **The funder** (whoever puts in $0.20) receives no direct benefit from the solution being built — they're contributing for the good of the system
- **The solver** earns ACRE only when their solution is verified to work AND is open-sourced
- **The recipient** (everyone who uses the open-source solution) is where the benefit is measured
- **Two validators** must confirm the solution works before the bounty releases

This is agape as economics: the reward formula `reward = base * phi^min(epochs,50) * (1 + ln(cooperators)/phi)` means cooperation compounds exponentially. Each funded bounty that produces an open solution adds a cooperador to the system. The math favors the species, not the individual.

---

## Examples — What This Could Do

| Scenario | Contribution Per Person | Participants | Total Bounty | Outcome |
|---|---|---|---|---|
| Delta-T thermal car | $1 | 1M Americans | $1,000,000 | Open-source zero-fuel vehicle plans |
| Pump-placed aerated concrete | $0.20 | 10M globally | $2,000,000 | Construction method that does more concrete than humanity has done since the beginning of civilization — with near-zero labor |
| Water purification module | $0.50 | 5M globally | $2,500,000 | Open-source filter anyone can build |
| Affordable shelter module | $1 | 3M globally | $3,000,000 | Ferrocement dome plans + verified build data |
| Cooling labyrinth for hot climates | $0.25 | 4M globally | $1,000,000 | Zero-electricity cooling design validated in 3+ climate zones |

These numbers are illustrative. The point is the principle: when 20 cents from millions of people converges on a specific, verifiable need, the species can procure solutions at a speed that no corporation, government, or billionaire can match.

---

## The Structural Innovation

This is not a Kickstarter. Kickstarter funds a creator. This funds a result.

This is not a prize competition. Prize competitions end when someone wins. The bounty protocol continues — each solved bounty generates new knowledge that makes the next bounty cheaper to solve.

This is not a DAO. DAOs vote on governance. The bounty board is outcome-focused: define the need, fund the need, release on proof. No politics. No committees. No ownership of the result.

---

## Guided by Permaculture Principles

- **Obtain a Yield:** Every bounty produces a usable, open-source artifact
- **Apply Self-Regulation & Accept Feedback:** Solutions must publish data — failures and successes — so the next iteration improves
- **Integrate Rather Than Segregate:** Each solution is a module that connects to the OpenRoot ecosystem (git + IPFS + ACRE)
- **Use Small & Slow Solutions:** Small bounties first (water filter) → compound into bigger bounties (vehicle, power plant)
- **Design From Patterns to Details:** The pattern is "fund the need, not the brand." Details emerge from the builders who solve it.

---

## ACRE Token Role

The ACRE token is not the bounty currency. The bounty is funded in any currency (USD, BTC, anything). ACRE is minted only for the solver — as recognition of verified innovation contribution. ACRE cannot be bought. It can only be earned by producing new, verified, open knowledge that meets a human need.

See: `tokens/ACRE_SPECIFICATION.md`

---

## What Happens Next

The bounty board concept is complete. The implementation requires:

1. **Protocol specification** — how bounties are proposed, funded, escrowed, validated, and released
2. **Escrow mechanism** — where contributed funds are held transparently until a solution is validated
3. **Validation framework** — who validates, what constitutes proof, how disputes are resolved
4. **First bounty proposal** — the first real test of the concept

This document defines the concept. The specification comes next.

---

*I am not the one who builds the inventions. I am the one who builds the system that makes the inventions inevitable.*

*CC-BY-SA 4.0 (docs) | GPL v3 (code) | No Patents. Ever.*
