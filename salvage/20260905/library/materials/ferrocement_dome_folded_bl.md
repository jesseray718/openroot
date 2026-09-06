# Ferrocement Dome — Folded-Edge + Black Locust (Revised)
**UNE:** DV.CON.DOME.FERRO.002  
**Status:** draft  
**η note:** Folded GFRC void panels + local black locust timber. Structural numbers are conservative starting points — physical prototype and local engineer review required before scale.

## One-sentence essence
Recalculated BOM using folded-edge triangular panels (GFRC-filled voids replace most steel flanges) and black locust timber for posts, lattice, and formwork, priced at realistic local Missouri rates.

## Structural Load Limits (Conservative Starting Values)

| Material / Element              | Property                        | Conservative Value          | Notes |
|--------------------------------|---------------------------------|-----------------------------|-------|
| Black Locust (air-dry)         | Modulus of Rupture (bending)    | 14,000–16,000 psi (96–110 MPa) | High for hardwood |
|                                | Modulus of Elasticity           | 1.7–1.9 × 10⁶ psi           | Stiff |
|                                | Compression parallel to grain   | 8,000–10,000 psi            | Good post material |
|                                | Outdoor service life            | 80–100+ years               | Exceptional rot resistance |
| GFRC Void Panel (folded edge)  | Compressive strength            | 50–70 MPa                   | AR-glass + polymer |
|                                | Flexural strength               | 12–20 MPa                   | Fiber-dominated |
|                                | Typical panel thickness         | 12–20 mm skin + void        | Depends on span |
| Combined System                | Design philosophy               | Redundant load paths        | Domes share load; single panel failure should not cascade |

These are starting values only. Real allowable loads require:
- Actual panel span and curvature
- Live load (snow, wind, occupancy)
- Prototype destructive testing
- Local engineer stamp for habitable structures

## Materials Cost (Revised with Local Timber Price)

Local black locust rough-sawn / post price used: **$160 / m³** (Scott County / Southeast Missouri realistic 2026 range $140–190)

| Component             | Item                              | Qty      | Unit Cost | Total   | Notes |
|-----------------------|-----------------------------------|---------|-----------|---------|-------|
| Shell                 | Portland cement                   | 1,200 kg| $0.12/kg  | $144    |       |
|                       | Sand                              | 2,400 kg| $0.05/kg  | $120    |       |
|                       | Chicken wire                      | 80 m²   | $2.50/m²  | $200    |       |
|                       | Carbon fiber (reduced)            | 25 kg   | $15/kg    | $375    |       |
| GFRC Struts / Voids   | AR glass fibers                   | 70 kg   | $8/kg     | $560    | more for voids |
|                       | Polymer additive                  | 25 L    | $15/L     | $375    |       |
|                       | Carbon pigment                    | 5 kg    | $20/kg    | $100    |       |
| Black Locust Timber   | Structural posts / lattice / form | 1.8 m³  | $160/m³   | $288    | local price |
|                       | Stainless fasteners               | 1 set   | $120      | $120    |       |
| Minimal Flanges       | Critical plates only              | 40 kg   | $1.20/kg  | $48     | 80% reduction |
|                       | Bolts/nuts                        | 120 sets| $0.50/set | $60     |       |
|                       | Silicone                          | 30 m    | $2/m      | $60     |       |
| Clear Coating         | Epoxy system                      |         |           | $2,300  |       |
| Thermal Labyrinth     | Concrete + waterproof + desiccant |         |           | $13,100 |       |
| Solar                 | Aluminum + support + tracker      |         |           | $1,490  | black locust can replace part of steel |
| **Materials Total**   |                                   |         |           | **$19,340** | |

## Labor Cost (Folded-Edge)

| Work Type                         | Hours | Rate   | Total   |
|-----------------------------------|-------|--------|---------|
| General construction              | 340   | $25/hr | $8,500  |
| Specialty (GFRC voids + timber)   | 180   | $40/hr | $7,200  |
| **Labor Total**                   | 520   |        | **$15,700** |

**Grand Total: $35,040**

## Next physical action
1. Source actual local black locust quote (board-foot or m³) within 50 miles of Sikeston.
2. Build one full-size folded-edge GFRC void panel prototype.
3. Simple load test (sandbags or known weight) and document failure mode.

## Related
- Parent: library/materials/INDEX.md
- Energy path: DV.GEN.BL.RMH.001
- Previous bolted version: ferrocement_dome.md
