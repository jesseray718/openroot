# ACRE Token Specification
## Real-Value Currency Minted for Verified Innovation

**Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)  
**Launch Target:** After Node Zero + 2 independent replications validated  
**Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)  
**Core Mechanic:** ACRE minted only when software/hardware improves, debugs, or gains knowledge  
**Total Supply:** Unlimited (minted only for verified innovation; deflationary through use)  
**Governance:** Community + legal framework (501(c)(3) nonprofit TBD)

---

## Philosophy

**ACRE = Proof of Innovation.**

ACRE is **minted only when the commons materially improves**—when:
- **Hardware designs** are debugged, optimized, or validated
- **Software tools** fix bugs or add critical features
- **Library knowledge** documents previously undocumented techniques
- **Cross-disciplinary integration** opens new capabilities

**Not minted for:** hours of work, mere effort, or repetition. Only for **measurable improvement** to the stack.

The principle: *Builders who advance the project get paid. Repetition doesn't.*

---

## Core Principle: Proof of Contribution

ACRE distinguishes between:

| Activity | ACRE? | Reason |
|----------|-------|--------|
| Build first thermal node (Node Zero) | ✅ YES | Validates entire stack; debugs in real conditions |
| Replicate Node Zero exactly (identical build) | ❌ NO | No new knowledge; just copying |
| Build Node Zero AND discover desiccant placement was wrong | ✅ YES | Debugged critical flaw; shared fix with commons |
| Document "how to mix aerocement" (new skill) | ✅ YES | Knowledge enters library; others can replicate |
| Translate existing skill to new language | ⚠️ MAYBE | Low-value contribution; small ACRE or none |
| Optimize sensor script for 10x faster logging | ✅ YES | Software improvement; tangible benefit to all |
| Run Node Zero for 30 days (no new data) | ❌ NO | Monitoring only; no innovation |
| Port sensor_log.sh from Bash to Python | ✅ YES | Better maintainability, new platform support |
| Win Stirling engine bounty with working prototype | ✅ YES | Major innovation; opens new energy tier |
| Discover bug in START-HERE.md curing schedule | ✅ YES | Critical fix; prevents 50+ failed nodes |

---

## Minting Triggers

### Category A: Hardware Validation & Debugging

**ACRE minted when:** Physical hardware is built, validated, and the data reveals actionable improvements.

#### A1: First Node in Climate Zone (20,000 ACRE)

**Trigger:**
- ✅ Build complete (21-day wet cure + 7-day dry-down)
- ✅ 48+ hours sensor data on clear day
- ✅ Two independent validators approve
- ✅ Data published to IPFS + Zenodo + GitHub
- ✅ Reveals new climate performance metrics OR bugs in existing design

**Why 20,000?** First node is pure validation—high risk, high value.

**Examples:**
- Node Zero (Sikeston, hot/humid): 20,000 ACRE ✅
  - Validates COP 8,544 in hot/humid. Debugged desiccant placement flaw (was downstream, should be upstream). Shared fix with commons.
  
- First node in Arizona (hot/dry): 15,000 ACRE ✅
  - New climate zone. Data shows efficiency improvement in low-humidity: 10,000 W potential vs. 2,197 W in humid. Actionable diff.

- Fifth node in Missouri (same climate, same design): 0 ACRE ❌
  - Replication only. No new data. No innovation. Validates known performance.

#### A2: Hardware Bug Fix / Optimization (5,000–50,000 ACRE)

**Trigger:**
- ✅ Existing design has flaw (documented in issues or in use)
- ✅ Builder proposes fix with engineering analysis
- ✅ Fix is tested (simulation, small prototype, or full rebuild)
- ✅ Improvement measured and published (COP increase, cost reduction, durability boost)
- ✅ Fix merged into START-HERE.md or projects/

**Payout scale:**
| Fix Type | Scope | ACRE |
|----------|-------|------|
| Material substitution (copper → aluminum, saves 20%) | Minor | 5,000 |
| Desiccant placement correction (fixes 50% of failures) | Critical | 25,000 |
| Copper coil geometry redesign (improves COP by 15%) | Major | 50,000 |
| New heat exchanger design (10x better performance) | Revolutionary | 100,000+ |

**Examples:**
- You realize xanthan gum ratio was wrong → retest → publish corrected recipe → **10,000 ACRE**
- Discovery: panel absorber needs black paint, not bare cement → fixes 30% of low-output nodes → **15,000 ACRE**
- New sensor placement algorithm cuts drift by 50% → **8,000 ACRE**

### Category B: Software Improvement

**ACRE minted when:** Code is written, debugged, or optimized—creating tangible value for builders.

