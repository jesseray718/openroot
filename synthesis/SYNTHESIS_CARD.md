# OpenRoot Synthesis Card — read this first in any new window

## Bigger vision
Offline-first appropriate-tech mesh: ferrocement/opencell energy nodes, Carnot-verified
thermal accounting, and a homemade SHA-256 blockchain that makes every contribution
provably credited. Physical yield (cooling joules, water, storage) becomes on-chain
value via ACRE tokens (Proof of Physical Work), priced through a bounty board settled
in STEP. Goal: energy sovereignty for grid-excluded populations, monetized through
grants + DePIN rails, owned by the contributors who hash-linked the work.

## Concepts (all live under synthesis/)
- **Contributions blockchain** — db/synthesis.db `chain` table; each block = sha256(prev|kind|payload).
  Credit is provable: verify with `synthesis.py verify` (GREEN = intact).
- **Capability registry** — every callable scanned from bin/, tools/, acre/, une/, workflows/,
  graded MEASURED / MODEL / STUB / CONFLICT (honesty system: nothing asserted above its grade).
- **Modular tidbits** — small self-contained scripts (<120 lines, hashed) in `tidbits` table;
  candidates for reuse and recombination.
- **Synergy combos** — every capability pair tested for compounding yield (cross-domain
  pairs get a coupling bonus). Top pairs are the cheapest next moves.
- **PoPW + thermal ledger** — joule events feed ACRE attestations; mints are REFUSED unless
  grade == MEASURED (Anchor stub enforces, contracts/acre_attest.rs).
- **Bounty board** — capabilities priced in ACRE; filling a bounty means pushing its
  capability up the grade ladder, which mints real credit.
- **Grants** — cluster drafts in synthesis/grants/, generated from the capability table,
  clearly marked DRAFT until claims are MEASURED.

## Rules for any AI node touching this
1. Append-only: never mutate chain rows or seals; add new blocks instead.
2. No claim without a grade; never upgrade a grade without verification evidence.
3. Yield question for every action: most output per human joule — check `intake` ranking first.
