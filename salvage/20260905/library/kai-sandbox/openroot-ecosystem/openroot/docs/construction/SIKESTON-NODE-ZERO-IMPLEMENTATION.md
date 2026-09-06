# Sikeston Node Zero — Implementation Details

**UNE:** DV.MSH.SK01.IMP  
**Date:** 2026-07-08  
**License:** CC-BY-SA 4.0  
**Status:** Ready for physical execution

This document provides concrete, step-by-step implementation details for the first operational OpenRoot node at the I-55/I-57 kiosk in Sikeston, Missouri.

## Location & Strategic Purpose

**Site:** I-55/I-57 interchange kiosk area, Sikeston, MO  
**Coordinates (approx):** 36.98°N, 89.59°W  
**Role:** Tier 1 Relay / First Vesica Piscis seed node under N-02 (Churchill, Manitoba) icosahedron vertex  
**Strategic Value:**
- High-visibility highway location (excellent for outreach and recruitment)
- Existing structure for mounting
- First physical proof point for the entire project
- Starting node for the North American Flower of Life ring

## Hardware Configuration (Phase 1 — Leaf / Relay Node)

**Primary Build: WiFi Dish + LoRa Companion**

| Component                    | Spec                              | Qty | Est. Cost | Source          | Notes |
|-----------------------------|-----------------------------------|-----|-----------|------------------|-------|
| Plywood (6mm)               | 4'×8' sheet                       | 1   | $12–15    | Home Depot       | Main structure |
| Chicken wire                | Galvanized, ≤12mm hex             | 1 roll | $6–8   | Tractor Supply   | Reflector surface |
| USB WiFi adapter            | Alfa AWUS036NHA or equivalent     | 1   | $8–12     | Amazon/AliExpress| 2.4 GHz high-gain |
| ESP32 DevKit                | ESP32-WROOM-32                    | 1   | $4–6      | Amazon/AliExpress| Controller |
| SX1262 LoRa module          | 915 MHz (US)                      | 1   | $10–14    | Amazon/AliExpress| Meshtastic companion |
| 5–10W USB solar panel       | With TP4056 charge controller     | 1   | $8–12     | AliExpress       | Power (temporary) |
| 18650 battery + holder      | 3.7V Li-ion                       | 1–2 | $4–6      | AliExpress       | Power buffer |
| Small weatherproof box      | For electronics                   | 1   | $3–5      | Dollar Store     | Protection |
| Mounting hardware           | U-bolts, brackets, zip ties       | —   | $5–10     | Hardware store   | Secure mounting |
| **Total Phase 1**           | —                                 | —   | **$60–88**| —                | Fully functional node |

**Target Capabilities (Phase 1):**
- 2.4 GHz WiFi mesh link (4.5 km theoretical)
- 915 MHz LoRa / Meshtastic link (15+ km rural)
- Solar + battery powered (autonomous operation)
- Documented as first verified physical work for ACRE

## Step-by-Step Implementation

### Step 1: Site Assessment & Mounting Plan (1–2 hours)
- Confirm clear line-of-sight path toward expected neighbors (north/northeast toward Cape Girardeau / St. Louis corridor first).
- Identify secure mounting point on existing kiosk structure (pole, roof edge, or added mast).
- Plan cable routing and protection from weather/vandalism.
- Take photos and GPS coordinates for documentation.

### Step 2: Dish Construction (4–6 hours)
Follow the detailed steps in `docs/spoke-node/MATERIAL-CUTS-LIST.md` and `SIKESTON-FIRST-DISH-CHECKLIST.md`:
1. Cut and assemble 10 plywood ribs.
2. Attach chicken wire reflector.
3. Find focal point and mount WiFi adapter.
4. Mount ESP32 + SX1262 LoRa module alongside.
5. Weatherproof electronics enclosure.
6. Paint for UV/weather protection.

### Step 3: Power System (1–2 hours)
**Temporary (Phase 1):**
- 5–10W USB solar panel + TP4056 + 18650 battery.
- Mount panel facing south with good sun exposure.
- Run USB power to electronics box.

