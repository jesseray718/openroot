# OPENROOT CONTEXT BRIDGE — THERMAL CASCADE H-003 REV-D (v4 WITH ALTERNATOR)

## IDENTITY
Jesse McMillen ("Jesse Ray") — Permaculture systems designer, appropriate technology inventor, polymath
Location: Sikeston, Missouri
Development: Samsung Galaxy A15 + Termux, Optiplex Ubuntu desktop
GitHub: jesseray718 (main: openroot)

## PROJECT
OpenRoot — decentralized architecture combining permaculture, thermodynamics, governance axioms, decentralization
Current focus: Thermal Cascade System (H-003) + AE-GFRC (aerated concrete) + ACRE token

## HYPOTHESIS STATUS
- **H-001 (Pumped AE-GFRC)**: COMPLETED — validated mix protocol, ZrO₂ ≥16%, xanthan stabilizer
- **H-002 (Delta-T Vehicle)**: COMPLETED — spec written, awaiting physical build
- **H-003 (Thermal Cascade)**: UNDER REVISION — v4 released with open-loop breathing + alternator

## ACTIVE WORK (v4 KEY CHANGES)
1. **Open-loop breathing**: Ambient air IN → panel → pre-dryer → labyrinth → storage → EXHAUST
   - Not closed loop — fresh air each cycle
   - Stack effect drives natural convection
   
2. **Flywheel → Gear Differential → Alternator**
   - Flywheel stores kinetic energy
   - Gear diff (4:1) smooths output
   - Alternator converts excess to 120V/240V AC
   - 24-hour electrical production guaranteed

3. **50-bar theoretical system** (full potential)
   - Pressure: 50 bar (725 psi)
   - Steam temp: 264°C
   - ΔT with ice (-10°C): 274°C
   - Stirling power: ~77kW theoretical
   - Daily electric: ~77kWh at full capacity
   
   **Reality:**
   - 10 bar = BUILDABLE (steel pipe, DIY)
   - 50 bar = PROFESSIONAL (ASME-certified team)
   - Present 50-bar concept to engineering group, build 10-bar ourselves

4. **Cold battery: Water→ICE phase change**
   - Radiative cooling lid freezes water solid (-10°C)
   - 461 kJ/kg vs 84 kJ/kg for water-only
   - 5.5x advantage from latent heat of fusion

5. **Stirling + TEG dual-mode**
   - Stirling: Main power (10-77kW depending on pressure)
   - TEG: 24/7 trickle (supplementary, no moving parts)

## KEY NUMBERS (1 m² BASE UNIT)

| Component | 10-Bar (Buildable) | 50-Bar (Theoretical) |
|-----------|-------------------|---------------------|
| Steam temp | 180°C | 264°C |
| ΔT | 190°C | 274°C |
| Stirling power | ~54kW | ~77kW |
| Daily electric | 81.6 kWh | 1848 kWh |
| ACRE/day | ~694k | ~1.8M |

**Scaling:** All components scale linearly with panel area
- 25 m² home = ×25 all
- 100 m² farm = ×100 all
- 500 m² village = ×500 all

## MATERIAL SPECIFICATIONS (CORRECTED)
- AR-glass fiber: ≥16% ZrO₂ (ASTM C1666)
- Wire mesh: 22ga galvanized hexagonal ½" — 2 layers
- AE-GFRC: cement + water + glass fiber + xanthan gum (NO SAND)
- Ferrocement: 21-day wet cure (ABSOLUTE)
- AE-GFRC: 1-2 day minimum cure
- Cardboard molds: silicone-treated, free from retail trash

## CURRENT STATE
- Thermal calculator updated to v4
- Spec documents written for Steam Integration + Delta-T Vehicle
- Budget optimizer (varo_optimize.sh) functional
- Week 1 purchase list: ~$180 ready

## NEXT STEPS
1. Execute purchases when paid ($180 for Week 1 materials)
2. Build 1 m² prototype panel (AE-GFRC, cardboard molds)
3. Pour ferrocement cold battery tank (21-day cure)
4. Source pneumatic hog ring pliers
5. Document with photos/video for promotional content
6. Begin RMH design (ferrocement/refractory composite)
7. Prepare 50-bar concept deck for engineering outreach

## FILES TO KNOW
- `~/bin/thermal_system_v4.py` — current calculator
- `research/thermal-systems/STEAM-INTEGRATION-SPEC.md`
- `research/thermal-systems/DELTA-T-VEHICLE-SPEC.md`
- `~/bin/varo_optimize.sh` — credit/budget simulator

## PHILOSOPHY
"Architecture not utopia" — practical framework for solving unnecessary suffering through abundance.
All content: GPL v3 (code), CC-BY-SA 4.0 (docs), Copyright: One Human Family
ACRE token: Proof of Physical Work — verified joules → minted ACRE

## CONTACT FOR SESSION RESUME
Send: "Resume H-003 v4" + paste last calculation output
Assistant will load full system context and continue work
