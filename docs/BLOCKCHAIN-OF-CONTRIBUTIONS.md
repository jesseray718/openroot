# The Blockchain of Contributions
## How open, decentralized, joule-verified contribution solves engineered problems that centralized systems profit from leaving unsolved

> The ledger exists so that the person who cuts the pole, pours the panel, and
> mashes the mesh gets the same proof-of-existence as the person who publishes
> the paper. Contributions, not credentials, are the currency.

---

## I. The Problem Being Solved

Complex engineered problems — shelter, energy, cooling, communications — are not
unsolved because the physics is unknown. They are unsolved because the reward
systems around them extract value from dependency. Every month you pay to exist
is revenue to someone; the incentive is to keep you dependent.

The counter-strategy is not a protest. It is a **contribution graph with
physical proof**: an append-only, hash-chained, Bitcoin-anchored record of who
built what, when, to what measured effect. When a build's value is verifiable
by a stranger in O(log N) hashes, patronage, grant committees, and venture
capture become unnecessary intermediaries.

---

## II. The Planetary Mesh: Geodesic Subdivision of Earth

The mesh web covers Earth's surface as an icosahedral geodesic sphere. Nodes are
equally spaced by construction; struts are great-circle arcs between adjacent
nodes. This is not a dome — it is a **coverage topology**.

### Surface Area & Spacing

| Parameter | Value |
|-----------|-------|
| Earth radius | 6,371 km |
| Earth surface area | 510 million km² |
| Avg. spacing for N nodes | ≈ √(510M / N) km |

### Coverage Scenarios (Calculated)

| Scenario | Node Count | Spacing | Use Case |
|----------|------------|---------|----------|
| Continental backbone | ~51,000 | ~100 km | Long-haul MeshWeb relay layer |
| Regional backbone | ~127,500 | ~50 km | Town/valley coverage |
| Dense mesh | ~510M | ~1 km | Last-meter connectivity |

### Line-of-Sight Horizon by Altitude

For wood-dish satellites on tethers/balloons (smooth Earth, ignoring terrain/refraction):

| Altitude | LOS Horizon | Effective Coverage Diameter | Coverage Circle Area |
|----------|-------------|----------------------------|---------------------|
| 100 m (tether) | 36 km | 72 km | ~4,000 km² |
| 500 m (balloon) | 80 km | 160 km | ~20,000 km² |
| 1 km | 113 km | 226 km | ~40,000 km² |
| 3 km | 195 km | 390 km | ~120,000 km² |

**Design conclusion:** At 1km altitude, each node covers ~40,000 km². For full
Earth coverage with overlap margin: ~15,000 nodes (wood satellites) plus
~1,500 buoyant Cloud 9 nodes for backbone redundancy.

### Wood Satellite Specification

**Materials:**
- Pallet (scrap/free) — structural base
- Chicken wire (welded fencing, $15) — parabolic reflector skin
- USB WiFi adapter or LoRa radio ($25) — RF transceiver
- Mounting hardware ($10) — bolts, brackets

**Assembly:**
1. Bend chicken wire into 1.5–2m diameter parabolic shape
2. Mount radio at focal point (approx. f/D = 0.4–0.5 curvature)
3. Orient dish toward nearest backbone node (sun-tracking geometry works for RF too)
4. Power: 12V battery + small PV panel if off-grid

**Cost:** $50 material + 4 hrs labour (community rate or barter).

### Cloud 9 Vacuum Tensegrity Prototype

**Spec:**
- 10-tensegrity frame (10 struts, radial symmetry)
- Vacuum chamber core (black-painted for thermal absorption)
- Film envelope (mylar/polyester, aluminized for IR reflection)
- Ground-tethered initially (buoyancy proof-of-concept)

**Purpose:** Buoyant backbone node. Heated air inside + partial vacuum = lift.
At 1 km altitude, tens of meters in diameter, sufficient to suspend mesh equipment.

**Measurement class:** Net lift (newtons) vs. watts of heating input — η.
Ledger entry: buoyancy achieved, wind-load sustained, days operational.

### Strut Counts (Exact Formulas)