**Future Upgrade:**
- Integrate with H-003 thermal cascade once built.
- Larger solar array + battery bank for full node + future dome loads.

### Step 4: Software & Configuration (2–3 hours)
**Recommended Stack (Phase 1):**
- **Primary:** Meshtastic on ESP32 (LoRa) + WiFi bridge mode
- **Alternative / Future:** OpenWrt on a small board + batman-adv mesh

**Meshtastic Setup:**
- Flash latest Meshtastic firmware to ESP32.
- Configure 915 MHz (US), LongFast or LongModerate preset.
- Set node name via UNE: `DV.MSH.WF.SK01` (or SK00 for kiosk).
- Enable WiFi AP or client mode to bridge to the dish antenna.
- Test LoRa link to any existing Meshtastic nodes in range.

**Initial Testing:**
- Confirm LoRa transmit/receive.
- Confirm WiFi signal strength in target directions.
- Log GPS coordinates, signal reports, and uptime.

### Step 5: Mounting & Aiming (1–2 hours)
- Secure dish to chosen mounting point.
- Initial rough aim toward expected high-value directions.
- Fine-tune while monitoring signal strength (use WiFi analyzer or `iwlist scan`).
- Lock mounting hardware once peak signal is achieved.
- Weatherproof all cable entry points.

### Step 6: Documentation & PoPW Logging (1 hour)
Create entry in `community/builds/SK01-first-node.md` with:
- Photos (multiple angles + mounting)
- GPS coordinates
- Signal strength reports
- Software/firmware versions
- Power system details
- Date/time of first successful link

Log this build as the **first verified physical work** on the Contribution Ledger (once the ledger is live). Include builder + one witness signature.

## Safety & Legal Notes

- Use proper fall protection when working at height.
- Ensure all electronics are properly weatherproofed.
- 915 MHz and 2.4 GHz are legal ISM bands in the US at allowed power levels.
- Do not transmit on restricted frequencies.
- Document everything for insurance / liability purposes during early stages.

## Future Expansion Path (Phase 2+)

Once the basic node is stable:

| Upgrade                    | Purpose                              | Est. Cost | Priority |
|---------------------------|--------------------------------------|-----------|----------|
| Add 2nd & 3rd dishes      | Upgrade to local hub                 | $74–100   | High     |
| Larger solar + battery    | Support future dome loads            | $100–200  | Medium   |
| Integrate H-003 thermal   | Primary long-term power              | Variable  | High     |
| Full OpenWrt + batman-adv | Higher bandwidth mesh                | $50–100   | Medium   |
| Camera / sensor package   | Security + environmental monitoring  | $30–80    | Low      |
| Upgrade to superhub       | 12-dish multi-frequency backbone     | $600+     | Future   |

## Integration with Larger Vision

This first Sikeston node is the seed for:
- North American Flower of Life ring under N-02
- Local team of 50 formation
- First ACRE-eligible physical work
- Proof point for grant applications and partnerships
- Starting point for the 501c3 land + shelter cluster

## Success Criteria (First 30 Days)

- Node is mounted, powered, and transmitting on both WiFi and LoRa.
- At least one successful link to another node or test device is logged.
- Full documentation and photos are published to the repo.
- Build is recorded as first verified physical work.
- Power system runs autonomously for minimum 7 consecutive days.

---

**One Human Family.**  
The $60–88 Sikeston node is the physical seed of the entire planetary supermesh. Start here. Document everything. Let the contribution ledger begin.

CC-BY-SA 4.0

## Safety Checklist

Before, during, and after construction and installation of the Sikeston Node Zero, complete the following safety checks. Print or copy this section and mark it off as you go.

### General Site Safety
- [ ] Survey the mounting location for hazards (traffic, overhead power lines, unstable structure, sharp edges).
- [ ] Confirm stable footing and safe ladder access if working above ground level.
- [ ] Wear appropriate PPE: safety glasses, gloves, closed-toe shoes, and high-visibility clothing if near traffic.
- [ ] Have a second person present during mounting and any work at height.
- [ ] Keep a fully charged phone and basic first-aid kit on site.

