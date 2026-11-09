# PATHWAYS — the cached way to do things here

Generated from the sealed pathway cache (`pathway_cache.jsonl`); every entry is hash-chained, so this
document can be regenerated at any time with `python3 bin/pathway_cache_v1.py export-md PATHWAYS.md`.
Replay a pathway by hand, step by step. Nothing here runs automatically.

## #1 — baseline friction scan

- actor: jesse
- sealed: 2026-11-03T06:09:10
- parent: #0
- hash: `3df4aa83ce46664b5a50c522c6520393...`

_rollout v20261103a baseline; fix HIGH first, then MED_

Steps:

1. `python3 bin/friction_observer_v1.py --write-ledger data/friction_ledger.jsonl --json data/friction_report.json`

Evidence (sealed by hash):

| file | bytes | sha256 |
|---|---|---|
| `/home/jesse/openroot/data/friction_report.json` | 444951 | `316c2a896960206d9d20ec71872e70d9...` |

## #2 — friction-20261103-high-anchors

- actor: jesse
- sealed: 2026-11-03T12:07:25
- parent: #1
- hash: `a956e4ae697ced377f0f10cb2b7c2860...`

_No deletes. Salvage moved to attic. Anchors are placeholders only._

Steps:

1. `stash salvage tree + create six root entry-point anchors`

Evidence (sealed by hash):

| file | bytes | sha256 |
|---|---|---|
| `/home/jesse/openroot/data/friction_report.json` | 445356 | `56f813d13dc36f5e71647ec865b52724...` |

## #3 — ai-hybrid-force-fractal-20261104T124203Z

- actor: jesse
- sealed: 2026-11-05T04:27:02
- parent: #1
- hash: `2f8acea286c86f49bde480072e32304f...`

_forced-absolute-path-fractal_

Steps:

1. `friction_observer`
2. `question_travel`
3. `pods_fractal_force`

Evidence (sealed by hash):

| file | bytes | sha256 |
|---|---|---|
| `/home/jesse/openroot/outbox/ai_hybrid_loop/20261104T124203Z/friction_report.json` | 250670 | `8542ca084f9b43829875a376dafa66b2...` |
| `/home/jesse/openroot/outbox/ai_hybrid_loop/20261104T124203Z/QUESTION_TRAVEL.json` | 871 | `5f5bd9a33e56d69830aed85a9d2a2513...` |
| `/home/jesse/openroot/outbox/ai_hybrid_loop/20261104T124203Z/PODS_FRACTAL.json` | 3752 | `c176709d442d14ca12f52617b4c16b75...` |

## #4 — intensity-chain-20261105T070124Z

- actor: jesse
- sealed: 2026-11-05T07:03:26
- parent: #1
- hash: `9cc611a5f5c2fa8ecc42c7365edcc548...`

_same pods; chained Qs bind prior answer_hash + pathway_flag; intensity L1-L3_

Steps:

1. `intensity_L1_surface`
2. `intensity_L2_bind`
3. `intensity_L3_intensify`

Evidence (sealed by hash):

| file | bytes | sha256 |
|---|---|---|
| `/home/jesse/openroot/outbox/intensity_chain_20261105T070124Z/INTENSITY_CHAIN.json` | 5273 | `09bcadcd3818a19850669a31de0d24e1...` |
| `/home/jesse/openroot/outbox/intensity_chain_20261105T070124Z/CHAIN_RECEIPT.md` | 1236 | `7d92118d1273a737351a1ee1faef1fc6...` |

---

To add a refinement, record it with `--parent <seq>` of the pathway you improved. The chain is the compounding.
