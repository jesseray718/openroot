# Material Science Notes

## Close Packing of Spheres

Foam bubbles approximate equal-sphere packing. Two maximal-density packings:

### HCP (Hexagonal Close Packing)
- Layers: ABABAB...
- Each sphere contacts 6 in-plane, 3 above, 3 below = 12 total.

### FCC (Face-Centered Cubic)
- Layers: ABCABC...
- Same in-plane hexagonal arrangement as HCP.
- Same 12-neighbor coordination.
- Difference is only stacking sequence.

Both achieve pi/(3*sqrt(2)) ~= 74.05% packing fraction.

Whether you start with hexagonal or square base layer, densest next-layer placement converges to HCP or FCC. Local coordination is identical.

In aerocement, bubbles are polydisperse (varying sizes), so true close-packing is never achieved. But each bubble tends toward maximal neighbor contact, with interstitial cement paste filling ~26% void space.

---

## Glass Fiber as Inter-Matrix Bridging

AR glass fibers operate at boundaries between packing matrices -- where clusters meet (grain boundaries, defects, interstitial gaps).

Functions:
- Span disrupted zones, providing tensile bridging.
- Independent fiber network complementary to foam pore structure.
- Resist crack propagation along grain boundaries.

Threads through cement paste in ~26% interstitial volume.

Prior art: GFRFC studies (MDPI, 2024) document gains in compressive, tensile, and flexural strength with AR glass in foamed concrete.

---

## Bubble Size Optimization: Shear/Stator Mixing

Standard mixing (300-500 RPM drill) produces adequate open-cell structure.

A high-shear stator mixer (rotor-stator) can drive bubble diameters progressively smaller:

- S/V proportional to 1/r -- halve radius, double surface area per unit volume.
- Smaller, more uniform cells distribute stress better -> higher compressive strength.
- Finer pore network -> stronger capillary action.
- More interconnects per unit volume -> better flow permeability.

This is an optimization target, not a requirement. Standard mixing yields a functional material.

---

## Activated Carbon: Revised Understanding

### Original Hypothesis
Bubbles would nucleate on activated carbon surface (1,000+ m2/g), coating carbon with foam.

### Revised Understanding
Bubbles form by mechanical entrainment in bulk fluid during mixing -- not surface nucleation. Carbon particles:

- Disperse throughout cement paste (interstitial matrix between bubbles).
- Provide volumetric blackbody absorption through the solid fraction.
- Do NOT attract or anchor bubbles.

Solar-thermal absorption is a **bulk property** of carbon-infused paste, not a surface-coating effect. Open-cell pores provide capillary pathways; carbon matrix provides thermal absorption. Structurally independent, functionally complementary.

---

## NASA Porous Ceramics Comparison

NASA explores engineered porosity in ceramic materials at multiple scales:

| Scale | Size | Function |
|---|---|---|
| Macropore | mm | Flow channels, volumetric solar absorption |
| Mesopore | nm to um | Catalysis, filtration |
| Nanoscopic void | nm | Ultra-low thermal conductivity (aerogels) |

Aerocement operates at macropore scale (foam bubbles) with mesoporous activated carbon embedded. Multi-scale porosity concept shared, though implementation differs (cementitious vs sol-gel ceramic).

Volumetric solar receivers in CSP research use porous open-cell foam (ceramic or metal) letting sunlight penetrate material depth -- ~90% solar-to-thermal efficiency. Activated carbon is a plausible candidate at moderate (non-concentrated) temperatures.

Constraint: Activated carbon oxidizes in air at a few hundred C. Non-concentrated temperatures or oxygen protection needed at higher temperatures. Open engineering question.

---

## Surface Area to Volume Ratio (m2/m3)

The defining metric. Open-cell porosity at 70-85% creates internal surface area orders of magnitude beyond solid concrete or pipe walls.

For spherical bubbles of radius r:
- Surface area = 4*pi*r^2
- Volume = (4/3)*pi*r^3
- N bubbles per m3 at porosity phi: N ~ phi / ((4/3)*pi*r^3)
- Total S/V ~ 3*phi / r

At phi=0.75, r=1 mm: S/V ~ 2,250 m2/m3
At phi=0.75, r=0.5 mm: S/V ~ 4,500 m2/m3

Compare to flat plate heat exchanger: S/V ~ 10-50 m2/m3.

This is why aerocement enables passive heat exchange and evaporative cooling at rates that would require mechanical forced convection in conventional systems.