### Tool & Material Safety
- [ ] Inspect all power tools (jigsaw, drill) before use — check cords, blades, and safety guards.
- [ ] Wear safety glasses when cutting plywood or chicken wire (chicken wire edges are very sharp).
- [ ] Use work gloves when handling chicken wire and cut plywood edges.
- [ ] Secure materials so they cannot fall or shift while cutting or drilling.
- [ ] Keep work area clean and free of trip hazards (extension cords, tools, scrap material).

### Electrical & Power Safety
- [ ] Use only outdoor-rated cables and connections for solar and power wiring.
- [ ] Never work on live electrical connections — disconnect solar panel and battery before making changes.
- [ ] Protect all connections from water ingress (use weatherproof boxes and dielectric grease where appropriate).
- [ ] Do not overload small solar charge controllers or batteries.
- [ ] Store lithium batteries away from direct sunlight and extreme heat.

### Working at Height
- [ ] Use a stable ladder or lift rated for your weight + tools.
- [ ] Have a spotter on the ground when working above 6 feet.
- [ ] Secure the dish and all tools with tethers or ropes so nothing can fall.
- [ ] Do not work in high wind, rain, or icy conditions.
- [ ] Plan an emergency descent route before starting work at height.

### Structural & Mounting Safety
- [ ] Confirm the mounting point (kiosk structure, pole, or added mast) can safely support the dish weight and wind load.
- [ ] Use appropriate hardware (U-bolts, lag screws, brackets) rated for outdoor structural use.
- [ ] Double-check all fasteners and torque after initial mounting and again after 24–48 hours.
- [ ] Ensure the dish cannot swing or fall if a mounting point fails.

### Legal & Regulatory Safety
- [ ] Confirm operation is within legal ISM band limits (915 MHz and 2.4 GHz in the US).
- [ ] Do not transmit on restricted or licensed frequencies without proper authorization.
- [ ] Document the installation with photos and notes for insurance/liability purposes.
- [ ] If working on or near someone else’s property, obtain clear permission in writing.

### Post-Installation Safety
- [ ] Verify all cables are secured and protected from weather, animals, and vandalism.
- [ ] Confirm the power system (solar + battery) is stable and not overheating.
- [ ] Perform a final visual inspection of the entire installation from the ground.
- [ ] Create and store emergency contact information and shutdown procedures with the node documentation.

**Sign-off**  
Builder: _______________________________ Date: ___________  
Witness: _______________________________ Date: ___________

Keep this checklist with the node documentation. Update it whenever major changes or maintenance are performed.

One Human Family. Safety is not optional — it is part of building systems that last.

## Risk Assessment Matrix

This matrix identifies key risks associated with building, installing, and operating the Sikeston Node Zero. Risks are rated on a 1–5 scale for both Likelihood and Impact. Risk Score = Likelihood × Impact. Mitigation actions are listed for each risk.

