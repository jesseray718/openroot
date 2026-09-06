# AE-GFRC Test Tile — BUILD-001 Checklist
**UNE:** DV.GEN.TH.AE01
**Hypothesis:** H-001 (pumped AE-GFRC) + H-003 (thermal cascade)
**Goal:** Validate foam stability, open-cell structure, and blackbody absorption

## Materials
- [ ] Portland cement (Type I/II)
- [ ] Glass fiber roving (alkali-resistant, zirconium-treated)
- [ ] Xanthan gum (foam stabilizer — prevents bubble collapse)
- [ ] Activated carbon (volumetric blackbody absorber, fine powder)
- [ ] Aluminum powder OR hydrogen peroxide (aeration agent)
- [ ] Water (clean, potable)
- [ ] Sand (fine, washed — or omit for pure cement paste variant)

## Equipment
- [ ] Mixing vessel (5gal bucket minimum)
- [ ] Drill paddle mixer
- [ ] Scale (0.1g resolution for xanthan gum)
- [ ] Mold (12"x12"x2" plywood or silicone)
- [ ] Release agent (vegetable oil works)
- [ ] Thermometer (probe type)
- [ ] Infrared thermometer (surface temp readings)
- [ ] Camera/phone for documentation
- [ ] Timer

## Mix Procedure
- [ ] Weigh all dry components
- [ ] Dry-mix cement + activated carbon (if used)
- [ ] Add glass fiber, distribute evenly
- [ ] Dissolve xanthan gum in water (0.1-0.3% by water weight)
- [ ] Add gum-water to dry mix, blend until slurry
- [ ] Add aeration agent, mix at consistent speed
- [ ] Record mix time, ambient temp, humidity
- [ ] Pour into mold in single lift
- [ ] Tap mold to release large voids
- [ ] Level surface

## Cure Protocol (21 days)
- [ ] Cover with damp cloth + plastic sheet
- [ ] Day 1: Initial set — do not disturb
- [ ] Day 3: Demold, photograph all faces
- [ ] Day 7: Document shrinkage, cracking, surface condition
- [ ] Day 14: Mid-cure photo + density measurement
- [ ] Day 21: Final demold — full documentation

## Validation Tests
- [ ] Density (weight ÷ volume) — target < 1200 kg/m³ for aerated
- [ ] Open-cell check (water absorption test — drip on surface, time penetration)
- [ ] Surface temperature under sun lamp (IR thermometer, 30min intervals)
- [ ] Compare surface temp vs plain concrete control sample
- [ ] Thermal conductivity (if equipment available; else document for lab send-out)
- [ ] Compressive strength (if press available; else document qualitative)

## Documentation Output
- [ ] Photo log (mix, pour, demold, each cure checkpoint)
- [ ] Temperature data table (time, ambient, surface)
- [ ] Mix design record (exact weights used)
- [ ] Anomalies/observations log
- [ ] Upload results to ~/projects/openroot/research/thermal-systems/BUILD-001-results.md
- [ ] Tag git: `git tag v0.5-test-tile-BUILD-001`

## Notes
- Without xanthan gum: bubbles WILL collapse — this is confirmed
- Activated carbon loading affects both absorption and structural strength
- Document EVERYTHING — this is the first physical artifact tying theory to reality
- If foam collapses: increase xanthan gum, decrease aeration agent, retry
