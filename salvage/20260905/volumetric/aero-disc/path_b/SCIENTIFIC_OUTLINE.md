# Path B — Scientific Outline
**High-Shear Stator + Thixotropic Surfactant Gel → Microscopic Closed/Open-Cell Material**

## Objective

Produce dual-structure cellular concrete:
- Outer skin: closed-cell, waterproof, non-breathable, structural
- Interior: open-cell, high-specific-surface, permeable, shape retained by the gel

The same material stream must be usable as both castable feedstock and printable feedstock for an open-source 3D printer.

## Physical Mechanism

High-shear mixing reduces mean bubble diameter (practical floor currently tens of microns with mechanical foaming). A thixotropic surfactant gel provides yield stress that holds the bubble network while the matrix sets and allows controlled rupture of cell walls in the interior while the outer skin remains closed.

## Target Properties

Closed-cell skin: density 800–1200 kg m⁻³, strength ≥ 5–8 MPa, near-zero permeability.
Open-cell interior: density 400–900 kg m⁻³, strength ≥ 2–3 MPa, high permeability.

## Open-Source Possibilities

Formulation recipes, simple stator designs, printer kinematics optimized for the gel, and a library of printable components (discs, manifolds, tank panels, vehicle cones) all released under the project licenses.

## Limitations

Mechanical foaming has a practical lower bound on bubble size. Long-term durability of the closed/open transition under cyclic wetting and thermal stress is unproven. Rheology must be matched to both casting and printing. Quality control of open-source builds will vary; measurement protocols are therefore essential.

## Experimental Roadmap

1. Small-batch trials of stator speed vs surfactant package vs observed bubble size
2. Systematic variation of thixotropic agent and measurement of yield stress / shape retention
3. Controlled experiments that produce demonstrable closed skin + open core
4. First printable test geometry
5. Publication of raw data and formulation in Issues
