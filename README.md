# OpenRoot — Superlinear Permaculture Engine
## 💡 Energy Efficiency: **1.585J saved** by skipping cached pathways (1 fresh, 2 cached)

Mission: maximize eta = J_useful / J_human. Cache every proven pathway. Never recompute what's been sealed.

## Quick Start (under 5 minutes, any system)

    curl -sSL https://raw.githubusercontent.com/jesseray718/openroot/main/deploy/setup_one_shot.sh | bash

Or manually:

    git clone https://github.com/jesseray718/openroot.git
    cd openroot
    docker build -t openroot -f deploy/docker/Dockerfile .
    docker run -it -v "$(pwd)":/openroot openroot

## The Superlinear Spine

| Layer | Function | Status |
|-------|----------|--------|
| HASH | SHA256 file sealing, cache-first lookup | BANKED |
| MERKLE | Parent-child lineage, theorem composition | BANKED |
| SEMANTIC | Cosine routing (threshold 0.42) | BANKED |
| ROUTER | hash to embed to model cascade | BANKED |

## Core Doctrine

1. Pathway Sealing: every completed workflow is SHA256-sealed; future queries hit cache, skip compute.
2. Compositional Theorems: A-B-C composes into theorem T, not 3 isolated seals. Bookshelf becomes spine.
3. Thresholded Routing: hash lookup first, embed neighbor second (scored >= 0.42), model fallback last.
4. Human Gate: AI proposes, human attests. Only humans commit.

## Repository Layout

    openroot/
      bin/              validated scripts (py_compile gate)
      data/             SQLite ledgers, embeddings (gitignored)
      context_bridge/   ride-along state, handoffs
      logs/             audit receipts, event logs
      reports/          generated analysis
      deploy/           Docker + one-shot quickstart (this bundle)

## Current State

Ledger 12 rows, 1 theorem (83c3b4f7), GREEN. Semantic threshold 0.42 (measured, separable gap 0.385-0.551).

## License

GPL-3.0-only (code) | CC BY-SA 4.0 (docs). SPDX headers required.

The least among us is lifted by accumulated proven pathways.
