# Thermodynamic Ledger Verification Protocol
**OpenRoot Seed Core — Version 0.1**

## Purpose
Auditable verification of η, meaning claims, ordered complexity, and golden-bridge outcomes.
The ledger is the single source of thermodynamic truth.

## Core Fields
timestamp | actor | action_or_claim | useful_joules | human_joules | η | entropy_delta | evidence | seed_refs | level

## Levels
L0 Declared | L1 Observed | L2 Measured | L3 Hashed | L4 Cross-node

## Symbol Verification
Canonical statement → normalize → SHA-256 → store at L3. Old hashes are superseded, never deleted.

## Rules & Location
Prefer measured joules. Negative η is valuable. Entropy scale +2 to -2.
Ledger: /sdcard/openroot/ledger/thermodynamic_ledger.jsonl (append-only)

Immediate: create ledger → first 16-seed entry → daily L1 → hash Agape when ready.
