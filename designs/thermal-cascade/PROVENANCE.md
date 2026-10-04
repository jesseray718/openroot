<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Thermal Cascade Provenance Register

## Purpose

This register maps canonical Thermal Cascade architecture and model sources.
It preserves their identity and claim type. Inclusion does not convert a target,
assumption, simulation, code default, or design statement into a measured
physical-performance, safety, certification, build-readiness, or deployment claim.

## Canonical source map

| ID | Source | Role | Current claim type |
|---|---|---|---|
| TC-ARCH-README | `docs/README.md` — SHA-256 `46dfda5a736b2d63e247374a95794397fe006ee9b9c1480095a0cc960125fa87` | Cross-project Heat / Cold / Work architecture | Canonical design architecture |
| TC-SYSTEM-ARCH | `designs/thermal-cascade/docs/system-architecture.md` — SHA-256 `2023c352b07f5ecec277266b9bdafe3727e0cdcdcb4f3e3031ded19e3d37bf21` | Packet system-architecture record | Design architecture |
| TC-HEAT-BALANCE | `docs/research/cascade-heatbalance.md` — SHA-256 `db0a8a73651cda954fbc99ee19e08db73462def94ab757f98982dea23f683bb3` | Heat-balance rationale | Theory/model |
| TC-OPENCELL-ABSORBER | `docs/research/opencell-absorber.md` — SHA-256 `d7c8c426b58e5e6341c1ee01a68090be8bac0bfcd266161b83744ca456204185` | Absorber research/protocol | Measurement protocol; claims pending experiment |
| TC-AEROCEMENT-TRIAD | `historical private calculation artifact: 0670_aerocement_triad_v1.py` — SHA-256 `dba758fac4044bd3c716fcb31544abfef66bd49f911e2722e648b0c1d8dfbddf` | Latent-water/generation model | Model |
| TC-DESICCANT | `historical private calculation artifact: 0672_desiccant_module_v1.py` — SHA-256 `b06510ee884c9c63f00071aa71c1ba0a8868c0869d0e1936db4f6fbc6290d1da` | Desiccant sizing/regeneration model | Model |
| TC-COLD-BATTERY | `historical private calculation artifact: 0679_thermal_battery_check.py` — SHA-256 `dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf` | Cold-side calculation | Model |
| TC-THERMAL-BATTERY | `historical private calculation artifact: 0708_thermal_battery_system.py` — SHA-256 `6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa` | Tank/coil/stratification model | Model |
| TC-HIGH-T-STEAM | `historical private calculation artifact: thermal_balance_v63.py` — SHA-256 `3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335` | Solar/steam/Stirling branch | High-hazard model branch |

## Admission rule

A theoretical artifact can support a documented model rationale after review of
its author/source, revision, assumptions, units, calculation method, validity
domain, and limitations. It can support a physical-performance claim only when
the claimed configuration has traceable documented testing, conditions,
instruments, raw data, uncertainty, and appropriate review.

## Excluded material

Backup, recovery, archive, duplicate, generated, cache, and quarantine material
may be used to locate source leads. It is not automatically canonical evidence
and cannot independently promote an evidence level.

## Current conclusion

Thermal Cascade has identified canonical architecture and model sources.
This register does not itself establish a measured cooling capacity, heating
capacity, electricity output, efficiency, safety status, construction approval,
certification, field readiness, or deployment result.


## Public calculation availability

The calculation artifacts listed above are preserved as provenance references
with recorded SHA-256 identifiers. They are not included in this public
repository as runnable code because they have not yet completed source,
license, safety, dependency, and reproducibility review. The associated
entries therefore support `documented` or `proposed` context, not an
independent public reproduction claim.