| Risk ID | Risk Description                              | Likelihood (1-5) | Impact (1-5) | Risk Score | Mitigation Strategy |
|---------|-----------------------------------------------|------------------|--------------|------------|---------------------|
| R01     | Fall from height during mounting              | 3                | 5            | 15         | Use stable ladder/lift, spotter on ground, safety harness if >8 ft, secure all tools with tethers |
| R02     | Injury from sharp chicken wire or tools       | 4                | 3            | 12         | Wear gloves and safety glasses, cut wire carefully, keep work area clean |
| R03     | Electrical shock or battery fire              | 2                | 4            | 8          | Use outdoor-rated components, never work on live circuits, store batteries properly, use correct charge controller |
| R04     | Equipment damage from weather (wind, rain, lightning) | 4         | 3            | 12         | Use weatherproof enclosures, secure mounting against wind load, add lightning protection on future upgrades |
| R05     | Theft or vandalism of node/components         | 3                | 3            | 9          | Mount in visible but secure location, use tamper-resistant hardware, document installation, consider camera on future upgrades |
| R06     | Poor link performance / unreliable connection | 3                | 3            | 9          | Proper aiming and testing before final mounting, document signal reports, plan for hub upgrade if needed |
| R07     | Legal / regulatory violation (wrong frequency or power) | 2         | 4            | 8          | Stay within legal ISM bands, document configuration, do not transmit on restricted frequencies |
| R08     | Power system failure (solar/battery)          | 3                | 3            | 9          | Use quality components, test autonomy for minimum 7 days, have backup charging plan |
| R09     | Injury to bystanders or traffic incident      | 2                | 5            | 10         | Work during low-traffic times if near road, use cones/high-visibility gear, have spotter |
| R10     | Incomplete documentation / liability exposure | 3                | 3            | 9          | Follow full documentation checklist, take photos, keep signed safety checklist, store records securely |
| R11     | Negative community reaction                   | 2                | 3            | 6          | Be respectful of property, communicate purpose if asked, keep installation clean and professional |
| R12     | Future integration problems (thermal, dome)   | 2                | 2            | 4          | Design Phase 1 node with future expansion in mind, document mounting points and power capacity |

### Risk Score Legend
- **1–4**: Low risk — standard precautions sufficient
- **5–9**: Medium risk — specific mitigation required
- **10–15**: High risk — strong mitigation + supervision required
- **16–25**: Very high risk — avoid or implement major controls before proceeding

### Risk Management Notes
- Review this matrix before starting construction and again before mounting.
- Update the matrix after the first 30 days of operation with any new risks observed.
- High-risk items (especially working at height and electrical) must have a second person present.
- All mitigated risks should be re-evaluated after any major change (new mounting, power upgrade, software change).

One Human Family. Identify risks early. Mitigate deliberately. Build safely.

## Risk Mitigation Checklist (Actionable)

Use this checklist during planning, construction, and installation. Mark each item as completed. This directly addresses the highest-risk items from the Risk Assessment Matrix.

### Pre-Construction (Before Starting Work)
- [ ] Review full Risk Assessment Matrix and understand high-risk items (especially R01, R03, R04, R09).
- [ ] Confirm second person / spotter will be present for any work at height or electrical work.
- [ ] Inspect all tools and PPE (safety glasses, gloves, sturdy shoes, high-visibility clothing).
- [ ] Check weather forecast — do not schedule mounting during high wind, rain, or storms.
- [ ] Confirm mounting location is structurally sound and clear of overhead hazards (power lines, etc.).
- [ ] Prepare emergency plan: nearest hospital, emergency contacts, and descent route if working at height.
- [ ] Print or copy this checklist + Safety Checklist section.

### During Construction (Workshop / Ground Work)
- [ ] Wear safety glasses and gloves when cutting plywood or handling chicken wire.
- [ ] Secure all materials and tools so nothing can fall or shift unexpectedly.
- [ ] Keep work area clean and free of trip hazards.
- [ ] Never modify or work on live electrical circuits (solar panel or battery).
- [ ] Use outdoor-rated cables and proper weatherproof enclosures for all electronics.
- [ ] Test power system (solar + battery + charge controller) on the ground before mounting.
- [ ] Document the build with photos at each major stage.

### During Mounting & Installation (On Site)
- [ ] Use stable, rated ladder or lift. Have spotter on ground at all times when above 6 ft.
- [ ] Secure the dish and all tools with tethers or ropes.
- [ ] Confirm all mounting hardware (U-bolts, brackets, fasteners) is rated for structural outdoor use and wind load.
- [ ] Double-check torque on all fasteners after initial mounting.
- [ ] Protect all cable entry points from water and animals.
- [ ] Perform final visual safety inspection from the ground before leaving the site.
- [ ] Confirm the node is stable and cannot swing or fall if a mounting point shifts.

