# Identity.py — Cycle-004 Contribution Notes
Date: 2026-08-13

## Core observations
- KEYSIZE = 512 bits (256 X25519 + 256 Ed25519)
- TRUNCATED_HASHLENGTH is non-configurable (comes from RNS.Reticulum)
- known_destinations is an in-memory dict protected by known_destinations_lock
- Entries are 5-tuples: [timestamp, packet_hash, public_key, app_data, last_used]
- save_known_destinations skips work if connected to a shared instance
- to_file / from_file write raw private key bytes (no encryption of the key file itself)

## Constrained-node implications
- Key material is small and clean — good for low-RAM nodes
- Persistence is simple but assumes reliable local storage
- Shared-instance guard is already present (important for multi-process / low-resource hosts)
- No explicit documentation of behaviour under extreme intermittency or very small storage

## First contribution candidate
Improve documentation in Identity class and Contributing.md / docs for:
1. Exact key sizes and format expectations
2. Behaviour of known_destinations under shared instances
3. Guidance for lowest-node / intermittent deployments (chicken-wire spokes)

Keep changes documentation-only for the first PR. Code changes only after that lands.
