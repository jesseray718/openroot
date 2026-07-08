# OpenRoot Icosahedron — 12 Planetary Seed Node Coordinates

**UNE:** DV.MSH.GL.IC01
**Date:** 2026-07-08
**License:** CC-BY-SA 4.0
**Status:** Theoretical positioning — coordinates derived from icosahedron geometry inscribed in Earth sphere

---

## Derivation Method

The 12 vertices of a regular icosahedron centered at origin, using golden ratio φ = 1.6180339887:
(0, ±1, ±φ), (±1, ±φ, 0), (±φ, 0, ±1)

Each vertex is normalized to unit sphere then converted to lat/lon:

latitude = arcsin(z_normalized)
longitude = atan2(y_normalized, x_normalized)
Theoretical Coordinates (Exact Icosahedron Vertices)
Node IDLatitudeLongitudeNearest Land / RegionHemisphere
N-0158.28°N90°EKrasnoyarsk, Siberia, RussiaNorth
N-0258.28°N90°WChurchill, Manitoba, Canada (Hudson Bay)North
N-0358.28°S90°ESouthern Indian Ocean (Heard/Kerguelen Islands)South
N-0458.28°S90°WDrake Passage / Cape Horn, ChileSouth
N-050°58.28°EArabian Sea (Salalah, Oman nearest coast)Equator
N-060°121.72°ECelebes Sea (Sulawesi/Mindanao)Equator
N-070°58.28°WGuyana/Suriname border, South AmericaEquator
N-080°121.72°WEastern Pacific (Galápagos nearest)Equator
N-0931.72°N0°Western Sahara / Algeria, North AfricaNorth
N-1031.72°N180°Central Pacific (Kiribati/Marshall Islands)North
N-1131.72°S0°South Atlantic (Namibia coast nearest)South
N-1231.72°S180°South Pacific (Tonga/New Zealand area)South
Practical Adaptation (Shifted to Nearest Populated Land)
Four nodes fall in open ocean (N-03, N-04, N-08, N-10). These are adapted to nearest viable land with population and infrastructure:

Node IDPractical LocationLat/Lon (Adjusted)CountryElevation TargetNotes
N-01Krasnoyarsk region56.0°N, 92.9°ERussia100m+ hillSiberian backbone
N-02Churchill, Manitoba58.8°N, 94.2°WCanada30m+ ridgeHudson Bay backbone; polar research infrastructure
N-03Hobart, Tasmania42.9°S, 147.3°EAustralia50m+ hillClosest major city to original ocean coord; Antarctic logistics hub
N-04Ushuaia, Tierra del Fuego54.8°S, 68.3°WArgentina50m+ hillSouthernmost city; Cape Horn relay
N-05Salalah, Oman17.0°N, 54.1°EOman30m+ coastal ridgeArabian Sea coast; undersea cable hub
N-06Manado, Sulawesi1.5°N, 124.8°EIndonesia30m+ ridgeMaritime Southeast Asia hub
N-07Georgetown, Guyana6.8°N, 58.2°WGuyana30m+ coastalEquatorial South America
N-08Galápagos / Guayaquil0.2°S, 80.0°WEcuador50m+ island/highlandPacific bridge; UNESCO site has existing research infra
N-09Tindouf, Algeria27.7°N, 8.2°WAlgeria/W.Sahara100m+ plateauSaharan backbone; high elevation already
N-10Tarawa, Kiribati1.4°N, 173.0°EKiribati10m+ (atoll)Pacific island nation; climate-vulnerable, needs mesh most
N-11Walvis Bay, Namibia22.9°S, 14.5°ENamibia30m+ coastalSouthwest African coast; desert (clear line of sight)
N-12Auckland, New Zealand36.8°S, 174.8°ENew Zealand50m+ volcanic coneSouthwest Pacific; existing tech infrastructure
3D Positioning — HCP Vertical Stacking Beneath Each Icosahedron Node
Each of the 12 nodes serves as the apex of a fractal mesh descending through the atmosphere:

