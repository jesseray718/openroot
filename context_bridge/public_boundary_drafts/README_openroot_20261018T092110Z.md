# OpenRoot

**Verifiable local autonomy. Sealed evidence, measured energy, auditable actions, physical work receipts.**

OpenRoot is a decentralized, open-source framework for civilizational regeneration based on permaculture principles, fractal mesh geometry, contribution economics, and direct work attestation. It replaces multiple layers of wealth extraction with community-owned systems that reward building, care, and productive work.

## Genesis receipt

```
receipt_id:  f753d4c6844a0814d685d7dcb867c5911566206340cdd15a0549a8597012f856
timestamp:   2026-10-18T09:21:54Z
signed by:   Ed25519 (genesis/genesis_ed25519.pub)
verify with: openssl pkeyutl -verify -pubin -inkey genesis/genesis_ed25519.pub -rawin -in <canonical> -sigfile genesis/receipt_v0.sig
```

This is receipt #1. Every future receipt chains from this.

## Status (as of 2026-10-18)

- **Genesis receipt:** SEALED 2026-10-18T09:21:54Z
- **Court v6:** daily sealed receipts (report + log + sha256 anchors). Two patches landed: `${TS}→`${STAMP}` fix (`06e21cc`) + tee redirect for real log bytes (`d4ee143`).
- **Heartbeat mesh:** 15-min cycle, live.
- **Newton chain:** live (axiom ledger).
- **Mistake compost:** 14 scars banked.
- **Lumo ingest:** live.
- **Mesh dossier engine:** live (cached).
- **Smart contract:** Solana ACRE token + Contribution Ledger (live, CI green).
- **Worker layer:** pending — next major arc after court calibration.

## Core subsystems

| Subsystem | Status | Receipt class |
|---|---|---|
| Genesis receipt | sealed | founding |
| Court v6 (adversarial evidence) | production | daily sealed |
| Heartbeat mesh (15-min cycle) | live | incremental |
| Newton chain (axiom ledger) | live | sealed per event |
| Mistake compost | live (14 scars banked) | per-mistake |
| Lumo ingest bridge | live | per-ingest |
| Mesh dossier engine | live (cached) | per-event |
| Worker layer | pending | per-action |

## Court v6 — first production sealed receipt

Daily 04:00 CDT. Defense (`qwen2.5-coder:7b`) vs Prosecution (`qwen2.5:3b`). FTS5 evidence corpus (49 excerpts). Every run produces:

- `context_bridge/court-v6-report-{stamp}.md` — verdicts and reasoning.
- `logs/court_v6_{stamp}.log` — full session log, tee'd from stdout/stderr.
- `sha256sum` seal on both — anchors real bytes.

Current backlog: `fail|13 hold|36 pass|0` (49 verdicts, 0% pass rate). Calibration audit in progress — see `context_bridge/court_audit/`.

## Doctrine

- **The receipt is the constitution.** Every action either chains from the genesis or doesn't.
- **Verifiers are pure code.** Models propose. Code disposes. No exceptions.
- **Receipts are canonical, independently verifiable.** Stdlib + openssl only.
- **Act as One Human Family.** Cut what harms. Grow what heals.

## License

- Documentation: CC-BY-SA 4.0
- Code: GPL v3
- Aerocement hardware: CERN-OHL-S v2 (pending license refactor)

## Links

- [Aerocement whitepaper](https://github.com/jesseray718/aerocement)
- [jesseray718 GitHub profile](https://github.com/jesseray718)

---
One Human Family. Build what serves. Track transparently. Reward contribution and care.