### Post-Installation & Ongoing Operation
- [ ] Re-inspect all mounting hardware and connections after 24–48 hours and after first major weather event.
- [ ] Verify power system runs autonomously for minimum 7 consecutive days.
- [ ] Confirm all cables are secured and protected from weather, wind, and potential vandalism.
- [ ] Complete full documentation package (photos, GPS, signal reports, safety sign-off).
- [ ] Store signed Safety Checklist and Risk Mitigation Checklist with node records.
- [ ] Create simple shutdown procedure in case of emergency or maintenance.
- [ ] Schedule periodic re-inspection (monthly for first 3 months, then quarterly).

### High-Risk Item Specific Mitigations
**Working at Height (R01, R09)**
- Spotter required at all times.
- Tools tethered.
- No work in wind, rain, or poor visibility.
- Stable platform only.

**Electrical / Battery Safety (R03, R08)**
- Disconnect solar panel before any wiring changes.
- Use correct charge controller and properly sized cables.
- Protect batteries from direct sun and extreme temperatures.
- Test full autonomy before relying on the node.

**Weather & Structural Damage (R04)**
- Use weatherproof enclosures and UV-resistant materials.
- Secure mounting against expected wind loads.
- Re-inspect after storms.

**Theft / Vandalism (R05)**
- Mount in visible but reasonably secure location.
- Use tamper-resistant hardware where practical.
- Document installation thoroughly for insurance purposes.

**Documentation & Liability (R10)**
- Complete this checklist and the Safety Checklist.
- Take dated photos of the full installation.
- Keep records in a known, backed-up location.

One Human Family. Mitigate risks deliberately. Build safely. Document everything.

## Detailed Risk Assessment Matrix (Expanded)

This expanded matrix includes additional context for each risk, including category, pre-mitigation score, post-mitigation residual risk, and responsible party.

| Risk ID | Category          | Risk Description                                      | Likelihood | Impact | Pre-Mitigation Score | Key Mitigation Actions                                      | Residual Risk | Owner          |
|---------|-------------------|-------------------------------------------------------|------------|--------|----------------------|-------------------------------------------------------------|---------------|----------------|
| R01     | Safety            | Fall from height during mounting                      | 3          | 5      | 15                   | Spotter required, stable platform, tool tethers, no work in bad weather | Low           | Builder + Spotter |
| R02     | Safety            | Injury from sharp chicken wire or cutting tools       | 4          | 3      | 12                   | Safety glasses + gloves mandatory, careful cutting technique | Low           | Builder        |
| R03     | Electrical        | Electrical shock or lithium battery fire              | 2          | 4      | 8                    | Disconnect solar before wiring, use correct charge controller, proper battery storage | Low           | Builder        |
| R04     | Environmental     | Equipment damage from wind, rain, or lightning        | 4          | 3      | 12                   | Weatherproof enclosures, secure mounting, lightning protection on upgrades | Medium        | Builder        |
| R05     | Security          | Theft or vandalism of node or components              | 3          | 3      | 9                    | Visible but secure mounting, tamper-resistant hardware, documentation for insurance | Medium        | Builder + Team |
| R06     | Technical         | Poor link performance or unreliable connection        | 3          | 3      | 9                    | Proper aiming and testing, document signal reports, plan upgrade path | Low           | Builder        |
| R07     | Legal/Regulatory  | Operation outside legal frequency or power limits     | 2          | 4      | 8                    | Stay within ISM bands, document configuration, no restricted frequencies | Low           | Builder        |
| R08     | Technical         | Power system failure (solar panel or battery)         | 3          | 3      | 9                    | Quality components, test 7+ days autonomy, backup charging plan | Low           | Builder        |
| R09     | Safety            | Injury to bystanders or traffic incident              | 2          | 5      | 10                   | Work during low-traffic periods if near road, use cones/high-vis gear, spotter | Low           | Builder + Spotter |
| R10     | Documentation     | Incomplete records leading to liability or insurance issues | 3     | 3      | 9                    | Complete all checklists, dated photos, signed safety forms, store records securely | Low           | Builder        |
| R11     | Community         | Negative reaction from neighbors or property owner    | 2          | 3      | 6                    | Be respectful, communicate purpose if asked, keep site clean and professional | Low           | Builder        |
| R12     | Future Integration| Difficulty integrating node with future thermal/dome systems | 2     | 2      | 4                    | Design Phase 1 with expansion in mind, document mounting points and power capacity | Low           | Builder + Team |