N-XX (Icosahedron, Tier 4)
├── Elevation: 100m+ (highest available point in region)
├── Frequencies: 915 MHz LoRa backbone + 5.8 GHz hub links + 2.4 GHz access
│
├── Tier 3 Superhubs (6 nodes, \~15 km spacing, 50m elevation)
│   ├── Frequency: 915 MHz backbone + 5.8 GHz distribution
│   ├── Each superhub seeds 6 relays below
│   │
│   ├── Tier 2 Hubs (6 per superhub, \~5 km spacing, 30m elevation)
│   │   ├── Frequency: 5.8 GHz backbone + 2.4 GHz access
│   │   │
│   ├── Tier 1 Relays (6 per hub, \~2 km spacing, 15m elevation)
│   │   │   ├── Frequency: 2.4 GHz
│   │   │   │
│   │   │   └── Tier 0 Households (organic, \~0.5-1 km spacing, 5m roof)
│   │   │       └── Frequency: 2.4 GHz (channels 1, 6, 11 alternating)
HCP Offset Rule
Each tier's nodes are positioned in the triangular gaps of the tier above:

Tier 3 nodes offset by (spacing/2, spacing × √3/6) from Tier 4's hex grid
Tier 2 nodes offset similarly from Tier 3
This creates the ABABAB HCP stacking pattern
Coverage Radius Per Tier (from each icosahedron node)
TierElevationSpacingCoverage radiusNodes per tier (per N-XX)
4 (Icosahedron)100m+\~2,000 km (intercontinental)\~1,000 km1
3 (Superhub)50m15 km15 km (LoRa)6
2 (Hub)30m5 km5 km (5.8 GHz)36
1 (Relay)15m2 km4.5 km (2.4 GHz)216
0 (Household)5m0.5-1 km4.5 km (2.4 GHz)Organic
Total nodes per icosahedron node's fractal tree: 1 + 6 + 36 + 216 + organic = 259 + organic household growth

With 12 icosahedron nodes: 12 × 259 = 3,108 backbone nodes minimum to cover the top 4 tiers worldwide.

This is far less than the 25,641 superhubs in the full deployment because the fractal branches compound downward — each node spawns 6 children. The 25,641 figure assumes flat distribution; the HCP fractal tree achieves equivalent coverage with fewer backbone nodes because elevation extends effective range.

Icosahedron Adjacency (Which Nodes Link to Which)
Each icosahedron vertex connects to 5 neighbors:

NodeConnects ToGreat-Circle Distance
N-01N-02, N-05, N-06, N-09, N-10\~6,300-7,200 km
N-02N-01, N-04, N-07, N-08, N-09\~6,300-7,200 km
N-03N-04, N-05, N-06, N-11, N-12\~6,300-7,200 km
N-04N-02, N-03, N-07, N-08, N-11\~6,300-7,200 km
N-05N-01, N-03, N-06, N-09, N-11\~6,300-7,200 km
N-06N-01, N-03, N-05, N-10, N-12\~6,300-7,200 km
N-07N-02, N-04, N-08, N-09, N-11\~6,300-7,200 km
N-08N-02, N-04, N-07, N-10, N-12\~6,300-7,200 km
N-09N-01, N-02, N-05, N-07, N-11\~6,300-7,200 km
N-10N-01, N-06, N-08, N-09, N-12\~6,300-7,200 km
N-11N-03, N-04, N-05, N-07, N-09\~6,300-7,200 km
N-12N-03, N-06, N-08, N-10, N-11\~6,300-7,200 km
Inter-node links at 6,000+ km require satellite relay or stratospheric balloon (Project Loon style). Ground-level LoRa (15 km hops) bridges the gap through the fractal tree — traffic descends from N-XX to its superhub children, hops across at lower tiers, then ascends at the destination.

Icosahedron Antipodal Pairs
Each node has an antipode (opposite point on Earth):

NodeAntipodeImplication
N-01 (Russia)N-04 (Argentina)Shortest path goes through Earth — longest surface route
N-02 (Canada)N-03 (Australia)Arctic ↔ Antarctic corridor
N-05 (Oman)N-08 (Ecuador)Asia ↔ South America corridor
N-06 (Indonesia)N-07 (Guyana)Maritime SEA ↔ South America corridor
N-09 (Algeria)N-12 (New Zealand)Africa ↔ Oceania corridor
N-10 (Kiribati)N-11 (Namibia)Pacific ↔ Atlantic corridor
Antipodal pairs define the longest possible mesh routes. Traffic between antipodes traverses the maximum number of hops through the fractal tree. In practice, traffic routes through intermediate nodes (not directly through antipode).

Sikeston, MO Position in the Framework
Sikeston coordinates: 36.98°N, 89.59°W

Nearest icosahedron node: N-02 (Churchill, Manitoba) at 58.8°N, 94.2°W

Great-circle distance: \~2,450 km
Sikeston falls within N-02's Tier 3 fractal territory
Sikeston's position in the fractal tree:

