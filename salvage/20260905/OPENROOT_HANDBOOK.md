# OpenRoot Living Context Handbook
**Last updated:** 2026-08-19
**Purpose:** Single entry point for navigation, commands, scanning, and connecting dots.

## 1. Core Loop (use these daily)

- See everything: `/data/data/com.termux/files/home/bin/openroot-run list`
- Full inventory: `/data/data/com.termux/files/home/bin/openroot-run inventory`
- Current status: `/data/data/com.termux/files/home/bin/openroot-run status`
- List seeds: `/data/data/com.termux/files/home/bin/openroot-run seeds`
- Seed graph: `/data/data/com.termux/files/home/bin/openroot-run seed-index`
- All LATTICE.md pointers: `/data/data/com.termux/files/home/bin/openroot-run lattice-pointers`

## 2. Keyword Scan (Connect the Dots)

`/data/data/com.termux/files/home/bin/openroot-keyword-scan <word or phrase>`

High-value examples:
- openroot-keyword-scan synergetic
- openroot-keyword-scan "R=1.0"
- openroot-keyword-scan resonance
- openroot-keyword-scan "zero coordination"
- openroot-keyword-scan handbook
- openroot-keyword-scan lattice
- openroot-keyword-scan aerated
- openroot-keyword-scan "closest packing"
- openroot-keyword-scan gfrc

## 3. Important Paths

- Handbook: `/sdcard/openroot/OPENROOT_HANDBOOK.md`
- Seeds: `/sdcard/openroot/context_bridge/seeds/`
- Seed index: `/sdcard/openroot/context_bridge/seed-index.json`
- Lattice pointers: `/sdcard/openroot/context_bridge/lattice-pointers.txt`
- Inner window: `/sdcard/openroot/context_bridge/INNER_WINDOW_AI_PROVIDER.md`
- Material seed: `/sdcard/openroot/context_bridge/seeds/aerated_gfrc_closest_packing.json`

## 4. Core Material Seed — Aerated Thixotropic GFRC

**ID:** AERO-GFRC-001

Stator-mixed, surfactant-gel-controlled open-cell aerated GFRC that drives bubble size downward and bubble count upward toward densest sphere packing. The cement matrix works in pure compression while air voids remain discrete.

Why it is foundational:
- High strength-to-weight with local materials only
- Passive thermal performance
- Fully open-source and patent-free
- Enables cast or 3D-printable appliances, thermal mass, structural elements, and tools
- Designed for the lowest-capability node

Related concepts: AeroCement, Black Locust thermal cascade, open-cell thermal systems, Synergetic Calculus, 3D-printable open-source hardware library.

## 5. Tips

1. Start every session with openroot-run list
2. Use keyword-scan before inventing something new
3. Prefer small pure seeds
4. Absolute paths only
5. After changes → inventory then seed-index

η = useful_joules / human_joules
R = 1.0 → C = 0