### Risk Score Interpretation
- **1–6**: Low — Standard precautions and normal vigilance sufficient
- **7–12**: Medium — Specific mitigation actions required + monitoring
- **13–25**: High — Strong controls, supervision, and re-evaluation required before proceeding

### Additional Guidance
- All **High** and **Medium** risks must be actively managed during the build and first 30 days of operation.
- Re-evaluate this matrix after any major change (new mounting method, power upgrade, software change, or environmental shift).
- Residual risk ratings assume all listed mitigations are properly implemented.

One Human Family. Understand the risks. Mitigate them deliberately. Build responsibly.

## Specific Mitigation Strategies

This section provides detailed, practical mitigation strategies for the highest-risk items identified in the Risk Assessment Matrix. These go beyond general advice and give concrete actions.

### R01 & R09 — Fall from Height / Injury to Bystanders or Traffic

**Mitigation Actions:**
- Never work alone when mounting above 6 feet. A spotter must be on the ground at all times.
- Use a stable, rated ladder or aerial lift. Inspect it before every use.
- Secure the dish and all tools with tethers or ropes so nothing can fall.
- Work during lower-traffic periods if the site is near active roads. Use traffic cones and high-visibility clothing.
- Do not mount in high wind (>15 mph), rain, or icy conditions.
- Have a clear emergency descent plan before starting work at height.
- Perform a final safety check from the ground after mounting is complete.

### R03 & R08 — Electrical Shock or Battery/Power System Failure

**Mitigation Actions:**
- Always disconnect the solar panel before making any wiring changes.
- Use only outdoor-rated cables, connectors, and enclosures.
- Use a quality charge controller (TP4056 or better) matched to your battery and panel.
- Protect lithium batteries from direct sunlight and extreme heat.
- Test the full power system (solar + battery + load) on the ground for at least 48–72 hours before final mounting.
- Create a simple visual indicator (LED or meter) so you can quickly check if the system is charging and healthy.
- Have a backup charging method (USB power bank or vehicle) available during the first week of operation.

### R04 — Weather Damage (Wind, Rain, Lightning)

**Mitigation Actions:**
- Use UV-resistant paint or coating on all exposed wood and enclosures.
- Secure all mounting hardware against expected wind loads for the area.
- Use weatherproof (IP65 or better) enclosures for all electronics.
- Add drip loops on all cables entering enclosures.
- On future upgrades, add basic lightning protection (grounding rod + surge protection on power lines).
- Re-inspect the entire installation after any major storm or high-wind event.

### R05 — Theft or Vandalism

**Mitigation Actions:**
- Mount the node in a visible location where casual tampering is more likely to be noticed.
- Use tamper-resistant or security-style fasteners where practical.
- Document the installation thoroughly with dated photos (useful for insurance claims).
- Consider adding a low-cost trail camera on future upgrades if theft risk is high.
- Do not leave valuable tools or spare parts at the site unattended.

### R06 — Poor Link Performance

**Mitigation Actions:**
- Spend adequate time aiming the dish while monitoring signal strength in real time.
- Document baseline signal reports in multiple directions before declaring the node operational.
- Plan an upgrade path to a hub or superhub if link quality is marginal.
- Keep firmware updated and test both WiFi and LoRa performance regularly during the first 30 days.

### R07 — Legal / Regulatory Issues

**Mitigation Actions:**
- Stay strictly within legal ISM band limits (915 MHz and 2.4 GHz in the US).
- Document your exact frequency, power level, and antenna configuration.
- Do not experiment with restricted or licensed frequencies.
- Keep records of firmware versions and configuration in case questions arise.

