# OpenRoot — Floor-Lift Economy, Four Engines, Superlinear Orchestration

## Core Thesis

**The spread between top and bottom is a speed limit on compound human growth.**

Same artifact, routed differently: 26x difference in systemic value. Controlled demo:
`floor_lift 67.05` (bottom-third routing) vs `2.5` (premium routing) — identical 100-unit benefit.

Metric: `floor_lift = Σ (benefit_i × (1 - percentile_i/100)²)` — graded by routing, not volume.
Live infrastructure: tier-0 deterministic gates → tier-4 big-brain (Qwen 72B) under a $0.50 hard
spend cap, CONFIRM=1 human gate, lessons.db sha-chained mistake→solution memory.

---
# OpenRoot — The Thermodynamic Commons

**Physical infrastructure + the computational swarm that serves it.**

> η = useful_joules / human_joules
> Every cycle must close on real thermal, material, or food yield.

---

## Status Badges

| Proof | Ledger | Publication | Quality |
|-------|--------|-------------|---------|
| ![Proof of Physical Work](https://img.shields.io/badge/PoPW-8.13M%20ACRE-brightgreen?style=flat-square&logo=bitcoin) | ![Thermal Ledger](https://img.shields.io/badge/Thermal%20Ledger-12.91%20kWh/m²%2Fnight-blue?style=flat-square&logo=thermal) | ![Zenodo](https://img.shields.io/badge/Zenodo-10.5281/zenodo.21225683-589632?style=flat-square&logo=zenodo) | ![License GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-orange?style=flat-square&logo=gnu) |
| ![ACRE Token](https://img.shields.io/badge/ACRE-16.27M%20cumulative-purple?style=flat-square&logo=solana) | ![Bitcoin Anchor](https://img.shields.io/badge/Bitcoin%20Anchor-3%20confirmed-black?style=flat-square&logo=bitcoin) | ![IPFS](https://img.shields.io/badge/IPFS-4%20CIDs%20pinned-ff5500?style=flat-square&logo=ipfs) | ![Last Commit](https://img.shields.io/github/last-commit/jesseray718/openroot?style=flat-square) |

---

## Quick Jump

| If you want... | Click here | Why |
|----------------|------------|-----|
| **Plain-language intro** | [START-HERE.md](./START-HERE.md) | No jargon — credit, energy, what to do this week |
| **Full thesis** | [THESIS.md](./THESIS.md) | The complete thermodynamic argument |
| **Hardware builds** | [aerocement/](./aerocement/) | Volumetric blackbody concrete recipes |
| **Talent alignment** | [TALENT-ALIGNMENT-PROMPT.md](./TALENT-ALIGNMENT-PROMPT.md) | Map ANY skill to the Four Engines |
| **Community standards** | [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) | How we treat each other |

---

## The Four Engines

| Engine | Purpose | Live Components |
|--------|---------|-----------------|
| **Knowledge** | Axioms, postulates, governance | 7 physics axioms, fractal constitution |
| **Energy** | Passive solar-thermal, storage | Black Locust coppice + RMH, H-003 thermal cascade |
| **Material** | Shelter, water, food | Aerated GFRC panels, ferrocement domes, aquaponics |
| **Finance** | Credit-building, ACRE token | PRF-001 routing, PoWr minting, thermodynamic ledger |

**Permaculture principle:** Each engine serves multiple functions. Each node generates surplus. Nothing extracted, nothing wasted.
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

Release: `v2026.09.20-floorlift` · Milestone 6 open · Quadratic exponent is a falsifiable hypothesis (agape_cascade validation pending).


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

The ledger proves every claim with measurable joules:

| Component | Status | Proof |
|-----------|--------|-------|
| Merkle audit trail | ✅ Live | `audit_trail.jsonl` → 32-byte root |
| Bitcoin-anchored snapshots | ✅ Confirmed | 3 OpenTimestamps on Bitcoin blockchain |
| Landauer + E=mc² bridge | ✅ Working | 256 bits → 7.36e-19 J → 8.19e-36 kg |
| ARM energy measurement | ✅ Live | CPU freq scaling → joule estimation |
| Kai9000 heartbeat | ⏳ Instrumenting | 0.26234 J/cycle target |

**Properties:**
- Root size: 32 bytes (constant, regardless of history length)
- Verification cost: log₂(N) hash operations
- Bitcoin-anchored via OpenTimestamps (independently verifiable)

---

## Contributing

**Shared credit is the doctrine.** See [CONTRIBUTING.md](./CONTRIBUTING.md) and [START-HERE.md](./START-HERE.md).

### How to Join
1. Read the talent alignment prompt above
2. Post output as GitHub issue with label `talent-alignment`
3. Fork relevant repo, submit PR within 2 weeks
4. Receive credit in README (auto-updated via `bin/pr_intake.sh`)

### Current Priorities
| Role | What You'd Do | Capital Needed | Timeline |
|------|--------------|----------------|----------|
| Experimentalist | Build H-003 prototype, log 30 days data | $2,000-5,000 | 8 weeks |
| Smart Contract Dev | ACRE validator on Solana | $0 (devnet free) | 10 weeks |
| Mesh Engineer | Deploy offline node on Raspberry Pi | $180-250 | 10 weeks |
| Material Scientist | Validate AE-GFRC simulations | $500-1,500 | 12 weeks |

See issue #5: [Call to Builders — OpenRoot Needs You](https://github.com/jesseray718/openroot/issues/5)

---

## Publications & Proofs

| Medium | Identifier | Content |
|--------|------------|---------|
| Zenodo | [10.5281/zenodo.21225683](https://doi.org/10.5281/zenodo.21225683) | Thermal system specs (WBTE-01, CTBS-01, AE-GFRC-01) |
| IPFS | QmbNEo5Qjqtug1BRYj4GKNyohdo1EkvLrZZRNrfmqMKpzY | v0.6 milestone publication |
| Solana | 3fF26gcj1ednMUASxJxo1dt5rQ2ZegXbH7k4ynJazerk | ACRE smart contract |
| Bitcoin | 3 OpenTimestamps confirmed | Ledger snapshots anchored |

---

## License

- **Hardware/Documentation:** CC-BY-SA-4.0
- **Software:** GPL-3.0
- **Patents:** None. Ever. Defensive publication only.

**Copyright:** One Human Family

---

## Contact

- **Email:** jrm8908@proton.me
- **GitHub:** [github.com/jesseray718](https://github.com/jesseray718)
- **Profile Atlas:** [jesseray718.github.io](https://jesseray718.github.io)
- **SimpleX Channel:** [Join the mesh](https://smp9.simplex.im/a#vklZrSjZTQdgXBqW_sLK1h5FeajDoa7wTaSWGSw62Sw)

---

*Engineering as an act of unconditional integration.*
*The unification is not something you do. It is something you stop denying.*

<!-- OPENROOT-A15-MIRROR:START -->
## A15 micro-mirror rollout

### Architecture

The target is a smaller resident replica of the same OpenRoot node,
not a separate phone chatbot:

- Same logical query interface and request format.
- Same pod identities, evidence references, and retrieval contracts.
- Cached pathways with provenance and dependency validation.
- Same dossier-to-specialist handoff and compatible receipts.
- Portable relative paths with device-specific model/storage settings.

The proposed phone team uses `qwen2.5-coder:0.5b` as operator and
`qwen2.5:1.5b` as writer. This collaboration is not yet validated end to end.

### Verified results — 2026-11-03

A manifest-gated transfer staged 20 files on the A15. All 20 passed
post-transfer SHA-256 verification against the generated manifest.

The staged artifacts include the auto-dossier compiler, pathway-cache
tooling and ledger, receipt-cache database, genesis-chain artifact, and
supporting documentation/tools.

SQLite databases were exported using the SQLite backup API. This provides
per-database snapshots, not a transactionally synchronized snapshot across
all databases. The rollout did not activate mirrored scripts or replace
the existing phone installation.

### Model smoke tests

The Termux loopback API returned HTTP 200 and `PHONE_OFFLINE_OK` for:

| Model | Observed request time |
|---|---:|
| `qwen2.5-coder:0.5b` | 11.92 seconds |
| `qwen2.5:1.5b` | 87.26 seconds |

These are end-to-end request times, not generation-speed benchmarks.
Network-disconnected phone-only inference has not yet been explicitly
confirmed.

### Current status: staged, not activated

| Check | Result |
|---|---|
| Staged files matching manifest hashes | 20 / 20 |
| Receipt-cache rows | 0 |
| Valid JSON records in pathway ledger | 2 |
| Referenced pathway evidence files resident | 0 / 2 |
| End-to-end mirrored query | Not verified |
| Cross-device cached-pathway reuse | Not verified |

Valid JSON does not establish pathway-chain integrity or evidence validity.
Transfer hashes establish that selected artifacts arrived intact, not that
the application or its dependencies are complete.

### Remaining activation gates

1. Identify the computer's working query/router entry point and actual
   pod/cache stores.
2. Include required resident pods, source objects, and pathway evidence.
3. Verify compiler dependencies and device-path resolution.
4. Test the operator/writer handoff using the same dossier contract.
5. Run a known cached query on both nodes and compare pathway/evidence IDs.
6. Repeat on the phone with networking disconnected.
7. Activate only after the checks pass.

### Shared historical-pod query (code path; device validation pending)

The same local-only query path is available on the computer and through the
phone snapshot CLI:

```bash
# Computer, from the checkout containing these changes
python3 bin/fts_pod_search.py ask --json "thermal storage"

# A15 Termux, from the checkout containing these changes, after staging
python3 bin/openroot-phone-v1 ask --json "thermal storage"
```

Both commands search `data/thermodynamics/openroot_interactive_pods.db` and
emit stable evidence IDs. Compare those IDs and the database SHA-256 across
devices; generated answer wording may differ by model. The phone command checks
the snapshot manifest hashes for the query tool, shared Ollama helper, and pod
database before running. The snapshot must list `bin/fts_pod_search.py`,
`bin/lumo_lib.py`, and `data/thermodynamics/openroot_interactive_pods.db` under
those exact relative paths. This command does not create or transfer a snapshot.
Use the same stable SQLite backup on both devices; a nonempty WAL is rejected.
Answers use a loopback Ollama endpoint only; the phone
defaults to `qwen2.5:1.5b`, while the computer uses the configured local model.
Both default to three evidence records. The JSON includes full pod records, so
review it for private content before sharing. An evidence ID identifies a
record; it does not verify the chain or prove the model's answer is correct.
This adds a query path, not proof that the current phone snapshot contains the
required files or that either device has completed an offline query.

### Publication boundary

Publish reviewed source, documentation, and non-sensitive verification
summaries only. This README update does not include credential files,
raw token documents, private corpus contents, or runtime databases.

<!-- OPENROOT-A15-MIRROR:END -->
