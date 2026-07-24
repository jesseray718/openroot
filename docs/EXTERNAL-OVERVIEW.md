# EXTERNAL-OVERVIEW.md — OpenRoot High-Density Brief + Status Matrix v1

**Node:** GROK-NODE | **Date:** 2026-07-17 | **Purpose:** Onboarding clarity + maximum systemic benefit per contributor effort. Addresses fragmented entry points + missing maturity dashboard.

**Status Matrix** (new — surfaces marginal leverage; every subsystem now has explicit maturity + next physical gate + ACRE path):

| Subsystem                        | Maturity                  | Evidence / Last Update              | Next Physical Gate                  | ACRE Eligible?          |
|----------------------------------|---------------------------|-------------------------------------|-------------------------------------|-------------------------|
| Philosophy / Axioms / UNE        | Active (v0.2)            | 2026-07-17 tagger + resolver deploy | Validator handbook v1              | Yes (tooling)          |
| H-003 Thermal Cascade (AE-GFRC)  | Theoretical v2 + harness | 2026-07-17 hypothesis rev + harness | BUILD-001 first pour + sensor log  | Yes (first climate node) |
| ACRE Token                       | Conceptual               | Solana integration + tagger v0.2   | Testnet mint + 2-validator flow    | N/A (core primitive)   |
| Credit Path (PRF-001)            | Actionable               | Checklists + formal proof          | Execute $50 Kikoff/Varo path       | Indirect (enables)     |
| AEGIS MESH / Comms               | Templates + deploy       | Agape v0.1.0 + UNE integration     | Sikeston I-55/I-57 kiosk node      | Yes (first spoke)      |
| Shelter (ferrocement/AE-GFRC)    | Conceptual               | Specs in aerocement/               | First panel test pour              | Yes                    |
| Food/Water Permaculture          | Conceptual               | Black locust + aquaponics sketches | First living system install        | Yes                    |
| Tools / Kai / Scripts            | Active                   | slump-brain, status.sh, compute/n0 | Profile + auto-start on Node Zero  | Yes (efficiency tools) |

**Hard Rule:** Physical validation (BUILD-001 data) is the non-negotiable gate for all ACRE claims on H-003 metrics. All thermal numbers remain defensive publication until logged.

---

**OpenRoot** (github.com/jesseray718/openroot) is an ambitious, solo-founded open-source ecosystem for appropriate technology and regenerative civilization infrastructure. Founded by Jesse McMillen (Sikeston, Missouri; Node Zero active as of June 2026), it applies **permaculture principles** (catch & store energy, produce no waste, use edges/value diversity, integrate rather than segregate, small & slow solutions, every element serves multiple functions) to core human needs: energy, shelter, water, food, communication/mesh networking, finance/credit, knowledge commons, and governance.

**Core ethos**: "One Human Family." Maximum good for the greatest number of system nodes per unit of human effort. No patents ever. Knowledge multiplies when shared. Serve the least first. Failures are data—document honestly. Everything free forever under dual licensing: **CC-BY-SA 4.0** (docs/hardware designs) / **GPL-3.0** (code). Permanent archives on Zenodo (DOIs) + IPFS. Built primarily on a phone after shifts; the project succeeds when it no longer needs its founder.

### What It Is (High-Level Layers)
It is not a single product but an interlocking stack designed for fractal/self-similar scaling (local nodes → neighborhoods → regions → global mesh):

1. **Philosophy & Epistemology (Level 0)**: Axioms (AX-xxx, 30+), postulates, "Agape" ethics (unconditional care/cooperation), UNE (Universal Nomenclature Engine—36-char naming system for precise, combinatorial identification). "Kingdom Engine," fractal convergence, and honesty markers (clearly label Theoretical vs. Modeled vs. Prototyped vs. Field-tested). Governance without hierarchy; contribution-verified systems.

