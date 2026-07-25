# Community Validator Handbook
## Inspect, Verify, Sign Off on Node Data

**Role:** You are a physical validator for OpenRoot nodes in your region.  
**Responsibility:** Inspect builds, verify sensor calibration, audit data integrity.  
**Authority:** Your sign-off makes a build eligible for ACRE token minting.

---

## What Validators Do

1. **Physical inspection** — visit the build site within 2 weeks of completion
2. **Data integrity audit** — check CSV schema, sensor calibration, timestamps
3. **Replication assessment** — can someone else repeat this build with the published data?
4. **Sign-off** — open validation PR with findings and recommendation

**Two independent validators must approve before ACRE minting.**

---

## Pre-Inspection Checklist (Send to Builder)

Request these files **before visiting:**

- [ ] **BUILD_LOG.md** — daily curing photos, temperature log, post-Day-21 notes
- [ ] **SENSOR_DATA.csv** — all readings from Day 22 onwards (dry-down + commissioning)
- [ ] **THERMAL_ANALYSIS.md** — calculated COP, peak delta-T, cost breakdown
- [ ] **Photos folder** — pour day, Day 7 curing, Day 21 complete, final installation
- [ ] **Bill of Materials** — actual costs, supplier receipts
- [ ] **IPFS hash** — sensor data published (ipfs://QmXXXX)

---

## On-Site Inspection (60–90 minutes)

### Visual & Physical

- [ ] **Panel location:** South-facing, unobstructed 6+ hours direct sun
- [ ] **Frame integrity:** No cracks wider than 1/16", surface uniform white/pale gray
- [ ] **Aerocement porosity:** Visual pores visible (not dense/solid)
- [ ] **Copper coil accessible:** Can locate inlet/outlet, measure tube temperatures
- [ ] **Sensor placement:** All 4 sensors accessible, wiring intact
- [ ] **Weather exposure:** Backplate insulated, no water pooling, fasteners secure
- [ ] **Labyrinth (if present):** Trench properly buried, soil compacted, no settling

### Thermal & Sensor Testing

**Bring:** thermometer, multimeter, camera, clipboard

1. **Hand verification (reference thermometer):**
   - Inlet tube (copper) at sensor location → compare to logged value (±3°C acceptable)
   - Outlet tube at sensor location → compare to logged value (±3°C acceptable)
   - Ambient (shaded location) → compare to logged value (±2°C acceptable)
   - If mismatch >5°C: sensor has drifted; note in report

2. **OneWire continuity test (if using Raspberry Pi):**
   ```bash
   ssh pi@[IP]
   ls /sys/bus/w1/devices/  # confirm 4 sensors present (28-XXXX)
   cat /sys/bus/w1/devices/28-*/w1_slave  # live read
   ```
   - All 4 devices respond: ✅
   - 1–2 devices missing: ⚠️ note it
   - 3+ devices missing: ❌ cannot validate yet

3. **CSV schema validation:**
   ```bash
   head -5 SENSOR_DATA.csv
   # Expected header: timestamp,inlet_C,outlet_C,ambient_C,panel_C,solar_W_m2,notes
   # Check: timestamps ISO 8601, temps are numbers (not strings), no gaps >1 hour
   ```

4. **Drift analysis (example):**
   - Plot outlet − inlet (delta-T) over 7 days
   - Expected: peaks 35–50°C on clear days, lower on cloudy
   - If: delta-T consistently <10°C or erratic → possible sensor issue

### Material & Cost Verification

- [ ] **Portland cement receipt:** Qty 1, 50 lb bag at ~$8
- [ ] **Xanthan gum purchase:** 0.5 lb at ~$15 (Amazon/co-op receipt)
- [ ] **Copper coil:** Show HVAC invoice, verify ¾" OD, 15 ft length
- [ ] **Total material cost:** Within $360–$500 range (document variance)
- [ ] **Labor time:** Builder's estimate vs. actual (pour day only, not curing)

---

## Data Integrity Audit

### Timestamp Validation

```bash
# Check for gaps >1 hour and time order
awk -F, 'NR>1 {print $1}' SENSOR_DATA.csv | head -20
```

Expected:
```
2026-06-29T06:15:00Z
2026-06-29T06:20:00Z
2026-06-29T06:25:00Z
...
```

- [ ] Timestamps monotonically increasing (no reversals)
- [ ] Intervals consistent (5-minute default, acceptable gaps during outages)
- [ ] Total span: 7+ days of data minimum

### Temperature Sanity Check

```bash
# Min/max per column
awk -F, 'NR>1 {print $2, $3, $4, $5}' SENSOR_DATA.csv | sort -n | head -5
awk -F, 'NR>1 {print $2, $3, $4, $5}' SENSOR_DATA.csv | sort -rn | head -5
```

- [ ] Inlet: 15–75°C (outside this range = sensor error or extreme weather)
- [ ] Outlet: 20–85°C (should be higher than inlet on clear days)
- [ ] Ambient: 10–50°C (outside range = sensor placement issue)
- [ ] Panel: 20–90°C (should spike during sun hours)

### Delta-T Verification

Calculate on 3 clear days (noon readings):

```bash
# Example: extract 3 noon readings across week
grep "T12:" SENSOR_DATA.csv | head -3
# Extract outlet − inlet for each
# Expected: 35–50°C on clear day, 100°F ambient
```

- [ ] Peak delta-T ≥ 30°C: **PASS** (meeting spec)
- [ ] Peak delta-T 20–30°C: ⚠️ (acceptable but lower efficiency)
- [ ] Peak delta-T < 20°C: **FAIL** (likely sensor or aerocement issue)

---

## Replication Assessment

Can a new builder follow this node's documentation and achieve similar results?

| Criterion | Assessment |
|-----------|------------|
| **BOM completeness** | Are all materials, costs, suppliers documented? Y/N/Partial |
| **Pour procedure** | Can someone follow the wet/dry mix ratios exactly? Y/N/Partial |
| **Curing timeline** | Daily photos + notes capture 21-day process? Y/N/Partial |
| **Sensor placement** | Diagram or GPS coordinates provided? Y/N/Partial |
| **Data publishing** | IPFS hash public? Zenodo DOI issued? Y/N |
| **Photos** | Key stages documented (Day 0, 7, 21, 28, sensor setup)? Y/N |

**Minimum pass:** ≥5/7 Partial or better

---

## Sign-Off Report

Create an issue in the repository:

```markdown
# Validation Report — [Node Name], [Location]

**Validator Name:** @[handle]  
**Inspection Date:** [DATE]  
**Node Status:** [Pre-curing / Curing / Dry-down / Operational]

## Physical Inspection
- Site: [South-facing / sheltered / exposure issues]
- Panel condition: [Describe porosity, cracks, coil access]
- Sensor placement: All 4 accessible and secured ✓/✗
- Labyrinth (if any): [Depth, soil type, compaction]

## Data Integrity
- Timestamp span: [START DATE] to [END DATE] ([# days])
- Readings missing: [N] ([% completion])
- OneWire sensors responding: [4/4 or list failures]
- Sensor drift (ref thermometer vs. logged): 
  - Inlet: ±[°C]
  - Outlet: ±[°C]
  - Ambient: ±[°C]

## Thermal Metrics
- Peak delta-T (clearest day): [°C] at [time]
- Average delta-T (3 best days): [°C]
- Peak outlet temp: [°C]
- Estimated power (if calculated): [W]

## Material Cost Verification
- Total spent: $[amount]
- Variance from $450 budget: $[+/- amount]
- All receipts available: Yes / No
- Unusual substitutions: [list or "none"]

## Replication Feasibility
- BOM complete & detailed: Yes / Partial / No
- Procedure documented: Yes / Partial / No
- Photo series (Days 0, 7, 21, 28): [count]/4
- IPFS/Zenodo published: Yes / No

## Recommendation

- [ ] **APPROVE** — Data meets spec, builder followed protocol, replicable
- [ ] **CONDITIONAL** — Minor issues (list): [issues]. Recommend [fix].
- [ ] **REJECT** — Major issues (list): [issues]. Cannot approve ACRE minting.

## Comments

[Additional observations, edge cases, climate-specific notes]

---

**Validator:** @[handle] | **Date:** [DATE]  
**Next validator needed:** Please inspect independently.
```

---

## Validator Nomination Process

### Step 1: Find Validators

**Are you willing to validate?**

Open an issue in the repository:

```
Title: Validator Application — [Your Location]
Labels: validator, community

I am applying to validate OpenRoot nodes in [REGION].

**Location:** [City, State/Country]  
**Availability:** [e.g., available for site visits within 50 miles, May–September]  
**Background:** [e.g., HVAC tech, builder, physicist, citizen scientist]  
**Commitment:** [How many nodes can you inspect per year?]

I have read and agree to the Validator Handbook.
```

**Repository maintainer** (@jesseray718) reviews and adds to the validator roster.

### Step 2: Builder Nominates Two

After completing build and 7-day dry-down, builder opens an issue:

```
Title: Validator Request — [Node Name], [Location Coordinates]

I am requesting two validators for my completed node.

**Node:** [Name]  
**Location:** [City/GPS]  
**Completion Date:** [DATE]  
**Climate Zone:** [Hot/dry, hot/humid, temperate, tropical, cold]  
**Data Status:** IPFS [QmXXXX], Zenodo DOI [10.5281/zenodo.XXXXXX]

Nominating:
1. @[validator1] — [reason, e.g., "30 miles away, HVAC background"]
2. @[validator2] — [reason]

Documentation: [link to BUILD_LOG.md, SENSOR_DATA.csv, etc.]
```

### Step 3: Validators Inspect & Report

Each validator completes on-site inspection and submits sign-off report (template above).

### Step 4: ACRE Eligibility

**Minting requirements met when:**
- ✅ Two independent validators approve
- ✅ Data passes schema & temperature sanity checks
- ✅ Replication score ≥5/7
- ✅ 21-day wet cure documented
- ✅ IPFS hash + Zenodo DOI published

**ACRE mint:** `[builder_handle]: 10,000 ACRE` (or bounty amount if competing for specific challenge)

---

## Validator Roster

Validators maintain their own public spreadsheet linked in community/VALIDATORS.md:

| Handle | Location | Climate Zones | Max Nodes/Year | Status |
|--------|----------|----------------|----------------|--------|
| @jesseray718 | Sikeston, MO | Hot/humid continental | 5 | Active |
| @[validator] | [City, ST] | [Zones] | [N] | [Active/Inactive] |

**Add yourself:** Fork, update the table, open PR.

---

## Conflict of Interest

**You cannot validate:**
- Your own nodes
- Nodes built by family/business partners
- Nodes in direct competition for a bounty you're also pursuing

**If nominated and conflict exists:** Politely decline in the nomination issue. Suggest an alternative validator.

---

## Validator Compensation

**Current (pre-ACRE launch):**
- Public recognition in build log
- Permanent credit in research commons
- Early access to ACRE when token launches

**Post-ACRE launch:**
- Validators earn **validation credits** (redeemable for ACRE or community goods)
- Proposed: 100 credits per thorough inspection = future benefit

---

## Resources

- **Validator Handbook:** community/VALIDATOR_HANDBOOK.md (this file)
- **Build Log Template:** build-log/node-zero/BUILD_LOG.md
- **Sensor Script:** scripts/sensor_log.sh
- **Contributing Rules:** community/CONTRIBUTING.md
- **Research Commons:** research/README.md

---

## Questions?

- **Unclear inspection step?** → Ask @jesseray718 in issues
- **Found data error?** → Document it; builder can re-run sensors
- **Validator issue?** → Open confidential issue, tag @jesseray718

---

**The commons grows when it's verified. Your inspection = permanent record. Thank you.**
