# OpenRoot

**Verifiable local autonomy. Sealed evidence, measured energy, auditable actions, physical work receipts.**

OpenRoot is a decentralized, open-source framework for civilizational regeneration based on permaculture principles, fractal mesh geometry, contribution economics, and direct work attestation. It replaces multiple layers of wealth extraction with community-owned systems that reward building, care, and productive work.

## Genesis receipt (v1.0 — canonical)

```
receipt_id:  5a64fcac7301728782448e5afeb7690e7173fdc3a93096dbb85d1e307bdf4b0b
timestamp:   2026-10-18T10:43:46Z
documents:   14 founding docs
supersedes:   receipt_v0 (partial, 4 docs)
signed by:   Ed25519 (genesis/genesis_ed25519.pub)
verify with: openssl pkeyutl -verify -pubin -inkey genesis/genesis_ed25519.pub -rawin -in <canonical> -sigfile genesis/receipt_v1.sig
```

This is the canonical founding artifact. Every future receipt chains from this. Theorems marked proof-pending will be sealed in v1.1 receipt.

## Founding corpus (14 documents)

| # | Document | Layer |
|---|---|---|
| 01 | Trillion Dollar Redirect | Economics |
| 02 | Full Systemic Reallocation Model | Economics |
| 03 | Combined Telecom-Energy Reallocation | Economics |
| 04 | Global Fractal Mesh Framework (Cloud 9 canonical) | Mesh |
| 05 | Societal Transformation | Vision |
| 06 | Aerocement Whitepaper v1.0 | Energy |
| 07 | Aerocement Defensive Publication | IP |
| 08 | Human Continuity Master v1.0 | Resilience |
| 09 | OpenRoot Lumo Context Bridge | Project |
| 10 | Axioms (Euclidean taxonomy, theorems marked) | Foundation |
| 11 | AX-039 Absolute Protection (Shield Law) | Governance |
| 12 | Newton Chain Kingdom Engine | Governance |
| 13 | 12 Agape Formalized | Governance |
| 14 | ACRE Specification | Token economics |

## Status (as of 2026-10-18)

- **Genesis receipt v1.0:** SEALED 2026-10-18T10:43:46Z
- **Court v6:** daily sealed receipts (patches: `${TS}→`${STAMP}` fix `06e21cc` + tee redirect `d4ee143`).
- **Heartbeat mesh:** 15-min cycle, live.
- **Newton chain:** live (axiom ledger).
- **Mistake compost:** 14 scars banked.
- **Smart contract:** Solana ACRE token + Contribution Ledger (live, CI green).
- **Worker layer:** pending — next major arc.
- **Theorem proofs:** pending — v1.1 receipt.

## Doctrine

- **The receipt is the constitution.** Every action either chains from the genesis or doesn't.
- **Verifiers are pure code.** Models propose. Code disposes. No exceptions.
- **Receipts are canonical, independently verifiable.** Stdlib + openssl only.
- **Act as One Human Family.** Cut what harms. Grow what heals.

## License

- Documentation: CC-BY-SA 4.0
- Code: GPL v3
- Aerocement hardware: CERN-OHL-S v2 (pending license refactor)

---
One Human Family. Build what serves. Track transparently. Reward contribution and care.