### R10 — Incomplete Documentation / Liability

**Mitigation Actions:**
- Complete both the Safety Checklist and Risk Mitigation Checklist before leaving the site.
- Take dated photos of the full installation from multiple angles.
- Record GPS coordinates and basic performance data on the day of installation.
- Store all documentation in a known, backed-up location (GitHub + local copy).
- Have a witness sign the safety and risk checklists.

### R11 — Negative Community Reaction

**Mitigation Actions:**
- Keep the installation clean, professional, and low-profile.
- Be prepared to politely explain the purpose of the node if asked by neighbors or property owners.
- Avoid blocking access or creating visual clutter.
- Document any conversations with neighbors or property owners.

---

## Summary of Top Priority Mitigations

| Risk | Highest Priority Mitigation | When to Apply |
|------|-----------------------------|---------------|
| Fall from height | Spotter + tool tethers + stable platform | Every time working above 6 ft |
| Electrical / battery | Disconnect solar before wiring + test on ground first | During construction and any power work |
| Weather damage | Weatherproof enclosures + secure mounting | During build and after storms |
| Theft / vandalism | Visible but secure mounting + documentation | During mounting and ongoing |
| Documentation gaps | Complete checklists + dated photos | Before leaving site every day |

One Human Family. Mitigate risks with specific actions. Build deliberately and safely.

## Implementing Specific Grounding Techniques

Proper grounding improves safety and helps protect equipment from static buildup, lightning-induced surges, and electrical noise. While a full professional grounding system is ideal for larger installations, the following techniques are practical and effective for a small outdoor mesh node like Sikeston Node Zero.

### Why Grounding Matters for This Node
- Reduces risk of electrical shock to people working on or near the node.
- Helps protect sensitive electronics (ESP32, WiFi adapter, LoRa module) from static discharge and minor surges.
- Improves long-term reliability of the radio equipment by reducing noise.
- Provides a basic path for lightning energy if a direct or nearby strike occurs (note: this is not full lightning protection).

### Recommended Grounding Approach (Phase 1)

**1. Ground the Mounting Structure (Dish Mount)**
- Drive a copper or galvanized ground rod (minimum 8 ft / 2.4 m) into the earth near the mounting location.
- Use heavy-gauge copper wire (minimum 10 AWG, preferably 6 AWG) to connect the metal mounting structure (pole, bracket, or kiosk frame) to the ground rod.
- Keep the wire as short and straight as possible.
- Secure the connection with a proper ground clamp rated for outdoor use.

**2. Ground the Electronics Enclosure**
- Connect the metal chassis or enclosure of the electronics box to the same ground rod using 10–12 AWG wire.
- If using a plastic enclosure, add a grounding terminal or bus bar inside and connect it to the ground rod.
- This helps drain static charge that can build up on the enclosure or cables.

**3. Ground the Coaxial Cable Shield (if applicable)**
- If using external antennas with coaxial cable in the future, ground the shield at the enclosure entry point using a grounding block or proper connector.
- For the initial Phase 1 build (internal WiFi adapter + LoRa module), this step is usually not required.

**4. Solar Panel Grounding (Recommended)**
- Connect the frame of the solar panel to the same ground rod.
- Use appropriate outdoor-rated grounding wire and clamps.
- This reduces the chance of static buildup on the panel and provides a basic path for surges.

### Materials Needed (Approximate)
- 8 ft copper or galvanized ground rod
- 10–6 AWG bare or insulated copper grounding wire
- Ground rod clamp (rated for outdoor use)
- Grounding block or bus bar (optional but helpful)
- Appropriate connectors and weatherproofing tape or heat shrink

### Installation Tips
- Drive the ground rod fully into the earth (leave only the clamp exposed).
- Keep all grounding wires as straight and short as possible — avoid sharp bends or loops.
- Make solid mechanical connections. Use proper clamps rather than just wrapping wire.
- Protect all connections from corrosion (use dielectric grease or outdoor-rated tape).
- Document the grounding installation with photos.

