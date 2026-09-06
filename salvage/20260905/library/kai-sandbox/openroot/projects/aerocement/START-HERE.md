# AeroCement Node Zero — START HERE
## Pour Your First Thermal Node

**Status:** Node Zero in Sikeston, MO — June 2026  
**Builder:** Jesse McMillen  
**Est. Time:** 1 day pour + 21 days wet cure + 7 days dry-down  
**Cost:** ~$300–500 in material (concrete, copper, foam, fans, soil)

---

## The Panel You're Building

A volumetric solar air heater:
- **Input:** 931W of direct solar radiation per m²
- **Output:** 77°C air at 2,197W total utility (mechanical + thermal)
- **Material:** Open-cell aerocement (wet), copper coil inlet, thermosiphon circulation
- **Mounting:** South-facing, 45° tilt (latitude ± 15°)
- **Size:** 1.5m × 1.0m minimum (1.5 m²) for data significance

```
[SUN] → [Desiccant intake filter]
         ↓
    [PANEL ABSORBER]
    wet open-cell aerocement
    98% solar absorption
    ↓
    [Copper coil] → hot air out (77°C at 100°F ambient)
         ↓
    [Backplate] IR-reflective
    [Insulation] 4" minimum
    [Frame] Aluminum or wood
```

---

## Bill of Materials (Per 1.5 m² Panel)

### Aerocement Mix
| Item | Qty | Cost | Source |
|------|-----|------|--------|
| Portland cement (50 lb bag) | 1 | $8 | Home Depot |
| Xanthan gum powder | 0.5 lb | $15 | Amazon or local co-op |
| Dawn Ultra dish soap | 1 bottle | $4 | Dollar store |
| Sand (washed, fine) | 50 lbs | $5 | Landscape supply |
| Activated carbon (optional, 5 lbs) | 1 | $25 | Amazon |
| Water | Tap | $0 | — |

**Aerocement batch:** ~80 lbs dry mix → 150 lbs wet → ~0.10 m³ volume

### Frame & Housing
| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| 2×4 lumber (8 ft) | 4 | $20 | Pressure-treated or cedar |
| 1×6 lumber (8 ft) | 2 | $15 | For backing plate |
| Galvanized L-brackets | 8 | $15 | 3" × 3" |
| Concrete screws | 1 box | $8 | 3" length |
| Aluminum flashing (roll) | 1 | $25 | For moisture barrier |

