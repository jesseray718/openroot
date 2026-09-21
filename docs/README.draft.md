# OpenRoot — The Thermodynamic Commons

**A self-sustaining network leveraging physical infrastructure and computational swarm to maximize thermal, material, and food yield while minimizing waste.**

> η = useful_joules / human_joules  
> Every cycle must close on real thermal, material, or food yield.

---

## Status Badges

[![Proof of Physical Work](https://img.shields.io/badge/PoPW-8.13M%20ACRE-brightgreen?style=flat-square&logo=bitcoin)]  
[![Thermal Ledger](https://img.shields.io/badge/Thermal%20Ledger-12.91%20kWh/m²%2Fnight-blue?style=flat-square&logo=thermal)]  
[![Zenodo](https://img.shields.io/badge/Zenodo-10.5281/zenodo.21225683-589632?style=flat-square&logo=zenodo)]  
[![License GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-orange?style=flat-square&logo=gnu)]  
[![ACRE Token](https://img.shields.io/badge/ACRE-16.27M%20cumulative-purple?style=flat-square&logo=solana)]  
[![Bitcoin Anchor](https://img.shields.io/badge/Bitcoin%20Anchor-3%20confirmed-black?style=flat-square&logo=bitcoin)]  
[![IPFS](https://img.shields.io/badge/IPFS-4%20CIDs%20pinned-ff5500?style=flat-square&logo=ipfs)]  
[![Last Commit](https://img.shields.io/github/last-commit/jesseray718/openroot?style=flat-square)]

---

## Getting Started

### Install
```bash
git clone https://github.com/jesseray718/openroot.git
cd openroot/bin
./setup.sh
```

### Architecture
- **Agent Loop:** Orchestrates the lifecycle of nodes, handling tasks and energy optimization.
- **Gates:** Controls access to resources based on authentication and authorization.
- **Mistake Ledger:** Tracks errors and provides a mechanism for correcting mistakes.
- **Non-Recompute Cache:** Stores results of expensive computations to avoid redundancy.

### Contribution Workflow
Contributions are reviewed by human gatekeepers before being merged into the main repository.

---

## How It Works

OpenRoot leverages the `lb_loop` 21-cached-passes proof to ensure that each computational cycle is optimized for energy efficiency and minimal waste. This proof is a key component of our thermodynamic ledger, which tracks every joule of useful work performed by the network.

---

## The Four Engines

| Engine | Purpose | Live Components |
|--------|---------|-----------------|
| **Knowledge** | Axioms, postulates, governance | 7 physics axioms, fractal constitution |
| **Energy** | Passive solar-thermal, storage | Black Locust coppice + RMH, H-003 thermal cascade |
| **Material** | Shelter, water, food | Aerated GFRC panels, ferrocement domes, aquaponics |
| **Finance** | Credit-building, ACRE token | PRF-001 routing, PoWr minting, thermodynamic ledger |

The permaculture principle at the core of OpenRoot is that each engine serves multiple functions. Each node generates surplus, and nothing is extracted or wasted.

---

## The Floor-Lift Economy

**The spread between top and bottom is a speed limit on compound human growth.**

Utility of a delivered benefit scales with (1 − recipient_percentile)² — the same artifact routed to the bottom decile carries ~25x the systemic value weight of routing it to the top decile. Routing beats volume.

**Verified demo** (contribution_tier_v2.py, ids d1579005 vs 50c984a5): floor_lift 67.05 bottom-routed vs 2.5 premium-routed — identical 100 units of aggregate benefit, 26x systemic value gap.

| Tool | Function |
|------|----------|
| `bin/contribution_tier_v2.py` | Bottom-floor weighted grading, FLOOR_LIFT as primary metric |
| `bin/openrouter_client_v1.py` | Live API tier routing under a $0.50 hard spend cap |
| `bin/tier_dispatch_v1.py` | 5-tier escalator, hash-idempotent queue |

**Release:** v2026.09.20-floorlift  
**Milestone:** 6 open  
**Quadratic exponent is a falsifiable hypothesis (agape_cascade validation pending)**.

---

## Hardware We're Building

### ① AeroCement H-003 Thermal Cascade
- **Volumetric blackbody concrete** — 95%+ solar absorption
- **Passive stack-effect circulation** — no pumps
- **Subterranean thermal storage** — 35°F cooling from 120°F inlet
- **Target:** 12.91 kWh/m² nightly capture (validated simulation)
- **Status:** Simulation complete, physical prototype needed

### ② Black Locust Coppice + Rocket Mass Heater
- **Carbon-negative forestry** — roots sequester while tops are burned
- **85-95% combustion efficiency** vs 50-70% conventional stoves
- **12-24 hour thermal mass storage** — one burn cycle heats a day
- **η multiplier:** 75-100× over traditional firewood processing

### ③ Ferrocement Dome Panels
- **Bolt-together modular** — LEGO-like assembly
- **Hurricane/earthquake/fire resistant**
- **Single-material structure** — walls + insulation + foundation
- **Drill-and-bucket buildable** — no industrial equipment

### ④ Offline Mesh Node
- **Recycled hardware** — phones, routers, mini PCs
- **Offline LLMs** — Ollama/llama.cpp, no cloud dependency
- **Long-range mesh radios** — comms that cannot be shut off
- **Energy independent** — solar-powered, battery-buffered

---

## Thermodynamic Ledger

The thermodynamic ledger proves every claim with measurable joules:

| Component | Status | Proof |
|-----------|--------|-------|
| Merkle audit trail | ✅ Live | `audit_trail.jsonl` → 32-byte root |
| Bitcoin-anchored snapshots | ✅ Confirmed | 3 OpenTimestamps on Bitcoin blockchain |
| Landauer + E=mc² bridge | ✅ Working | 256 bits → 7.36e-19 J → 8.19e-36 kg |
| ARM energy measurement | ✅ Live | CPU freq scaling → joule estimation |

---

## Community

OpenRoot is an open-source project governed by the community. Please refer to our [Code of Conduct](./CODE_OF_CONDUCT.md) for guidelines on how we treat each other.

If you are interested in contributing, please review our [contribution guidelines](https://github.com/jesseray718/openroot/blob/main/CONTRIBUTING.md).

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](./LICENSE) file for details.

---

Join us in building a sustainable future, one joule at a time!