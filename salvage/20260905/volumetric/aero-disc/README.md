# OpenRoot Aero-Disc

**Volumetric passive thermal exchanger for AeroCement / UNE infrastructure**

A short, multi-start helical wet-media disc that delivers full design airflow under pure buoyancy (stack pressure ≤ 5–6 Pa). Designed for flat-cardboard snap-fit construction (Path A) and microscopic closed/open-cell material control via stator + thixotropic gel (Path B). Part of the larger OpenRoot / AeroCement / PoPW ecosystem.

**η-first design**: maximize useful cooling and heating joules per human joule of fabrication and operation. Fully open-source under CC-BY-SA 4.0 (hardware & documentation) + GPL-3.0 (software).

## Why this exists

Conventional HVAC is energy-intensive and centralized. The Aero-Disc is a drop-in volumetric component for climate-battery / solar-chimney / rocket-mass-heater cascades that can run fan-free under design conditions. It is the physical primitive that lets a 50 m² dwelling meet 1.7–3.8 kW sensible cooling with only solar and ground ΔT.

The same geometry and material system scales to:
- Passive solar absorbers with greenhouse air gap
- Wet labyrinth climate batteries
- Future fully passive vehicles that treat aerodynamic drag as the primary energy input

## Quick Start (Path A – cardboard)

1. Read `design/FLAT_CARDBOARD_DESIGN_GUIDE.md`
2. Cut the flat patterns from ordinary cardboard
3. Apply acetone + silicone solution only to mating faces
4. Snap together while tacky → continuous waterproof membrane
5. Fill with open-cell black aerocement
6. Measure ΔP at 0.18 m³/s

## Path B – microscopic control + open-source printer

See `path_b/SCIENTIFIC_OUTLINE.md` and `path_b/3D_PRINTER_ROADMAP.md`.

## Repository Structure
openroot-aero-disc/
├── README.md
├── docs/
│   ├── WHITE_PAPER.md
│   ├── ROADMAP.md
│   └── OPENROOT_INTEGRATION.md
├── design/
│   ├── FLAT_CARDBOARD_DESIGN_GUIDE.md
│   └── GREENHOUSE_GAP.md
├── path_b/
│   ├── SCIENTIFIC_OUTLINE.md
│   └── 3D_PRINTER_ROADMAP.md
├── scripts/
│   └── porous_exchanger_design.py
└── .github/ISSUE_TEMPLATE/
## How to contribute

Preferred Issue types (use the templates):
- Physics / thermodynamics falsification
- Fabrication process improvement
- Material characterization
- Scaling laws
- Vehicle concept critique

## License

- Hardware & documentation: CC-BY-SA 4.0
- Software: GPL-3.0
- No patents. Defensive publication.

**OpenRoot** — useful joules for the least among us.  
https://github.com/jesseray718/openroot
