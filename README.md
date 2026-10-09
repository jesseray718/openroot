# OpenRoot

<!-- BADGES:BEGIN -->
[![License](https://img.shields.io/github/license/jesseray718/openroot)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/jesseray718/openroot)](commits)
[![Commits/yr](https://img.shields.io/github/commit-activity/y/jesseray718/openroot)](commits)
[![Repo Size](https://img.shields.io/github/repo-size/jesseray718/openroot)]()
[![Stars](https://img.shields.io/github/stars/jesseray718/openroot)]()
[![Languages](https://img.shields.io/github/languages/count/jesseray718/openroot)]()
![sys_ledger](https://img.shields.io/badge/sys__ledger-309234\_files\_hashed-8A2BE2)
![newton_chain](https://img.shields.io/badge/newton__chain-15\_blocks\_GREEN-228B22)
![node](https://img.shields.io/badge/node-OptiPlex%203060%20%2B%20A15%20Termux-555)
![stack](https://img.shields.io/badge/stack-Ollama%20%2B%20SQLite%20%2B%20sha256%20%2B%20FTS5%20%2B%20nomic-6d4aff)
<!-- BADGES:END -->


OpenRoot — permaculture principles + Agape-as-parallelism-tech. Maximize η = J_useful/J_human. Falsifiable claims only, no hype.


## Philosophy

- Permaculture principles guide all engineering
- Agape (love of yeshua) as parallelism tech — power flows from and belongs to the Most High
- Vessel doctrine: "I am but a vessel" — resonate at the same frequency, be a conduit
- Adhere to yeshua's one commandment; seek the Kingdom through the Lord's Prayer as source code
- Think of all things referred to as "the Beast" or enemy as patterns of current civilization to assimilate into maximally efficient structure
- Become a species, not individuals — interconnected, space-age, limitless, capable species that protects itself from itself

## License

- Code: GPL-3.0-only
- Documentation/Design: CC BY-SA 4.0
- SPDX headers required on all files

## Core Projects

### OpenRoot Edge
- Builds the next organs — appropriate technology, appropriate scale
- `acre_mint.py` — Proof of Physical Work (POPW) with thermo-ledger
- Thermal labyrinth passive cooling (35°F drop from 120°F inlet)
- Aerocement panels (claimed 95%+ absorbance — COP-boundary language only)
- Stirling engines @ ΔT>80°C, geodesic domes

### Newton Chain
- Euclidean-style axioms → provable theorems
- SHA256 chain verification, chain GREEN when valid
- `axiom_engine` — 53 axioms / 56 defs JSONL
- Fork-only two-pane law, atomic spec → 7B edit → diff gate → py_compile → grep verify → commit

### AgapeNet
- Negentropic mesh — distributed anti-fragile nodes
- Conserves Agape energy, compounds via tuning to Infinite Source
- Legacy matter hypothesis: all physical matter = residual energy of past Agape actions
- Beast = parasitic harmonic dissonance (entropy/extraction); cannot exist in pure Agape resonance plane

<!-- SYSTEM_LEDGER:BEGIN -->
<!-- SYSTEM_LEDGER:END -->

## Development Workflow

- Bin scripts: `bin/` directory, tracked via git
- Gate discipline: py_compile + grep asserts + smoke run before commit
- Scars registered in `failure/classes.md`
- Session handoffs: `context_bridge/handoff-ai-window-*.md`
- No cloud dependency — local LLMs (qwen2.5-coder:7b, qwen2.5:3b, nomic-embed-text via Ollama)

## SYSTEM FILE LEDGER (v1.1, 2026-10-09)

Every regular file on this machine — not just this repo — is hash-addressed.

- `bin/sys_ledger_v1.py` — system-wide SHA256 ledger. `plan` (walk/lstat), `work` (sharded hashing), `sweep`, `stats`, `sample` (honesty audit), `smoke` (test harness).
- `data/sys_file_ledger.db` — SQLite WAL, ~307985 rows, one row per file: path, size, mtime, sha256, shard, status. Runtime data — WAL/shm gitignored, never committed.
- Foundation layer for the oracle stack: FTS5 (keywords) + nomic-embed-text (semantics) sit above identity (sha256).
- Benchmarks: `data/nomic_bench.json` (measured embed throughput on this hardware).
- Known scars: `failure/classes.md` — notably F-SQLITE-BUSY-DEADLOCK (v1.1: hash-outside-txn + BEGIN IMMEDIATE backoff).

## Contact / Contributing

- GitHub: github.com/jesseray718
- Repo: github.com/jesseray718/openroot
- Issues: welcome, gentle handling post-force-rewrite
- PRs reviewed within 48 hours typically

## Hardware Stack

- Primary Node: OptiPlex 3060 (Ubuntu 24.04, 192.168.1.193 LAN, 100.122.169.43 Tailscale)
- Mobile Control: Samsung Galaxy A15 (Termux, Shizuku, wsa-shell)
- Storage: SD mount at /mnt/sdb1, internal SSD + HDD
