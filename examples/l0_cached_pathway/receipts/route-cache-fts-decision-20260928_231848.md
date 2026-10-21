# Route Cache / FTS Decision

Timestamp: 2026-09-28T23:18:48-05:00
Run: /home/jesse/openroot/.tinycrew/runs/tinycrew-20260928_221311

## Verified facts

- route_cache.db exists at:
  /home/jesse/openroot/data/route_cache.db

- route_cache contains one verified, provenance-linked exact-cache route.

- Exact lookup through route_cache.query is operational:
  EXACT_REUSE = PASS

- route_cache_fts is an existing FTS5 external-content table:

  route_cache_fts(query, response, content='route_cache', content_rowid=rowid)

- route_cache_fts has no synchronization triggers.

- route_cache_fts MATCH queries return no result for the verified route.

- FTS state is:

  HELD_UNSYNCED_FTS_INDEX

## Existing writer assessment

Existing script:

  bin/offline_route_cache_v1.sh

Observed behavior:

- Creates route_cache and route_cache_fts if missing.
- Uses SQL string interpolation rather than parameter binding.
- Mutates hits during lookup.
- Stores route records with generic "network" provenance.
- Does not synchronize external-content FTS5.
- Has an offline-check mode that performs external DNS/TCP probes.

Decision:

  DO_NOT_USE_FOR_SUPERLOOP_PROMOTION

Allowed use:

  Schema/history evidence only.

## Active routing policy

L0 exact cache:
  ACTIVE

L1 FTS5:
  HELD_UNSYNCED_FTS_INDEX

L2 embeddings:
  UNKNOWN_EMBED_INTERFACE

L3 local-model dispatch:
  HELD_UNBENCHMARKED

RAPL metrics:
  HELD_UNKNOWN_METRICS_SCHEMA

Git actions:
  HUMAN_GATE_REQUIRED

## Next safe engineering item

Build a dedicated, audited route-cache maintenance adapter only after:

1. the dirty worktree is isolated,
2. the update semantics are explicitly reviewed,
3. an FTS synchronization mode is chosen,
4. a bounded one-row test is approved,
5. rollback evidence is prepared.

No FTS rebuild, FTS direct write, trigger creation, schema change, model dispatch,
network probe, or Git mutation was performed by this decision record.