#### B1: New Tool / Script (5,000–50,000 ACRE)

**Trigger:**
- ✅ Fills a gap in the toolkit (automation, monitoring, analysis)
- ✅ Code is production-ready (tested, documented, open-source)
- ✅ Solves a real problem reported by builders
- ✅ Merged into /scripts/ with usage docs

**Payout scale:**
| Tool | Value | ACRE |
|------|-------|------|
| Simple Python IPFS uploader | Low | 5,000 |
| Real-time Solana transaction logger | Medium | 15,000 |
| Thermal simulation model (predicts panel performance) | High | 30,000 |
| Full OpenRoot data dashboard (web UI for all nodes) | Very high | 50,000 |

#### B2: Bug Fix (1,000–20,000 ACRE)

**Trigger:**
- ✅ Bug exists in deployed code (documented in issues)
- ✅ Root cause identified
- ✅ Fix is tested and merged
- ✅ Fixes production outages OR prevents data loss

**Payout scale:**
| Bug Severity | Impact | ACRE |
|--------------|--------|------|
| Typo / formatting | Trivial | 0 |
| Logic error in noncritical path | Minor | 1,000 |
| Data logging skips readings | Moderate | 5,000 |
| Sensor calibration formula incorrect | Critical | 20,000 |

#### B3: Optimization / Refactor (2,000–30,000 ACRE)

**Trigger:**
- ✅ Code works but is slow, fragile, or hard to maintain
- ✅ Optimization improves performance, reliability, or usability
- ✅ Measurable improvement (10% faster logging, 50% less code, 0 crashes vs. 5/month)
- ✅ Merged with before/after metrics

**Examples:**
- Rewrite sensor_log.sh in Python (10x faster, handles edge cases) → **12,000 ACRE**
- Refactor validator handbook for clarity (fixes 80% of validation errors) → **8,000 ACRE**
- Add automatic retry logic (reduces data loss from network glitches) → **10,000 ACRE**

### Category C: Knowledge & Skills

**ACRE minted when:** The library gains actionable knowledge that helps other builders.

#### C1: New Skill Document (5,000–20,000 ACRE)

**Trigger:**
- ✅ Fills a gap in skills-library/ (undocumented technique OR problem-solver)
- ✅ 500+ words, step-by-step with photos
- ✅ Has been tested by at least 1 other builder (proof in PR comments)
- ✅ Prevents a common failure OR enables a new capability

**Payout scale:**
| Skill | Impact | ACRE |
|-------|--------|------|
| How to mix aerocement (foundational) | Very high | 15,000 |
| How to build activated carbon oven | Medium | 8,000 |
| Advanced desiccant tuning | High | 12,000 |
| Troubleshooting: why my sensor reads -127°C | Low–Medium | 3,000 |

**Examples:**
- Document "Nighthawkin Light foam method, tested in 3 climates" → **15,000 ACRE** (foundational)
- Write "How to repair corroded copper coil" → **5,000 ACRE** (solves real failure)
- Create "Aerocement failure taxonomy" (23 failure modes, how to prevent each) → **18,000 ACRE** (critical)

#### C2: Skill Replication in New Context (3,000–10,000 ACRE)

**Trigger:**
- ✅ Existing skill tested in new climate/region/material context
- ✅ Results documented (what worked, what failed)
- ✅ Adaptations documented (modifications needed for new context)

**Examples:**
- You test xanthan foam concrete in tropical Brazil (vs. original Midwest) → document adjustments → **5,000 ACRE**
- Replicate aerocement technique using local sand/cement brands → document regional sourcing → **4,000 ACRE**

#### C3: Research Data / Analysis (2,000–15,000 ACRE)

**Trigger:**
- ✅ Original experimental work (not just building a known design)
- ✅ Scientific rigor (hypothesis, methodology, error analysis)
- ✅ New insight (reveals previously unknown property/behavior)

**Examples:**
- Long-term degradation study: aerocement performance over 2 years → **8,000 ACRE**
- Material science: comparative COP across 5 different absorber materials → **10,000 ACRE**
- Climate analysis: map COP vs. humidity/temperature across 10 regions → **15,000 ACRE**

#### C4: Integration / Cross-Disciplinary Bridge (5,000–50,000 ACRE)

**Trigger:**
- ✅ Connects two previously separate domains
- ✅ Creates new capability (e.g., combines thermal + aquaponics, or Stirling + mesh networking)
- ✅ Fully documented integration pathway

**Examples:**
- Integrate aerocement with aquaponics (use waste heat for fish farming) → **25,000 ACRE**
- Combine Node Zero with AEGIS MESH networking (sensor data routed via mesh) → **20,000 ACRE**
- Add cold thermal battery to existing node (enables freezing capability) → **15,000 ACRE**