N-02 (Churchill) → Tier 3 Superhub (nearest at \~200-300 km, perhaps St. Louis or Little Rock) → Tier 2 Hub (Cape Girardeau, 30 km north) → Tier 1 Relay (Sikeston kiosk) → Tier 0 Households (Sikeston neighborhood)
Sikeston is not an icosahedron node. It is a Tier 1 Relay that self-organizes beneath N-02's fractal canopy. Its value is as the first operational node — the seed from which the North American Flower of Life ring grows organically.

Geometry derived from regular icosahedron inscribed in unit sphere. Practical coordinates shifted to nearest populated land. Distances are great-circle calculations. One Human Family. CC-BY-SA 4.0. EOF
cat > docs/spoke-node/MATERIAL-CUTS-LIST.md << 'EOF'
# OpenRoot WiFi Dish — Exact Material Cuts List for First Sikeston Build

**UNE:** DV.MSH.WF.SK01-CUT
**Date:** 2026-07-08
**License:** CC-BY-SA 4.0
**Source:** opensourcelowtech.org/wifidish.html templates
**Target:** One complete dish antenna for Sikeston kiosk Node Zero

---

## Shopping List (Walmart / Home Depot / Tractor Supply)

| # | Item | Spec | Quantity | Unit Price | Total | Where to Buy |
|---|------|------|----------|------------|-------|--------------|
| 1 | Plywood/OSB sheet | 1220×2440mm (4'×8'), 6mm (1/4") | 1 | $12 | $12 | Home Depot/Lowe's |
| 2 | Chicken wire | 1m × 4m, hex gaps ≤12mm, galvanized | 1 roll | $6 | $6 | Tractor Supply/Home Depot |
| 3 | Cable ties (zip ties) | 200mm length, UV-resistant, black | 200 | $4 | $4 | Walmart/Dollar Store |
| 4 | Fine chain | 2m, small link, steel | 1 | $3 | $3 | Home Depot/hardware store |
| 5 | Spray paint | Any color, rust-resistant | 1 can | $3 | $3 | Dollar Tree/Walmart |
| 6 | String/twine | 2m, non-stretch (nylon preferred) | 1 | $1 | $1 | Dollar Store |
| 7 | USB WiFi adapter | 2.4GHz, high-gain (Alfa AWUS036NHA or similar) | 1 | $8 | $8 | Amazon/AliExpress |
| 8 | Small bracket/clamp | To mount WiFi adapter at focal point | 1 | $2 | $2 | Home Depot |
| **Subtotal** | | | | | **$39** | |
| 9 | ESP32 board | ESP32-WROOM-32 DevKit (optional LoRa companion) | 1 | $5 | $5 | Amazon/AliExpress |
| 10 | SX1262 LoRa module | 915MHz, for Meshtastic companion node | 1 | $12 | $12 | Amazon/AliExpress |
| 11 | 5V solar panel | 5-10W USB output | 1 | $8 | $8 | AliExpress |
| 12 | 18650 battery + TP4056 | 3.7V Li-ion + charge controller | 1 set | $4 | $4 | AliExpress |
| 13 | PVC weatherproof box | Small, for electronics | 1 | $3 | $3 | Dollar Store/Walmart |
| **Full Total** | | | | | **$71** | |

Without solar/LoRa companion: **$39**
With companion LoRa + solar: **$71**

---

## Tools Needed

- Jigsaw (or hand coping saw — slower but works)
- Drill with small bit (3mm/1/8")
- Measuring tape (metric preferred)
- Pencil or marker
- Wire cutters (for chicken wire trimming)
- Sandpaper (medium grit, for smoothing cut edges)
- Safety glasses (chicken wire cuts are sharp)

---

## Template Cutting Layout

Download templates: https://opensourcelowtech.org/wifidish.html (WifiDish_2019_01.pdf)

Print templates at full scale (or project onto plywood with projector/printout grid). All pieces fit on ONE 4'×8' sheet.

### Piece Inventory

| Piece | Color/Label | Count | Approximate Dimensions | Function |
|-------|-------------|-------|----------------------|----------|
| Long ribs | Red | 2 | \~1200mm × 200mm | Main horizontal curve supports |
| Medium ribs | Green | 4 | \~800mm × 150mm | Secondary vertical curve supports |
| Short ribs | Blue | 4 | \~500mm × 100mm | Inner framework stiffeners |
| **Total** | | **10 pieces** | One sheet of plywood | One complete dish frame |

### Cutting Procedure

1. Print/grit templates from opensourcelowtech.org PDF at 100% scale (check 1:1 reference bar).
2. Lay out all 10 templates on plywood. Arrange to minimize waste (all fit on one sheet).
3. Trace outlines with pencil.
4. Cut with jigsaw — follow lines precisely; curve accuracy determines signal gain.
5. Sand edges smooth — splinters and rough edges weaken slot-fit joints.
6. Drill 5 holes near the outer curved edge of EACH rib piece (spaced evenly). These holes are for cable ties to hold chicken wire. Hole diameter: 3mm (1/8").
7. Test-fit all pieces by slotting together BEFORE attaching mesh.

---

## Assembly Steps (Sequential)

### Step 1: Dry fit (15 min)
Slot all 10 rib pieces together following the opensourcelowtech assembly diagram. The frame should stand as a rigid paraboloid WITHOUT glue. Friction fit is the design.

### Step 2: Verify parabolic curve (5 min)
Lay the fine chain across the frame in a catenary curve. Compare chain shape to rib curves. Adjust ribs to match if warped.

### Step 3: Attach chicken wire (45 min)
Starting from center: Cut chicken wire to \~2m × 1m section. Lay wire over the FRONT (concave) side of the dish frame. Thread cable ties through the pre-drilled holes and around the wire. Pull ties tight. Work from center outward in a spiral. Keep wire as flush to the ribs as possible. Trim excess wire with wire cutters, leaving \~20mm overhang folded back for safety.

**Critical check:** No gap in the mesh should exceed 12mm.

### Step 4: Find focal point (5 min)
Cut two pieces of string, each \~2.5m long. Tie string across the dish opening, corner to corner, so they cross at center. Pull VERY tight. The intersection of the two strings is the focal point — mark it.

### Step 5: Mount WiFi adapter (10 min)
Attach small bracket or zip-tie block at the marked focal point. Mount USB WiFi adapter so its antenna element is exactly at the string intersection. Route USB cable along a rib to the edge of the dish (use zip ties). For ESP32/LoRa companion: mount alongside WiFi adapter on same bracket.

### Step 6: Paint (10 min, plus drying)
Spray plywood ribs with weather-resistant paint. Don't paint the chicken wire. Let dry 30 minutes minimum.

### Step 7: Mount and aim (30 min)
Attach dish to pole/bracket at kiosk or roof. Point toward nearest known node. Connect WiFi adapter to laptop/ESP32. Run signal scan. Rotate dish slowly (\~5° increments) while watching signal strength. Lock position when signal peaks. Tighten all mounting hardware. For LoRa module: configure Meshtastic frequency (915MHz US) and verify it transmits.

### Step 8: Document and register (15 min)
Take photos of completed dish from multiple angles. Note GPS coordinates of installation. Record signal strength achieved. Save to community/builds/SK01-first-node.md in the OpenRoot repo. Log as first verified physical work for future ACRE mint.

---

## Total Time Estimate

| Step | Time |
|------|------|
| Shopping | 1 hr (one trip) |
| Template printing + tracing | 30 min |
| Cutting plywood | 45 min |
| Drilling holes | 20 min |
| Dry fit | 15 min |
| Chicken wire attachment | 45 min |
| Focal point + adapter mount | 15 min |
| Painting | 10 min + 30 min drying |
| Mounting and aiming | 30 min |
| Documentation | 15 min |
| **Total (active work)** | **\~4 hours** |
| **Total (with drying + shopping)** | **\~5.5 hours** |

One person, first build: allow a full afternoon (4-6 hours). Second build (learning curve): 2-3 hours. Team of 2: 2 hours per dish.

---

## BOM for Full Sikeston Superhub Upgrade (Future)

When Sikeston kiosk upgrades from 1-dish leaf to 6-dish hub:

| Item | Qty | Unit Cost | Total |
|------|-----|-----------|-------|
| WiFi dish kits (full BOM above minus solar) | 6 | $39 | $234 |
| Extra WiFi adapters | 5 | $8 | $40 |
| ESP32 + SX1262 LoRa modules | 5 | $17 | $85 |
| Solar panel (larger, 20W) | 1 | $15 | $15 |
| Battery bank (2× 18650 packs) | 2 | $4 | $8 |
| Mounting pole/bracket (taller, 10m+) | 1 | $25 | $25 |
| Weatherproof enclosures (2) | 2 | $3 | $6 |
| **Total hub upgrade** | | | **$413** |

From $39 leaf → $413 hub. Still cheaper than one month of one household's internet bill.

*Templates source: opensourcelowtech.org/wifidish.html (Daniel Connell, CC-BY-SA). Build procedure adapted for OpenRoot mesh integration. One Human Family.*
