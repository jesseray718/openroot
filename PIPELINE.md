# OpenRoot Pipeline — Canonical Flow

Unit of flow: the evidence-gated design packet.
Entry point for all routed work: `bin/openroot_superlinear_v1.py`

## Pre-route gauntlet (every task, before any model spends a joule)
1. canonicalize task (stopwords stripped, params ordered) -> SHA-256
2. CACHE hit?        -> return verified result       [free]
3. mistake chain hit? -> return recorded correction   [free]
4. FTS5 retrieval?   -> return sources, route the GAP only [~free]
5. miss              -> route to smallest capable model (model_registry.json)

Results are banked back via `bank()` only after verification.
Runtime DBs, logs, harvest/ stay UNTRACKED (regenerable state).
Thermal claims: low-grade pre-heat only, COP-boundary language. Never ">100%".
Human is the sole commit/push/release gate.

## Data Doctrine (config vs runtime)

Tracked = config, rewritten only by deliberate human-gated commits:

- `data/model_registry.json` — routing weights, provenance-worthy. Tooling READS
  this file; only the human gate WRITES it. Auto-rewrites land in
  `data/operator_holds/` for review instead.

Untracked = runtime derivatives, regenerated freely on disk:

- `data/superloop_chains.json` — analytics VIEW re-derived from command history
  each pulse. Immutable source is the SQLite ledger + mistake_solutions/.
- `context_bridge/superloop_DASHBOARD.md` — cron-pulsed dashboard (15 min).
  Regen templates must re-add the SPDX header before any future re-tracking.

Rule: a file is tracked XOR machine-written. Never both.