### Category D: Bounty Challenges (1,000–150,000 ACRE)

| Challenge | Prize | Why ACRE? |
|-----------|-------|----------|
| Scrap-steel Stirling engine (200W+) | 1,000 ACRE | New hardware tier unlocked |
| Stirling-powered scooter | 10,000 ACRE | Mobility application opens possibilities |
| Stirling-powered tractor | 25,000 ACRE | Agricultural scale validation |
| Stirling-powered tugboat | 50,000 ACRE | Waterborne application + integration |
| Stirling-powered bulldozer | 75,000 ACRE | Heavy equipment; transforms energy independence |
| Industrial factory drive (5kW+) | 100,000 ACRE | Commercial viability proven |
| Community power plant (10kW+) | 150,000 ACRE | Grid-scale distributed energy |
| Cold-battery refrigerator | 5,000 ACRE | New thermal application |
| Water purification system | 2,000 ACRE | Enables survivalist use case |
| Atmospheric water harvester | 3,000 ACRE | Climate-specific breakthrough |

---

## NOT Minted For

**Activity does NOT earn ACRE:**

- ❌ Building Node Zero replica #47 (known design, no new data)
- ❌ Running sensors for 30 days (monitoring, not innovation)
- ❌ Translating docs to Spanish (important, but low innovation)
- ❌ Reporting a typo (fix is <5 lines; trivial)
- ❌ Asking questions on issues (support, not contribution)
- ❌ Validating a build (important but handled separately—validators earn ACRE for each inspection as commodity)
- ❌ Hosting an IPFS node (infrastructure, not innovation)

**Validator exception:**
- Validators earn **100 ACRE per inspection** (recognized utility, not innovation)
- Applies to all validations, even routine replications

---

## Minting Process

### Step 1: Identify Innovation

**Builder recognizes:** "This is new or fixes something broken."

| Scenario | Next Step |
|----------|-----------|
| Build new node in unexplored climate | Create ACRE Mint Request issue + link BUILD_LOG.md |
| Discover bug in curing protocol | Open GitHub issue with analysis, propose fix PR |
| Write new skill doc | Create PR to skills-library/ + link test results |
| Optimize sensor_log.sh | Create PR + benchmarks showing improvement |
| Create new hardware design | Open issue, publish CAD/design docs, request ACRE evaluation |

### Step 2: Document Innovation

**Required for all ACRE requests:**

```markdown
# ACRE Mint Request: [Innovation Title]

## What Changed
[Describe innovation: new hardware, bug fix, software feature, knowledge]

## Why It Matters
[Impact: enables new capability, fixes widespread failure, improves efficiency]

## Proof
- [Link to code PR / hardware photos / skill doc]
- [Before/after metrics if applicable]
- [IPFS hash of full documentation]
- [Zenodo DOI if research]

## Validators
- @validator1 approves: [link to approval comment]
- @validator2 approves: [link to approval comment]

## ACRE Request
- **Category:** [A1/A2/B1/B2/B3/C1/C2/C3/C4/D]
- **Amount:** [ACRE requested]
- **Justification:** [Why this amount]
```

### Step 3: Two Validators Approve

**Validators assess:** "Does this genuinely advance the project?"

- ✅ Code review (if software): Is it solid, tested, maintainable?
- ✅ Scientific review (if research): Methodology sound? Results novel?
- ✅ Practical review (if hardware): Does it work? Will others benefit?
- ✅ Impact: Is the improvement measurable and significant?

**Validators reply with:** `Approved — [Category] — [Amount] ACRE justified because [reasoning]`

### Step 4: Mint on Solana

**Treasury mints ACRE:**

```bash
solana spl-token transfer [ACRE_MINT] [AMOUNT] [builder_wallet] \
  --memo "ipfs://QmXXXXXXXX#[innovation-name]|[category]|@validator1|@validator2"
```

**Transaction anchors:**
- IPFS hash (immutable proof)
- Category (innovation type)
- Validator handles (attribution)
- Solana signature (permanent record)

### Step 5: GitHub + IPFS Record

**PR merged; ACRE recorded:**

```
tokens/mint-log/
├── 2026-06-29_node-zero_20000acre.md
├── 2026-07-05_desiccant-bugfix_25000acre.md
└── 2026-07-12_sensor-optimization_12000acre.md

research/nodes/
└── node-zero/
    └── IPFS_HASH.txt (QmXXXXXXXX)
    └── SOLANA_TX.txt (tx signature)
```

---

## Token Lifecycle

### Earning ACRE