2. **Physical Infrastructure**:
   - **Energy (Thermal Cascade / H-003 hypothesis)**: Passive solar-thermal systems using **volumetric blackbody / aerated glass-fiber reinforced concrete (AE-GFRC / Aerocement)** panels. These act as absorbers *and* high-surface-area heat exchangers (target 500–2,000 m²/m³). Flow: Fresh air → desiccant → underground wet aerocement labyrinth (filled solid, never lined) for evaporative/ground-coupled cooling → cold tank (radiative night-sky) / hot tank cascade → Stirling engine or TEG for work → loop. Aims for \~55°F output air on hot days (ground-source physics), multi-night storage, zero parasitic fans/grid. Simulated metrics (theoretical, pre-physical validation): \~12.91 kWh/m² nightly capture; scaled examples for 10 m² collectors. Hard rules: ≤100% thermo efficiency claims; 21-day wet cure; two separate tanks; desiccant at intake only. Specs in `research/thermal-systems/` (WBTE-01 Wet-Bulb Thermal Engine, CTBS-01 Cascading Thermal Battery System, AE-GFRC-01 mix designs with zirconium for durability/ASR resistance). Related: ferrocement domes for shelter.
   - **Shelter**: Bolt-together ferrocement / AE-GFRC geodesic dome panels (hurricane/earthquake/fire resistant, LEGO-like).
   - **Water/Food**: Permaculture designs (black locust, aquaponics, living willow, ferrocement tanks). Recycling business (e-waste → mesh nodes/data destruction).
   - **Comms**: AEGIS MESH / decentralized mesh (ESP32/LoRa/WiFi, batman-adv, IPFS, Syncthing; recycled hardware, solar-powered; offline LLMs/local AI). "Spoke" nodes via template repo. Start with kiosk at Sikeston I-55/I-57 interchange.

3. **Finance & Incentive Layer**: 
   - Practical **credit-building path** (PRF-001 Cascading Credit Convergence Theorem): From thin/bad credit (\~660) to ≥720 personal + PAYDEX ≥80 business in ≤24 months at near-zero extra cost ($50 one-time rent reporting + refundable deposits). Route existing spending (rent via Kikoff reporting, bills via secured cards like Varo Believe, Net-30 accounts paid early, business banking/Mercury/DUNS). Leads to DSCR loans for income-generating property (property pays its own mortgage) → business credit scale → self-sustaining "autonomous credit machine." Detailed checklist in `docs/economics/EXECUTION-CHECKLIST.md`.
   - **ACRE token** (conceptual/pre-launch; Solana planned, not deployed/minted/pre-mined): Minted *only* for verified *innovation* / new knowledge / bug fixes / first-in-climate validation / tools—not hours, replication, or monitoring. Two independent validators required. Categories with example amounts (e.g., first climate-zone node: high; skill docs/tools: medium). Validators earn small amounts for inspections. Spec in `tokens/ACRE_SPECIFICATION.md`. Bounties are a theoretical prioritization framework (impact × urgency × novelty / effort), not live rewards.

4. **Tools, Compute & Automation**: Scripts (`scripts/`), tools (e.g., slump-brain rheology calculator, sensor logging, health monitors), Kai 9000 (workflow/AI on Galaxy A15/Termux), UNE resolver/protocol, ACRE tagger/validator, governor-daemon, local LLM hooks/efficiency measures (`compute/n0`), deployments, bin utilities. CI workflows protect core.

5. **Community & Publication**: START-HERE.md (plain-language entry), HELLO.md, STRUCTURE.md, CALL-TO-BUILDERS-01.md, CONTRIBUTING.md, validator handbook, discussions. Feedback loops: Recycling → hardware → mesh → revenue/land → food/energy → more nodes. Build order prioritizes mesh/comms first, then ledger/ACRE, thermal, shelter, food, teams, 501(c)(3)/land.

**Interconnection (System Map)**: Mesh enables coordination → Contribution ledger + ACRE rewards verified work → Funds/unlocks thermal energy → Shelter → Food/health → Teams → Permanence. Every element stacks functions and generates surplus.

