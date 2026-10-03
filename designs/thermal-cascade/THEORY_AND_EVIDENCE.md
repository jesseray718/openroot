<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Theory and Evidence

## Theory is proof within stated premises

Theoretical mathematical physics is a legitimate form of proof. A correct
derivation proves what follows from its equations, assumptions, boundary
conditions, parameter values, and definitions.

For Thermal Cascade, valid theoretical work can establish energy conservation,
dimensional consistency, heat/mass-transfer relationships, psychrometric bounds,
stack-pressure limits, storage calculations, and thermodynamic limits within
the stated model.

## Identified model artifacts

| Model area | Source | Correct classification |
|---|---|---|
| OpenCell latent heat / water / generation tradeoff | `historical private calculation artifact: 0670_aerocement_triad_v1.py` — SHA-256 `dba758fac4044bd3c716fcb31544abfef66bd49f911e2722e648b0c1d8dfbddf` | Model with explicit defaults and accounting boundary |
| Desiccant sizing and regeneration | `historical private calculation artifact: 0672_desiccant_module_v1.py` — SHA-256 `b06510ee884c9c63f00071aa71c1ba0a8868c0869d0e1936db4f6fbc6290d1da` | Model with desiccant-capacity and heat-input assumptions |
| Cold-side thermal value check | `historical private calculation artifact: 0679_thermal_battery_check.py` — SHA-256 `dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf` | Calculation/model |
| Ferrocement tank, coil, freezing, and stratification | `historical private calculation artifact: 0708_thermal_battery_system.py` — SHA-256 `6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa` | Model with stated tank, coil, weather, and U-value inputs |
| Solar/steam/Stirling branch | `historical private calculation artifact: thermal_balance_v63.py` — SHA-256 `3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335` | Separate high-hazard model branch |
| Architecture and heat-balance rationale | `docs/README.md` — SHA-256 `46dfda5a736b2d63e247374a95794397fe006ee9b9c1480095a0cc960125fa87`; `docs/research/cascade-heatbalance.md` — SHA-256 `db0a8a73651cda954fbc99ee19e08db73462def94ab757f98982dea23f683bb3` | Design architecture and mathematical rationale |

## Proof layers

| Layer | Establishes | Does not establish alone |
|---|---|---|
| Mathematical proof | What follows from explicit premises | That a constructed system satisfies those premises |
| Model or simulation | Predicted behavior inside a stated parameter domain | Correct geometry, material behavior, losses, controls, or field performance |
| Controlled measurement | A documented configuration’s observed behavior | General reliability, replication, certification, or universal suitability |
| Field validation | Behavior across recorded actual-use conditions | Safety certification or performance outside documented conditions |

## Required accounting boundaries

- Latent heat transport is not a second energy source.
- Do not add solar-face input and a latent-transport term as energy created.
- Do not add heat service, cooling service, and shaft/electrical output as one thermodynamic-efficiency numerator.
- Treat open-loop exhaust as a mass and enthalpy outlet.
- Keep direct thermal service, stored energy, and work conversion in distinct accounting columns.
- Keep the high-pressure steam branch separate from the wet-labyrinth system.

## Evidence status

The repository contains specific architecture and model artifacts. This review
does not itself classify every artifact as admitted L1 evidence or identify a
complete L2 physical record. Any public claim must cite the exact source,
revision, configuration, method, units, conditions, and limitation that support it.

The OpenCell absorber document is explicitly a manuscript skeleton whose claims
await experiment: `docs/research/opencell-absorber.md` — SHA-256 `d7c8c426b58e5e6341c1ee01a68090be8bac0bfcd266161b83744ca456204185`.


## Public calculation availability

The calculation artifacts listed above are preserved as provenance references
with recorded SHA-256 identifiers. They are not included in this public
repository as runnable code because they have not yet completed source,
license, safety, dependency, and reproducibility review. The associated
entries therefore support `documented` or `proposed` context, not an
independent public reproduction claim.
