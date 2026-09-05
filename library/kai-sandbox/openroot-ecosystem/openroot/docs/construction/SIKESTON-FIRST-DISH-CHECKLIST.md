# Sikeston First Dish — This-Week Build Checklist (Node Zero)

**Project:** OpenRoot  
**Designation:** DV.MSH.WF.SK01-CHECK  
**Date:** 2026-07-08  
**Target:** Complete + mount first operational WiFi + LoRa dish at I-55 kiosk by end of week  
**License:** CC-BY-SA 4.0

---

## Pre-Build (Today or Tomorrow — 1–2 hours total)

1. **Confirm kiosk mounting point**  
   - Existing pole, roof edge, or new 10–15 ft pole section.  
   - Clear line-of-sight path toward expected neighbors (north toward Cape Girardeau / St. Louis direction first).  
   - GPS coordinates recorded.

2. **Shopping run (one trip)**  
   Use MATERIAL-CUTS-LIST.md shopping list.  
   - Plywood/OSB 4×8 sheet (6 mm)  
   - Chicken wire roll (galvanized, ≤12 mm hex)  
   - 200 cable ties (UV black, 200 mm)  
   - Fine chain (2 m)  
   - Spray paint + string  
   - USB WiFi adapter (Alfa or equivalent 2.4 GHz high-gain)  
   - Small bracket for focal-point mount  
   **Optional same trip:** ESP32 + SX1262 LoRa, 5–10 W solar panel, 18650 + TP4056, small PVC box.  
   Total \~$39 basic / \~$71 with companion.

3. **Download & print templates**  
   https://opensourcelowtech.org/wifidish.html → WifiDish_2019_01.pdf  
   Print at 100% scale (verify reference bar). Or project onto plywood.

---

## Build Day 1 (4–6 hours active work)

**Morning — Cutting (2–2.5 hrs)**  
- Lay out all 10 templates on one 4×8 sheet (long red ribs, medium green, short blue).  
- Trace + cut with jigsaw. Sand edges smooth.  
- Drill 5 holes (3 mm) evenly spaced near outer curved edge of every rib piece.

**Afternoon — Assembly (2–3 hrs)**  
- Dry-fit all 10 ribs into paraboloid frame (friction only — no glue).  
- Verify curve with fine chain catenary test.  
- Attach chicken wire from center outward with cable ties. Keep tight and flush. Trim excess, fold edges safe.  
- Critical check: no mesh gap >12 mm.  
- Find focal point with two tight crossing strings.  
- Mount WiFi adapter (and LoRa module if bought) exactly at focal point on bracket.  
- Route cables along a rib with zip ties.  
- Optional: spray-paint plywood ribs (let dry 30+ min).

**End of Day 1**  
- Dish frame complete + receiver mounted.  
- Take photos from multiple angles.  
- Note any fit issues for next build.

---

## Build Day 2 (2–3 hours)

**Mounting & Aiming (1.5–2 hrs)**  
- Attach completed dish to kiosk pole/roof bracket.  
- Initial rough aim toward nearest expected node or open direction (north/northeast first).  
- Connect WiFi adapter to laptop or phone.  
- Run signal scan (iwlist scan or WiFi analyzer app).  
- Rotate dish in 5° increments while watching signal strength.  
- Lock at peak. Tighten all hardware.  
- If LoRa companion installed: flash Meshtastic, set 915 MHz (US), test transmit/receive.

**Documentation & Registration (30–45 min)**  
- GPS coordinates + photos of finished install.  
- Signal strength achieved + direction aimed.  
- Create community/builds/SK01-first-dish.md with photos + notes.  
- Log build as first verified physical work (builder + one witness) for future ACRE mint.

**Power (same day or next)**  
- Temporary: kiosk outlet or small solar panel on ground.  
- Permanent plan: tie into future Thermal Cascade / AE-GFRC housing on kiosk.

---

## Success Criteria (End of Week)

- Dish physically mounted and aimed.  
- WiFi link test successful (or at least scanning neighbors).  
- LoRa module (if installed) transmitting on 915 MHz.  
- Build documented in repo.  
- First ACRE-eligible physical work logged.

---

## Immediate Next Actions After This Dish

1. Add second dish or elevate first dish → upgrade toward local superhub.  
2. Recruit 3–5 neighboring households for first Flower of Life ring.  
3. Test link quality over 1–2 weeks and log uptime.  
4. Open GitHub issue or SimpleX thread titled “Sikeston Node Zero — first operational dish online”.

---

## Safety Notes

- Wear safety glasses when cutting chicken wire (sharp edges).  
- Use proper ladder / fall protection when mounting on roof or pole.  
- Do not transmit on restricted frequencies. 915 MHz / 2.4 GHz ISM bands are legal in US at allowed power.

One Human Family. The $39 dish you build this week at the I-55 kiosk is the Vesica Piscis seed of the entire planetary supermesh. Start here.