**Channels:**
1. **Build & validate:** First node in climate = 20,000 ACRE
2. **Debug & optimize:** Fix critical bug = 5,000–25,000 ACRE
3. **Advance software:** Write feature/tool = 5,000–50,000 ACRE
4. **Share knowledge:** Document skill = 5,000–20,000 ACRE
5. **Validate others:** 100 ACRE per inspection
6. **Win bounty:** 1,000–150,000 ACRE

### Spending ACRE

**Redemption:**
- **Materials credit:** $50 per 500 ACRE (bulk orders)
- **Workshop access:** 250 ACRE/day (tools + mentorship)
- **Consulting:** 100 ACRE/hour (expert design help)
- **Equipment rental:** 100–1,000 ACRE (specialized tools)
- **Land access:** 500–5,000 ACRE/month (workspace)

**Future (if community votes):**
- DEX listing: Trade ACRE/USDC on Raydium
- Staking: Lock ACRE for governance votes
- DAO treasury: Stake to earn ecosystem share

---

## Safeguards Against Gaming

### Problem: "I'll change one variable and claim innovation"

**Solution:**
- Two independent validators review all claims
- Impact must be measurable (% improvement, cost saved, failures prevented)
- Trivial changes (typo, formatting) = 0 ACRE
- Innovation must be reproducible

### Problem: "I'll mint ACRE for doing nothing"

**Solution:**
- Validators are community members with reputation
- Bad minting decisions are reversible (nonprofit can revoke in early governance)
- On-chain memo records innovation claim publicly
- If overturned: memo field documents it ("Disputed — burned by community vote")

### Problem: "I'll copy someone else's work"

**Solution:**
- IPFS hashing proves originality (hash changes with any modification)
- GitHub history shows authorship
- Validators cross-reference against existing PRs
- Plagiarized work = immediate 0 ACRE + community reputation hit

---

## Economics

### Supply Model

**Year 1 (3 validated nodes + bugfixes):**
- 3 nodes × 20,000 ACRE = 60,000 ACRE
- 5 bugfixes × avg 12,000 ACRE = 60,000 ACRE
- 10 skills × avg 8,000 ACRE = 80,000 ACRE
- **Total:** ~200,000 ACRE in circulation

**Year 5 (50 nodes + robust ecosystem):**
- 50 nodes × 20,000 ACRE = 1,000,000 ACRE
- 200 skills + tools + research = 1,500,000 ACRE
- 10 major bounties = 500,000 ACRE
- **Total:** ~3 million ACRE (estimated)

**Growth limited by:** real innovation, not speculation. Supply follows actual project maturity.

### Value Model

**Initial:** 1 ACRE ≈ $1–$5 USD equivalent (based on materials credit redemption)

**Long-term:** 1 ACRE = access to commons infrastructure + network effects

**No floor / ceiling:** Price floats based on what it can be redeemed for. If tools become cheap, ACRE value adjusts. If land becomes scarce, ACRE value rises.

---

## Pre-Launch (Now)

**Until token launches officially:**

1. **Record all innovation in GitHub issues**
   ```
   Title: ACRE Mint Request — [Innovation]
   Labels: acre, [category], pending-validators
   ```

2. **Validators approve** (in comments + PR review)

3. **Provable priority log**
   - First 100 innovations recorded here
   - When token launches: batch mint all early contributions
   - Zero loss; only adds tech layer

4. **Build Solana integration** (parallel work)
   - SPL token contract on devnet
   - Test memo field format
   - Validator tooling for signing off

---

## Roadmap

| Phase | Timeline | Action |
|-------|----------|--------|
| **Pre-launch** | Now–Dec 2026 | Build validator network, document innovations, GitHub records |
| **Alpha** | Jan–Jun 2027 | Deploy SPL token on Solana devnet, test mint flow |
| **Beta** | Jul–Dec 2027 | Testnet, limited minting, legal review |
| **Launch** | Jan 2028 | Mainnet ACRE token, batch mint early innovators |
| **Scale** | 2028+ | Ongoing minting, ecosystem grows, nonprofit governance |

---

## See Also

- **bounties/README.md** — Active challenges (high-reward innovation)
- **community/VALIDATOR_HANDBOOK.md** — How validators assess innovation
- **research/README.md** — Climate zones & replication requirements
- **projects/aerocement/START-HERE.md** — Build your first node

---

## Dedication

> *"We own nothing. We control everything."*
> 
> *ACRE is minted for those who improve the commons.*

Not for effort. Not for grind. For **innovation**—for those who debug the hard problems, share the hard-won knowledge, and make the next builder's path easier.

**The project succeeds when the innovation no longer needs Jesse McMillen.**

---

**Innovate. Get minted. The commons grows.**