### Thermal Components
| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| Copper coil (¾" OD, 15 ft) | 1 | $45 | HVAC supply |
| Thermometer wells (1" NPT) | 2 | $12 | Inlet + outlet |
| Pipe insulation (foam) | 20 ft | $8 | For inlet/outlet lines |
| Hose clamps (stainless) | 12 | $6 | Various sizes |

### Insulation & Surface
| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| Rigid foam insulation (4") | 2 sheets (R-24) | $40 | Rigid XPS, not spray |
| Aluminum reflective tape | 1 roll | $8 | For backplate |
| Black paint (exterior) | 1 qt | $10 | For absorber |
| Caulk (silicone, outdoor) | 2 tubes | $8 | For sealing |

### Sensors & Data Logging
| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| DS18B20 temp sensors | 4 | $12 | Inlet, outlet, ambient, panel |
| Raspberry Pi 4 (4GB) OR Arduino | 1 | $50–$15 | Pi for IPFS upload; Arduino for basic logging |
| USB power bank (20,000 mAh) | 1 | $25 | 48+ hour autonomy |
| Cat-5 cable (100 ft) | 1 | $8 | For sensor runs |
| Weatherproof junction box | 1 | $12 | Outdoor sensor hub |

### Misc
| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| Masking tape & plastic sheeting | 1 | $10 | Pour protection |
| Wire brush & chisel | 1 | $8 | Curing inspection |
| Thermometer (reference) | 1 | $5 | Hand verification |

**Total BOM: ~$360–$480**

---

## Pre-Pour Checklist (48 Hours Before)

- [ ] **Site selected:** South-facing, unobstructed 6 a.m.–4 p.m. direct sun
- [ ] **Frame built & square:** ±¼" tolerance over 1.5m × 1.0m footprint
- [ ] **Foam insulation cut to fit** underneath, back, and sides (¼" air gap on back)
- [ ] **Copper coil pressure-tested** at 50 PSI (find leaks before embedding)
- [ ] **Sensors calibrated:** DS18B20s in ice bath (0°C) and boiling water (100°C)
- [ ] **Soil excavated:** Labyrinth trench location marked (if building paired cold battery)
- [ ] **Water supply tested:** Garden hose ready for curing
- [ ] **Backup power:** Batteries charged, phone fully charged (for logging)
- [ ] **Safety:** Work gloves, dust mask, safety glasses, sunscreen

---

## The Pour (Day 1)

### Aerocement Mix Procedure

**Batch size:** 80 lbs dry → 150 lbs wet → covers ~0.10 m³ (sufficient for 1.5 m² × 4" thick panel)

1. **Dry mix in wheelbarrow:**
   - 50 lbs Portland cement
   - 50 lbs fine sand
   - 5 oz xanthan gum (weighed, not eyeballed)
   - Mix thoroughly until uniform (2 min with shovel)

2. **Wet the mix:**
   - Add water **slowly** (1 gallon at a time) while stirring
   - Target: **thick pancake batter** consistency (not soup, not dry)
   - You should see **visible air pores** form as you mix (xanthan gum stabilizes foam)
   - Total water: 8–12 gallons for 80 lbs dry mix

3. **Activate the foam:**
   - Pour **2 oz dish soap** (Dawn Ultra) into a separate bucket with 2 gallons water
   - Whisk **hard** for 2 minutes until bubble column forms (½ inch of stable bubbles on top)
   - Add soap-foam mixture to wet cement slowly while stirring gently
   - **DO NOT OVERMIX** — you want bubbles to stay intact
   - Final consistency: **airy slurry** with visible pores, not foam-solid

4. **Place immediately:**
   - Pour into frame over copper coil (coil should already be laid in position, not touching backplate)
   - Fill to **4–6 inches** depth, working out air pockets by gently tapping frame sides
   - **Level the surface** with a board screed
   - Cover with plastic to slow hydration (but do NOT seal completely — open-cell needs to breathe)

### Copper Coil Placement

- Lay coil in **snake pattern** (inlet left-bottom, outlet right-top) on thin gravel bed
- Keep coil **½ inch away from backplate** (air gap for radiative cooling on reverse)
- Secure coil with temporary spacers so it doesn't shift during pour
- **Inlet/outlet tubes** routed to junction box on side (sealed with caulk)

### Curing Starts Now

**Day 1–3 (Initial Set):**
- Mist the surface every 2 hours with water (phone alarm helps)
- Keep cover on but prop it ¼" open for air circulation
- Temperature: 65–75°F is ideal; if hotter, shade and mist more

**Day 4–21 (Wet Cure):**
- Mist 2× per day (morning, evening) until Day 21
- Remove cover after Day 3 — aerocement needs moisture to set
- Surface should never fully dry during this phase
- **Critical:** Do NOT let it get below 50°F or above 95°F if possible

**Day 22 onward (Dry-Down):**
- Stop misting — let it dry naturally
- **Allow 7–10 days dry time** before first sensor readings (residual moisture affects COP)
- Surface should be pale gray/white when fully cured

---

## Sensor Installation (Day 22+)

### DS18B20 Placement

Four sensors on each panel:

1. **Inlet (fresh air):** ½" into copper coil entry, shielded from direct sun
2. **Outlet (hot air):** ½" into copper coil exit, insulated from ambient
3. **Ambient (reference):** 6 feet away, 5 feet high, in shade with airflow
4. **Panel surface:** Embedded in final ½" of aerocement, painted black

### Wiring (Cat-5 Cable)

```
[Pi/Arduino GPIO]
    ↓
[4.7kΩ pull-up resistor to 3.3V]
    ↓
[DS18B20 data line] ← all 4 sensors on same wire (OneWire protocol)
    ↓
[Weatherproof junction box] ← silicone potting
    ↓
[Run to shaded sensor hub]
```

**Raspberry Pi setup (if using):**
```bash
# Enable OneWire in /boot/config.txt
dtoverlay=w1-gpio,gpiopin=4

# Test sensors
ls /sys/bus/w1/devices/  # should list 28-XXXX entries
cat /sys/bus/w1/devices/28-XXXX/w1_slave  # read temp
```

### Data Logging Script

See **scripts/sensor_log.sh** — runs every 5 minutes, outputs CSV:

```
timestamp,inlet_C,outlet_C,ambient_C,panel_C,solar_irradiance_W_m2
2026-06-28T06:15:00Z,18.5,19.2,20.1,18.8,0
2026-06-28T06:20:00Z,18.6,22.3,20.2,42.5,185
```

**Auto-upload to IPFS** after 1,000 readings (~83 hours of data).

---

## First 48 Hours of Operation (Commissioning)

**Goal:** Establish baseline delta-T and verify heat capture

1. **Clear morning (6 a.m.–noon):**
   - Log every 5 minutes
   - Record: inlet temp, outlet temp, ambient temp, time of day
   - Calculate delta-T = outlet − inlet
   - At 100°F ambient + full sun, expect **35–50°C rise**

2. **Calculate instantaneous power:**
   - Air volume flow rate Q (CFM) = measured by anemometer or estimated from fan specs
   - Delta-T (°C)
   - Power = Q × 1.2 kg/m³ × 1.006 kJ/(kg·K) × ΔT
   - **Expected: 500–800W at noon on clear day**

3. **Verify copper coil circulation:**
   - Feel inlet and outlet tubes (should be noticeably warm)
   - No ice or blockage at outlet (frost means desiccant failure elsewhere)
   - Thermometer wells should read within 2°C of sensor values

4. **Log everything:**
   - First 24 hours → bounties/node-zero/FIRST_48H.csv
   - Photos of panel, sensor setup, thermometers
   - Ambient conditions (humidity, cloud cover, time of day)

---

## Data Submission to Research Commons

**After Day 28 (7-day dry-down complete):**

1. **Bundle files:**
   - build-log/node-zero/BUILD_LOG.md (daily photos, curing notes)
   - build-log/node-zero/SENSOR_DATA.csv (21 days of readings post-dry-down)
   - build-log/node-zero/THERMAL_ANALYSIS.md (calculated delta-T, COP, efficiency)
   - build-log/node-zero/PHOTOS/ (pour, curing, final installation)

2. **Calculate verified metrics:**
   - **Peak COP** = total useful output (mechanical + thermal) / solar input
   - **Average delta-T** across 3 clear days
   - **Material cost per m²**
   - **Replication time** (hours to pour)

3. **Publish to IPFS:**
   ```bash
   scripts/sensor_log.sh --publish
   # Returns: ipfs://QmXXXXXX (immutable hash)
   ```

4. **Register DOI:**
   - Upload to Zenodo (zenodo.org) with IPFS hash
   - Cite as: "OpenRoot Node Zero, Sikeston MO (2026), DOI: 10.5281/zenodo.XXXXXXX"

5. **Open PR to research/:**
   ```
   pr: Add Node Zero climate data — Sikeston, MO (hot/humid)
   - Verified 931W → 2,197W per m²
   - 21-day wet cure, passive COP 8,544
   - Replication: 8 hours pour, $450 material
   ```

6. **Request validators:**
   - Issue: "Validator Request — Node Zero, Sikeston MO, 38.49°N"
   - Two independent validators sign off
   - Your build enters permanent research commons
   - **ACRE token pending** (3 validated nodes to launch)

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Aerocement won't rise (dense, not porous) | Xanthan gum too low or water too high | Restart batch: add xanthan first, then water |
| Copper coil freezes at night | Convection loop draining to cold battery when off | Add check valve or drain valve |
| Outlet temp not rising above 40°C at noon | Solar absorber too wet or low-emissivity coating | Wait 2 more days (curing). Verify absorber is BLACK |
| Sensor reads -127°C | OneWire communication loss | Check pull-up resistor, Cat-5 continuity |
| Mold on curing surface | High humidity + poor airflow | Increase misting frequency, add fan nearby |
| Cracking on Day 10–14 | Too-fast dry-down | Resume misting, shade panel |

---

## Next Steps After First Node

1. **Document failures** — publish them. Data > ego.
2. **Invite second builder** — send START-HERE.md to someone 500 miles away with different climate.
3. **Compete for bounties** — scale to Stirling scooter (projects/hearth/).
4. **Validate others** — become a validator (community/VALIDATOR_HANDBOOK.md).

---

## References

- **Thermal Loop Diagram:** kai/KAI_SYSTEM_PROMPT.md (lines 15–27)
- **Hard Constraints:** community/CONTRIBUTING.md (lines 20–27)
- **Sensor Schema:** scripts/sensor_log.sh (data format)
- **Climate Trials Map:** research/README.md (validation needed)
- **Bounty Details:** bounties/README.md

---

**Build it. Log it. Publish it. The project succeeds when it no longer needs Jesse McMillen.**
