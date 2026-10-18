# OpenRoot

**Verifiable local autonomy. Sealed evidence, measured energy, auditable actions, physical work receipts.**

OpenRoot is a decentralized, open-source framework for civilizational regeneration based on permaculture principles, fractal mesh geometry, contribution economics, and direct work attestation. It replaces multiple layers of wealth extraction with community-owned systems that reward building, care, and productive work.

## Receipt chain

```
v1.0 (genesis):       a5a988e5879eb4f2ce14aadc0c72ae29eded0987b0c3ca9fcf4eeb9cacf5a889
  sealed:              2026-10-18T09:21:54Z
  documents:           14 founding docs
  signed by:           Ed25519 (genesis/genesis_ed25519.pub)

v1.1 (theorem reg):   11f7934c5c1e42ca9303e939bae26425b905c186aa634190d63304092a5bfc57
  sealed:              2026-10-18T11:49:28Z
  parent:              a5a988e5... (v1.0)
  theorems registered: 3
  merkle_root:         d2bba4608f35596b50f62ec34a0fa254a2765d0c154daaafff3b46f882d4c387
  formal proofs:       pending v1.2
```

## Independent verification

```bash
git clone https://github.com/jesseray718/openroot
cd openroot
# Verify v1.0 genesis:
openssl pkeyutl -verify -pubin -inkey genesis/genesis_ed25519.pub -rawin \
  -in <(python3 -c 'import json; r=json.load(open("genesis/receipt_v1.json")); print(json.dumps(r,sort_keys=True,separators=(",",":"),ensure_ascii=False),end="")') \
  -sigfile genesis/receipt_v1.sig
# Verify v1.1 theorem registry:
openssl pkeyutl -verify -pubin -inkey genesis/genesis_ed25519.pub -rawin \
  -in <(python3 -c 'import json; r=json.load(open("genesis/receipt_v1_1.json")); print(json.dumps(r,sort_keys=True,separators=(",",":"),ensure_ascii=False),end="")') \
  -sigfile genesis/receipt_v1_1.sig
```

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

- **Genesis v1.0:** sealed 2026-10-18T09:21:54Z (14 founding docs)
- **Theorem registry v1.1:** sealed 2026-10-18T11:49:28Z (3 theorems registered)
- **Court v6:** daily sealed receipts (patches: `${TS}→`${STAMP}` fix `06e21cc` + tee redirect `d4ee143`).
- **Heartbeat mesh:** 15-min cycle, live.
- **Newton chain:** live (axiom ledger).
- **Mistake compost:** 14 scars banked.
- **Smart contract:** Solana ACRE token + Contribution Ledger (live, CI green).
- **Formal theorem proofs:** pending — v1.2 receipt.

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