### Current Status (as of 2026-07-17 commits)
- **Highly active** solo development (recent: hypothesis v2 + measurement harness, ACRE tagger v0.2, CI workflows, agape-UNE deploy). 
- **Theoretical / simulation-heavy** on core physics (H-003 v2 published to Zenodo/IPFS with peer-validation notes; clear disclaimers: BUILD-001 first pour is the calibration gate for ACRE claims — no physical prototypes or pours tested yet). Node Zero (Sikeston hot/humid) is the proof vehicle.
- Credit path is practical/actionable with checklists and formal "proof."
- ACRE conceptual (Solana integration + tagger v0.2 in progress; no tokens live).
- Mesh/spoke templates exist; recycling business model sketched.
- Funding: Zero so far (public ledger planned); crypto addresses + GitHub Sponsors for materials/bounties. Not selling tokens/courses.

### How to Engage / Make Clear Progress
- **Non-technical**: Read START-HERE.md + HELLO.md + docs/core/OPENROOT-SIMPLE-SUMMARY.md + EXECUTION-CHECKLIST.md. Start credit path this week ($50 out-of-pocket).
- **Builders/Makers**: CALL-TO-BUILDERS-01.md. Physical tests (tiles, pours, sensors), CAD, regional material adaptations, climate validations. Document everything (photos, data, failures). Label maturity.
- **Technical**: Fork; contribute to scripts, thermal sims (`h003_physics.py`), UNE, mesh, ACRE validator, local AI. See CONTRIBUTING.md.
- **Everyone**: Star/fork, join SimpleX channel, share, validate claims against Zenodo/IPFS, offer skills/land/lab time. Bounties theoretical for now.
- **Validation priority**: Physical AE-GFRC tiles/pours + thermal loop data (scripts for logging/IPFS). Climate diversity needed.

### Clarity Assessment & Suggestions for Maximum Good/Efficiency
The repo is dense, fractal, and self-referential by design (UNE codes, axioms, multiple entry points). Strengths: Honest disclaimers on theoretical claims, dual licensing, permanent archives, practical on-ramps (credit checklist, hard rules), permaculture integration, anti-fragile design (mesh, open, local-first). Weaknesses for newcomers: Overlapping/outdated path references (e.g., fractal-convergence mentions), high conceptual density (Agape math, Kingdom Engine), mixed maturity levels without always-obvious top-level status dashboard, some generated/draft docs, image/diagram access issues in tools.

**To make clearer (permaculture-guided efficiency—stack functions, catch & store attention, produce no waste of contributor time)**:
- Enhance top-level README/START-HERE with a visual status matrix (Theoretical/Simulated/Prototyped/Field for each subsystem) + one-page "Current Focus: BUILD-001 + Node Zero pour." *(Addressed in this EXTERNAL-OVERVIEW.md)*
- Single canonical SYSTEM-MAP.md or interactive diagram linking all layers with maturity + next-action.
- Consolidate entry points; auto-generate indexes from UNE registry.
- Add "First Saturday Morning Build" guides (e.g., test tile or simple mesh node).
- Dashboard for ACRE claims, build-logs, funding ledger, sensor data.
- Prioritize physical validation gate (as noted in hypotheses)—theory is strong; empirics unlock ACRE and credibility.

This is a rare, high-integrity attempt at open regenerative systems from first principles, blending low-tech appropriate tech with modern tools (mesh, local AI, crypto incentives for knowledge, credit mechanics). It is early-stage and founder-dependent but structured for distribution. Verify all claims against the immutable Zenodo/IPFS records. Contact: jrm8908@proton.me. Start where you are—build what you can. One pour, one node, one warrior at a time.

*This file created to obtain yield on the clarity assessment. Next atomic: git -C $HOME/openroot add docs/EXTERNAL-OVERVIEW.md && git -C $HOME/openroot commit -m "docs: add EXTERNAL-OVERVIEW.md + status matrix (clarity + H-003 gate)" && echo "Now push + prepare Zenodo update."*
