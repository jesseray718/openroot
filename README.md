# OpenRoot

**Open-source hardware blockchain — Proof of Physical Work.** Local-first AI agent orchestration meets open hardware: passive energy systems, mesh networks, and a contribution ledger that raises the economic bottom floor. Efficiency target: **eta = J_useful / J_human** — never claim >100% thermodynamics.

[![Release v1.0.0](https://img.shields.io/badge/release-v1.0.0-6d4aff)](https://github.com/jesseray718/openroot/tree/8a012b2a)
![CI](https://github.com/jesseray718/openroot/actions/workflows/test.yml/badge.svg)
[![License: GPL-3.0](https://img.shields.io/badge/code-GPL--3.0-blue)](LICENSE)
[![Docs: CC-BY-SA-4.0](https://img.shields.io/badge/docs-CC--BY--SA--4.0-green)](LICENSE)

## 📷 Proof of Physical Work
<!-- [PHOTO] Insert build-evidence photo here: aerocement sample, thermal labyrinth test rig, or dome frame.
     Recommended: docs/img/popw-hero.jpg — photo is the badge for hardware projects. -->

## Doctrine (read before contributing)
1. **AUDIT INSTRUMENTS BEFORE BUILDERS** — gates test on real files. A file that survived is not a product.
2. **Human is the only commit gate.** AI authors; only grep + gates + human verify.
3. **Falsifiable claims only, no hype.** Absorbance framed as COP-boundary, never ">100% of solar."
4. **Two-pane law, fork-only.** Delete merged branches instantly.

## Verified State (snapshot 20260921_162046)
| Metric | Value |
|---|---|
| HEAD | a1ea652a (= origin/main, CI green) |
| Latest release | v1.0.0 — Public Launch |
| bin/ instruments | 172 tracked, all py_compile + bash -n green |
| Roadmap | GOALS.md + MASTER_TODO.md (rebuilt 2026-09-21) |

## Hardware
- **Primary node:** OptiPlex 3060 (Ubuntu 24.04, user `jesse`, LAN 192.168.1.193, Tailscale 100.122.169.43)
- **Mobile node:** Samsung A15 + Termux + Shizuku/aShell
- **Firmware targets:** nRF52, nRF54L15, STM32 · SBC experiments: Orange Pi clusters

## Local AI Stack (no cloud dependency)
Ollama @ localhost:11434 — `qwen2.5-coder:7b` (builder), `qwen2.5:3b` (grader), `nomic-embed-text` (embeddings).
Agent path: atomic spec → 7B edit → diff gate → py_compile → grep verify → human-gated commit → push_guard → push.

## Engineering Programs
- **OpenCell aerocement** solar absorber (95%+ claimed absorbance; COP-boundary framing)
- **Thermal labyrinth** passive cooling (35°F drop from 120°F inlet, measured)
- **Stirling engines** at ΔT > 80°C on solar/waste heat
- **Geodesic domes** (E = 30·V² BOM truth table, verified)
- **axiom_engine** — 53 axioms / 56 defs, JSONL, SHA-256 chain-verified
- **agape_cascade** economy sims (known floor-cap flaw, fix precedes v2 claims)

## Contributing
Fork only, two-pane review, read SCOPE.md first. Every PR must pass the CI gates. Commit messages assert — only grep verifies. See [releases](https://github.com/jesseray718/openroot/tree/8a012b2a) for the changelog.

## License
Code GPL-3.0 · Docs CC-BY-SA-4.0 · SPDX headers required.
