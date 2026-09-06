# Cloud Nine Prototype v0.1 — Preliminary BOM & Cut List

This is the lowest-viable first article. It prioritizes proof of the stacked functions over perfection or size.

## Structural
- Compression struts: lightweight tube or wood (bamboo, scrap, or thin-wall metal) — quantity to be determined by chosen tensegrity geometry (start with 6-strut or 12-strut simple tensegrity)
- Tension elements: high-strength cord, wire rope, or spectra/dyneema equivalent (scrap or low-cost)
- Connectors / hubs: 3D-printable or simple bolted/plate hubs

## Thermal
- Inner absorber: high-absorptivity black surface (painted metal, carbon-loaded sheet, or early aerocement panel)
- Vacuum or insulated gap: practical first version may use multi-layer insulation or sealed air gap if true vacuum is not yet available; true vacuum is the target
- Outer radiative surface: high-emissivity coating or material facing the sky

## Orientation & Safety
- Simple passive or low-power solar orientation (weighted or reflective)
- Autorotation / spin-stabilized descent path (geometry chosen so that uncontrolled descent produces spin and drag)

## Power & Control (minimal)
- Small photovoltaic for housekeeping
- Optional low-power microcontroller for logging ΔT and basic orientation
- Mesh radio compatible with the lowest-node stack (Meshtastic / MeshCore / TinyGS-class)

## Life support (stretch goal for v0.1)
- Thin soil tray or grow mat
- Water retention and simple drainage

## Ground support equipment
- Black Locust coppice material for any wooden elements and for test RMH heat source
- Node-001 style ground ΔT reference unit for comparative measurement
- Basic temperature logging (already exists in openroot/bin/or_log_dt)

## Notes
- First article should be small enough to build and test with a handful of people and scrap-level resources.
- Every component must have a clear path to lower-cost or scrap substitution.
- Success metric for v0.1: measurable ΔT + stable structure + soft-failure mode demonstrated + mesh node reachable.
