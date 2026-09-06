# White Paper: OpenRoot Aero-Disc
**Volumetric Helical Wet-Media Exchanger for Passive Thermal Cascades**

**Version**: 0.1 (2026-07-25)
**Status**: Living document — open for falsification
**License**: CC-BY-SA 4.0

## Abstract

We present a short multi-start helical wet-media disc (the “Aero-Disc”) sized so that its pressure drop remains below the buoyancy head of a modest residential solar chimney (≈5–6 Pa). The geometry exploits Dean vortices for 2–4× heat- and mass-transfer enhancement. Two fabrication routes are developed in parallel:

- Path A: snap-fit construction from flat cardboard treated with acetone-silicone solution, filled with open-cell volumetric aerocement.
- Path B: high-shear stator + thixotropic surfactant gel process that produces an engineered closed-cell outer skin and open-cell interior, feeding an open-source 3D printer library.

The disc is a modular primitive within the larger OpenRoot AeroCement / UNE / PoPW infrastructure. A secondary conceptual extension treats aerodynamic drag on a deep φ-spiraling wet cone as the energy source for a fully passive vehicle.

## 1. Motivation

In hot-humid climates evaporative cooling alone is insufficient. The OpenRoot thermal cascade therefore combines solar chimney, optional desiccant, wet high-surface labyrinth, stratified water battery, and rocket-mass heater. The Aero-Disc replaces the long high-resistance labyrinth with a compact volumetric element whose pressure drop stays inside available stack pressure, restoring the possibility of true fan-free operation.

## 2. Governing Physics (summary)

Stack pressure: ΔP = ρ g H (ΔT / T) ≈ 5.6 Pa for H=6 m, ΔT=25 K.

Helical enhancement uses Dean number, Ito friction, and Dravid Nusselt correlations. Corrected geometry yields NTU 3–5 at axial lengths of only 0.17–0.20 m when face velocity is kept low.

Design target: 0.18 m³/s, NTU ≥ 3, ΔP ≤ 5.6 Pa → fully passive. Sensible capacity 1.7–3.8 kW depending on approach temperature.

## 3. Locked Geometry (Path A)

- Outer diameter: 780 mm
- Axial length: 190 mm
- Face area: 0.478 m²
- 7 starts
- Channel diameter: 10 mm
- Coil radius: 25 mm
- Pitch: 80 mm
- Greenhouse air gap: 25–35 mm between black absorber and clear membrane

## 4. Fabrication Paths

Path A uses only flat cardboard pieces with male/female interlocking tabs. Acetone-silicone is applied to mating faces only and the pieces are assembled while tacky so a continuous waterproof membrane forms.

Path B uses high-shear stator mixing + thixotropic surfactant gel to control bubble size distribution and produce dual closed-cell skin / open-cell interior structure. This material becomes feedstock for a simple open-source 3D printer library.

## 5. Open-Source & Community Design

Issue templates force quantitative claims, references, and proposed experiments. Soft ideation lives in Discussions; hard falsification lives in Issues. Defensive publication under CC-BY-SA + GPL is the IP strategy. No patents.

## 6. Conceptual Extension — Passive Vehicle

A deep φ-spiraling cone with closed-cell outer surface and wet open-cell interior can convert a fraction of aerodynamic drag into useful work via a low-ΔT heat engine. This remains a speculative research track.

## 7. Limitations

Measured ΔP of the first physical disc is still required. Desiccant-stage pressure drop must also stay inside the stack budget. Long-term durability of the membrane and dual-structure material under cyclic loading is unproven.

## 8. Call for Collaboration

Open Issues that either falsify a quantitative claim with better data or propose a concrete measurable improvement. The only metric that matters is η = useful joules / human joules.
