# OPENROOT PROJECT SKELETON MAP

## THE ATLAS — All Pieces Connected

Complete map of what's being built and how everything connects.

---

## LEVEL 0: CORE PHILOSOPHY
**Location:** `docs/fractal-convergence/`

- **AX-001+** — Axioms (first principles, 30+ active)
- **PO-001+** — Postulates (logical conclusions, 20+ active)
- **AGAPE-ETHICS-01** — Cooperation over competition
- **UNE** — 36-char naming system for organizing everything

## LEVEL 1: PHYSICAL INFRASTRUCTURE

### Permaculture (`research/permaculture/`)
- Willow living fence, worm farm, community garden — design phase

### Thermal Energy (`research/thermal-systems/`)
- WBTE-01 (Wet-Bulb Thermal Engine) — published
- CTBS-01 (Cascading Thermal Battery) — published
- AE-GFRC-01 (Aerated GFRC w/ zirconium) — published
- Thermal Cascade H-003 — validated: sun heats concrete, air moves through underground labyrinth, heat stored, Stirling engine converts to electricity

### Mesh Network (`research/networking/`)
- Core Node: Pi 4/5 or recycled mini PC (batman-adv, IPFS, Syncthing)
- Relay Node: OpenWrt routers from recycling stream
- Edge Node: Old Android phones
- Solar powered, built from recycled electronics

### Housing (`research/construction/`)
- Ferrocement dome panels — bolt-together concrete modules
- FEMA contract target

### Electronics Recycling (`business/recycling/`)
- Data destruction for law firms
- Hardware refurbishing → mesh network nodes
- Material recovery

## LEVEL 2: FINANCIAL SYSTEM (`docs/finance/`)
- Bluebird (prepaid reservoir) → pays personal credit cards + Kikoff
- Mercury (LLC bank) → Amex Blue Business → builds business credit
- Personal and business NEVER cross
- 3 secured cards (Discover, CapOne, OpenSky) build FICO 670+
- Deposits are seeds — returned after 7-11 months
- paycheck script monitors payment schedule at `~/bin/paycheck`

## LEVEL 3: GOVERNANCE (`docs/governance/`)
- NOMOS Schema — attestation system for verifying contributions
- Bounty Board — hypothesis-driven task prioritization
- FEDERATION-01 — multi-party signing authority
- Anyone contributes, contributions verified by peers, reputation = influence

## LEVEL 4: PUBLICATION PIPELINE
- GitHub (code/docs) | Zenodo (DOIs) | IPFS (permanent files) | Solana (timestamps)
- Published: DOI 10.5281/zenodo.21225683, DOI 10.5281/zenodo.21210931
- IPFS CID: QmVJxfQmFoTVDp1GRui8bEKJ7x7J154h8RX3EmxQBcCrBt

## LEVEL 5: AUTONOMOUS TOOLS (`~/.governor/` + `~/bin/`)
- paycheck — payment schedule monitor (deployed)
- aiq — multi-provider AI CLI (needs jq patch)
- governor-daemon — nanobot swarm orchestrator (deployed, limited)
- publish-all — unified GitHub+IPFS+Zenodo publisher (needs fix)
- or-rag — local RAG retrieval (indexing broken)

## LEVEL 6: COMMUNITY
- CONTRIBUTING.md, START-HERE.md, FUNDING.md (published)
- GitHub Discussions live with welcome post
- Goal: recruit co-maintainer (bus factor = 1 currently)

---

## INTERCONNECTION

Recycling feeds hardware → hardware builds mesh → mesh provides internet/services → revenue buys land → land grows food + generates energy → energy powers nodes → cycle continues. Every piece feeds every other piece.

## QUICK REFERENCE

| Question | Go here |
|----------|---------|
| What is this project? | HELLO.md |
| Show me the code | github.com/jesseray718/openroot |
| What are the rules? | docs/fractal-convergence/ |
| Thermal energy stuff | research/thermal-systems/ |
| How do I help? | CONTRIBUTING.md |
| Can I donate? | FUNDING.md |
| What's published? | Zenodo (DOI 10.5281/zenodo.21225683) |
| Where's the finance plan? | docs/finance/ |

---

*Licensed CC-BY-SA-4.0 (docs) / GPL-3.0 (code). Copyright: One Human Family.*
