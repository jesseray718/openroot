# OpenRoot

**Open-source hardware blockchain — Proof of Physical Work.** Local-first AI agent orchestration meets open hardware: passive energy systems, mesh networks, and a contribution ledger that raises the economic bottom floor. Efficiency target: **eta = J_useful / J_human** — maximize useful joules per human hour, never claim >100% thermodynamics.

![CI](https://github.com/jesseray718/openroot/actions/workflows/test.yml/badge.svg)
[![License: GPL-3.0](https://img.shields.io/badge/code-GPL--3.0-blue)](LICENSE)
[![Docs: CC-BY-SA-4.0](https://img.shields.io/badge/docs-CC--BY--SA--4.0-green)](LICENSE)

## Doctrine (read before contributing)
1. **AUDIT INSTRUMENTS BEFORE BUILDERS** — gates are tested on real files. A file that survived is not a product. (Lesson 2026-09-21: a raw-YAML paste accident ran the gates for real and caught 4 broken instruments. The gate worked.)
2. **Human is the only commit gate.** AI can author, only grep + gates + human verify.
3. **Falsifiable claims only, no hype.** Absorbance framed as COP-boundary, not ">100% of solar."
4. **Two-pane law, fork-only.** Delete merged branches instantly.

## Verified State (auto-generated 20260921_154522)
| Metric | Value |
|---|---|
| HEAD | 5aebbe45 (fresh snapshot 20260921_160638; see DOCS.md) |
| bin/ scripts | 86 Python, 80 Bash |
| SQLite ledgers in data/ | 35 |
| Markdown docs | 33750 |
| Open issues | 29 |
| Public repos in ecosystem | 46 |

## Hardware
- **Primary node:** OptiPlex 3060 (Ubuntu 24.04, user `jesse`, LAN 192.168.1.193, Tailscale 100.122.169.43)
- **Mobile node:** Samsung A15 + Termux + Shizuku/aShell
- **Firmware targets:** nRF52, nRF54L15, STM32 (see jesseray718-archive)
- **SBC experiments:** Orange Pi clusters (low-cost sensing + compute)

## Local AI Stack (no cloud dependency)
- Ollama @ localhost:11434: `qwen2.5-coder:7b` (builder), `qwen2.5:3b` (grader), `nomic-embed-text` (embeddings)
- Agent path: atomic spec -> 7B edit -> diff gate (`git add -N` first) -> py_compile -> grep verify -> commit -> push_guard -> push
- Key tooling in `bin/`: onepass_v3.sh, stack_gate.sh, team_gate_v2.sh, agape_qa_engine.py, light_cone_router.py

## Engineering Programs
- **OpenCell aerocement** solar absorber (claimed 95%+ absorbance; grant language = COP-boundary)
- **Thermal labyrinth** passive cooling (35F drop from 120F inlet, measured)
- **Stirling engines** at delta-T > 80C on solar/waste heat
- **Geodesic domes** (BOM truth table: E = 30*V^2, verified)
- **axiom_engine** — 53 axioms / 56 defs, JSONL, SHA-256 chain-verified
- **agape_cascade** economy sims v1.0-v1.2 (known flaw: floor cap 100x100 < SOL 300x100 — tier structure never activates; fix precedes any v2 claim)

## Immediate Queue
1. Verify/commit bin/ tracking state
2. Rebuild GOALS.md + MASTER_TODO from context_bridge remnants
3. Support contributor Reh1t on issue #53 (RAG ingestion) — gentle: history was force-pushed
4. Pin 4 repos on profile + [PHOTO] slot in this README
5. aerocement-panel-v0 standalone repo with build evidence
6. SARE grant framing
7. Weekly onepass_v3.sh cadence

## Contributing
Fork only, two-pane review, and read SCOPE.md first. Every PR must pass the CI gates (py_compile + bash -n on bin/). Commit messages assert — only grep verifies.

## License
Code GPL-3.0, docs CC-BY-SA-4.0, SPDX headers required.