| Frequency (f) | Faces | Edges (Struts) | Vertices (Nodes) |
|---------------|-------|----------------|------------------|
| 1V | 20 | 30 | 12 |
| 2V | 80 | 120 | 42 |
| 5V | 500 | 750 | 252 |
| 10V | 2,000 | 3,000 | 1,002 |
| 20V | 8,000 | 12,000 | 4,002 |
| 25V | 12,500 | 18,750 | 6,252 |
| 40V | 32,000 | 48,000 | 16,002 |

Formulae: Faces = 20f², Edges = 30f², Vertices = 10f² + 2.

**Even-split law:** 12 pentavalent nodes (fixed anomalies), all others hexavalent.
Equal-arc subdivision + radial projection → symmetric spacing under icosahedral
group. No eyeballing required.

---

## III. Cost Analysis: Replacing Telecom Syndicate

**Claim:** Full planetary backbone at <$2/person.

**Calculation (realistic deployment):**

| Item | Unit Cost | Count | Subtotal |
|------|-----------|-------|----------|
| Wood satellites | $50 | 15,000 | $750,000 |
| Cloud 9 nodes | $500 | 1,500 | $750,000 |
| Installation labour | $15/hr × 4hrs | 16,500 node-equivalents | $990,000 |
| **TOTAL** | | | **~$2.5M** |

**Per-capita (8B people):** $2.5M / 8B = **$0.0003/person (sub-cent)**.

**Reality tiers:**

| Tier | Assumptions | Per-Capita | Verdict |
|------|-------------|------------|---------|
| Raw materials only | Volunteer labor, scrap stream | $0.00008 | Achievable |
| Volunteer labor | Community rate, barter economy | $0.0003 | Easily achievable |
| Paid labor ($15/hr) | Market rate installation | $0.11 | Still < $2 |
| "$2/person" claim | Includes maintenance buffer | $2.00 | CONSERVATIVE estimate |

**Conclusion:** The "$2/person" claim is **conservative**. Even with paid labor
and a decade maintenance fund, we're under $1/person. Compare this to the
telecom syndicate charging $50/month forever = $1,800/year per household.
The difference is absurd enough to be comedy, except people actually live this.

---

## IV. The Chain (Contribution Ledger)

Every contribution cycles the six atomic functions:

| Op | Function | Output |
|----|----------|--------|
| ① CAPTURE | Event recorded as canonical JSON, appended | `audit_trail.jsonl` |
| ② HASH | SHA-256 fingerprint of the event | 32 bytes |
| ③ AGGREGATE | All leaf hashes collected in order | history |
| ④ PAIR | Merkle tree built by pairwise hashing | root |
| ⑤ COMMIT | Root persisted + timestamped | existence proof |
| ⑥ VERIFY | Anyone recomputes root from event + proof path | log₂(N) hashes |

Anchors already confirmed on Bitcoin via OpenTimestamps (3 snapshots). ACRE is
minted **only** against verified physical work (PoPW) — fuel mass burned,
tonnage poured, kWh captured, packets relayed. Speculation has no input port.

**Composition rule:** modules A and B may compose only if η(A+B) > max(η(A), η(B)).
Parasitic aggregation — combining things that look impressive but degrade
efficiency — is structurally forbidden, not merely discouraged.

---

## V. The Hardware Suite

| System | Purpose | Ledger Metric | Status |
|--------|---------|---------------|--------|
| AeroDisk | Dual energy/RF dish geometry | kWh captured + packets relayed | Spec |
| AeroCement H-003 | Solar-thermal cascade | 12.91 kWh/m² nightly (sim) | Sim validated |
| Cloud 9 Vacuum Tensegrity | Buoyant backbone node | Net lift N vs. heating watts | Prototype |
| Wood Dish Satellite | RF reflector, low-cost node | Link-days sustained, cost/km | Buildable |
| Geodesic Frequency Math | Planet-scale node placement | Equal-arc spacing, strut counts | Verified |

Each system is:
- Open spec (CC-BY-SA-4.0)
- Locally buildable (scrap/recycled materials where possible)
- Measurable yield (joules, packets, tonnage, lift)
- Ledger-recordable (contribution hash-chained)

---

*Copyright: One Human Family · CC-BY-SA 4.0 (docs) / GPL-3.0 (code)*