### Important Safety Notes
- Grounding does **not** make the system immune to direct lightning strikes. In high-risk lightning areas, additional protection (surge protectors, disconnecting equipment during storms) is strongly recommended.
- Never work on grounding connections during a thunderstorm.
- If you are unsure about any electrical work, consult a qualified electrician.
- Proper grounding is especially important once the node is integrated with larger power systems (thermal cascade, larger solar arrays, or AC-powered equipment).

### Future Enhancements (Phase 2+)
- Add a dedicated surge protection device on the power input.
- Install a more robust grounding system when upgrading to a hub or superhub.
- Consider a lightning rod on taller structures (future dome or mast) with proper down-conductor and grounding.

One Human Family. Ground deliberately. Protect people and equipment. Build safely for the long term.

## Installing Surge Protection Devices

Even a small outdoor mesh node like Sikeston Node Zero benefits from basic surge protection. While no device can fully protect against a direct lightning strike, surge protection can significantly reduce damage from nearby strikes, power line surges, and static discharge.

### Why Add Surge Protection

- Protects sensitive electronics (ESP32, WiFi adapter, LoRa module) from voltage spikes.
- Reduces risk of damage from nearby lightning or utility power fluctuations.
- Complements proper grounding (grounding provides a path; surge protection clamps the voltage).
- Low-cost insurance for a node that may become part of a larger network.

### Recommended Approach for Phase 1 (Simple & Affordable)

For the initial Sikeston build, focus on **power-side surge protection**. Data/radio side protection can be added in Phase 2.

**Power Input Surge Protection**
- Use a quality outdoor-rated surge protector or surge protection device (SPD) on the DC power line coming from the solar charge controller or battery.
- Recommended simple options:
  - DC surge protector module (commonly used in solar installations)
  - Quality USB surge protector / power strip with surge protection (for very small setups)
  - MOV (Metal Oxide Varistor) based DC surge protector rated for your system voltage (usually 12V or 5V in Phase 1)

**Installation Steps**
1. Install the surge protection device as close as possible to where power enters the electronics enclosure.
2. Connect it between the power source (solar/battery) and the load (ESP32 + radio modules).
3. Ensure all connections are weatherproof (use outdoor enclosures, dielectric grease, and proper sealing).
4. Connect the surge protector’s ground terminal to your main ground rod if it has one.

### Phase 2+ Enhancements (When Scaling Up)

When upgrading to a hub or superhub, or integrating with larger power systems, add these:

- **AC Surge Protection** (if using any AC-powered equipment in the future)
- **Data Line Surge Protection** on Ethernet or long cable runs (using gas discharge tube or TVS diode-based protectors)
- **Coaxial Surge Protection** if using external antennas with coax cable
- **Whole-system grounding + surge protection** tied to a proper ground rod system

### Important Limitations

- Surge protection devices have a finite lifespan and can be destroyed by a large surge. They should be inspected periodically.
- No surge protector offers 100% protection against a direct lightning strike. For critical or high-value installations, consider additional measures such as:
  - Disconnecting equipment during severe storms
  - Using fiber optic links for long cable runs (future)
  - Installing a lightning rod on tall structures with proper down-conductor

### Safety Notes

- Always disconnect power before installing or replacing surge protection devices.
- Use devices rated for outdoor use and the correct voltage/current of your system.
- If you are not comfortable working with electrical components, consult someone with experience.
- Document the installation of surge protection devices (photos + notes) as part of the node records.

### Summary Recommendation for Sikeston Node Zero

**Phase 1 (Current Build):**  
Add a simple, low-cost DC surge protector on the power input to the electronics enclosure. Combine it with proper grounding of the mount, enclosure, and solar panel.

**Phase 2+ (Future Upgrades):**  
Add data line and coaxial surge protection when expanding the node or connecting longer cable runs.

One Human Family. Protect what you build. Ground and surge-protect deliberately. Build systems that last.
