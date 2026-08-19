# OpenRoot

**Open-source appropriate-technology lattice for physical infrastructure and the computational systems that serve it.**

## What this is

OpenRoot is the root repository of a larger interconnected system. It holds the core designs, documentation, thermodynamic ledgers, and coordination patterns for offline-first physical infrastructure (thermal, material, shelter, food) and the software that measures and improves it.

Key elements include:
- AeroCement and passive solar-thermal systems
- Node Zero (Sikeston) as the first physical instance
- Thermodynamic and PoPW (Proof of Physical Work) ledgers
- Integration points for the wider lattice (UNE, Agape, Black Locust, mesh communications)

## Role in the Lattice

OpenRoot is the trunk.  
Most other repositories in the jesseray718 account are specialized spokes that extend or implement parts of this system.

## Bigger Picture

The goal is an offline-first, open-source infrastructure stack that raises the amount of useful work available to the lowest-capability node while driving coordination cost toward zero.  

Physical systems (heat, materials, food, shelter) and the computational systems that observe, measure, and coordinate them are treated as one lattice. The work is deliberately patent-free, reproducible, and designed to function under intermittent power and connectivity.

## Current Status

Active. Node Zero and core documentation are live. The system is evolving through physical builds, measurement, and the surrounding software lattice.

## Key Entry Points

- `STRUCTURE.md` / `STRUCTURE_V2.md` — system map
- `projects/` — physical system designs
- `computational_flow/` / related engines — measurement and coordination
- `LATTICE-INDEX` (in the private archive) — full map of related repositories

## Related

- [une](https://github.com/jesseray718/une) — joule-native computational substrate
- [black-locust-rmh](https://github.com/jesseray718/black-locust-rmh) — carbon-negative thermal cascade
- [agape-primitives](https://github.com/jesseray718/agape-primitives) — cooperation primitives
- [Reticulum](https://github.com/jesseray718/Reticulum) + LXMF — offline mesh communications

License: Hardware CC-BY-SA 4.0 · Software GPL-3.0 · No patents.
