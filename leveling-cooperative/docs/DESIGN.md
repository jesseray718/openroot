# Design: Autonomous Leveling Cooperative

## Goal
Turn many small investments from people with thin or damaged credit into a collective engine that raises the floor for everyone, while returning dividends and directing surplus to highest-need members.

## What members put in
- Capital only (USD or local equivalent recorded as units)
- Optional: anonymized need score (self-declared or community-attested)
- They do **not** put their full credit profile or SSN into the pool

## What the pool does
1. Accepts investments into a transparent ledger
2. Compounds according to simple, published rules
3. Calculates decision coefficients via local nanobot hive
4. Pays dividends proportional to contribution + time
5. Routes a fixed % of surplus to the highest need-coefficient members (hand-up)
6. Never has an owner or preferred class

## Nanobot Hive (Decision Coefficient)

need_score          = 0.0 – 1.0   (higher = more need)
contribution_weight = log(1 + total_invested)
time_weight         = months_in_pool / 12
η_factor            = useful_output / human_input

decision_coefficient = (need_score * 0.45) + (contribution_weight * 0.25) + (time_weight * 0.15) + (η_factor * 0.15)

Hand-up allocation is sorted by decision_coefficient descending.

## Ledger
JSONL append-only + periodic Merkle root (same pattern as ACRE / thermodynamic ledger).

## Autonomy Rules (hard-coded)
- No human can change the hand-up percentage without ledger consensus
- No extraction to any external corporate entity
- All code and rules are public and forkable

## Zero-dependency runtime
- Pure bash + python3 standard library only
- No pip, no network required for core operation
