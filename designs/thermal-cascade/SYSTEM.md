<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade System

## Status

This is a source-linked architecture summary compiled from existing OpenRoot
design material. It describes design intent and theoretical system boundaries.
It does not claim a completed, measured, safe, certified, build-ready, or
field-validated installation.

## Core architecture

Thermal Cascade is an open-loop, multi-organ thermal system built around
separate hot and cold stores. Its governing design rule is:

> **Two tanks. Never one.**

The air stream enters once and exits once:

```text
fresh ambient air
→ desiccant pre-drying
→ underground labyrinth filled with wet OpenCell AeroCement
→ controlled thermal-exchange branch
  ├─ cold-side service and/or Cold Tank B exchange
  ├─ hot-side AeroDisk, solar, RMH, or computing-waste-heat interaction
  ├─ direct thermal-use load
  └─ defined work-conversion exchanger, where configured
→ controlled exhaust to atmosphere
```

Spent air does **not** return to the desiccant. Copper-coil water loops,
tank loops, source loops, and any working-fluid loops are separate from the
once-through air path.

## Heat, cold, and work

### Heat

Carbon-loaded or dark OpenCell AeroCement is intended to act as a volumetric
absorber. Air passes through the matrix rather than merely over a flat plate.
Captured heat may transfer through a copper coil into an insulated ferrocement
hot-water reservoir, **Hot Tank A**.

Possible hot-side organs include AeroDisk solar stack-effect panels, a
separate solar absorber, Black Locust rocket-mass-heater heat, documented
computing waste heat, or another bounded heat source. These are modular organs,
not evidence that every source operates in one validated installation.

### Cold

The underground OpenCell AeroCement labyrinth is intended to remain wet.
Incoming air is pre-dried with a desiccant so it has water-vapor uptake capacity.
The wet porous matrix provides distributed evaporation area through its internal
pore volume. This can shift sensible heat into latent water-vapor transport,
lowering air temperature under the stated inlet conditions.

Useful coolth may serve a direct load, exchange into the separate insulated
ferrocement **Cold Tank B**, couple to ground mass, or be routed through a
secondary heat-rejection path. Cold Tank B stores, buffers, and supplies
cold-side capacity. The wet porous labyrinth, ground coupling, and any
configured secondary heat-rejection path determine how cold-side capacity is
generated or replenished in a given operating mode.

### Work

A defined hot-to-cold temperature difference may support shaft work through a
Stirling/flywheel stage or electrical generation through a thermoelectric stage
where electricity is actually required. Direct thermal use remains distinct from
work conversion and must not be counted twice.

## Architectural distinctions

- **AeroDisk** is an above-grade solar stack-effect absorber, not the underground labyrinth and not the RMH.
- **The labyrinth** is a below-grade wet, porous, volumetric air–water–solid exchange stage.
- **Black Locust RMH** is a separate coppice-fueled hot-side source or backup.
- **Hot Tank A** and **Cold Tank B** are separate thermal reservoirs.
- The high-temperature steam/Stirling proposal is a distinct, high-hazard model branch. It is not a requirement of the low-pressure wet-labyrinth architecture.

## Model and measurement boundary

The following cited source values remain targets, assumptions, open values, or
model values until configuration-specific physical evidence is admitted:

- carbon-doped solar absorption target;
- permeability, water absorption, and internal surface-area targets;
- air-flow, stack-pressure, storage, and evaporative-cooling model outputs;
- source-specific heat delivery;
- cooling service, thermal storage capacity, work output, and efficiency.

## Sources

- `docs/README.md` — SHA-256 `46dfda5a736b2d63e247374a95794397fe006ee9b9c1480095a0cc960125fa87`
- `designs/thermal-cascade/docs/system-architecture.md` — SHA-256 `2023c352b07f5ecec277266b9bdafe3727e0cdcdcb4f3e3031ded19e3d37bf21`
- `docs/research/cascade-heatbalance.md` — SHA-256 `db0a8a73651cda954fbc99ee19e08db73462def94ab757f98982dea23f683bb3`
- `docs/research/opencell-absorber.md` — SHA-256 `d7c8c426b58e5e6341c1ee01a68090be8bac0bfcd266161b83744ca456204185`
