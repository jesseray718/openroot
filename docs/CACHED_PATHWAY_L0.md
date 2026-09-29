# OpenRoot Cached Pathway L0

## Status

**L0 exact reuse is verified for one local pathway.**

This package documents a bounded vertical slice:

```text
candidate → Turing Tidbit identity → verified provenance
          → reviewed cache promotion → exact cache lookup
          → local verified response, no model dispatch
```

## What L0 does

L0 is exact reuse. It does not infer semantic equivalence.

A route is eligible only when the exact canonical key/query and its recorded
provenance match the verified cached record.

Current demonstrated record:

```text
Key:
ce678d1529540ee80d86348a813fcb331177e3a9b953752684e5a79eefc45ef9

Query:
read-only OpenRoot route cache probe

Route:
local_verification

Stored response:
490 bytes/characters in the verified local record

Provenance:
linked to a verified Turing Tidbit content identity and event evidence
```

## Components

| Component | Responsibility |
|---|---|
| `bin/turing_tidbits_v1.py` | Content-addressed artifact store, metadata identity, event receipts, integrity verification |
| `bin/tidbit_registry_v1.py` | Tidbit registry interface |
| `bin/route_promotion_plan_v1.py` | Read-only candidate planner; no cache write |
| `bin/router_cache_probe_v1.py` | Read-only exact cache probe |
| `bin/router_cache_probe_v2.py` | Exact reuse probe with explicit FTS held state |
| `bin/smart_router.py` | Future router integration point |
| `bin/offline_route_cache_v1.sh` | Historical cache helper; do not use for new writes without review |
| `bin/cache_pathway_orchestrator_v1.py` | Pathway orchestration utility |
| `examples/l0_cached_pathway/receipts/` | Sealed candidate, tidbit, repair, and FTS-decision evidence |

## Verified run sequence

1. Create a reviewed route-promotion candidate.
2. Ingest source/candidate into Turing Tidbits.
3. Verify tidbit content and metadata identities.
4. Perform a separately human-confirmed cache write.
5. Verify exact reuse through the read-only router probe.
6. Preserve a receipt for every stage.

The cache write is intentionally separate from candidate creation and tidbit ingestion.

## Read-only verification

From a real OpenRoot checkout with the live data directory present:

```bash
python3 bin/router_cache_probe_v2.py "read-only OpenRoot route cache probe"
```

Expected state for the demonstrated exact key:

```text
cache_disposition = EXACT_REUSE
status = READ_ONLY_HIT
next_state = RETURN_EXACT_RESULT_AND_HOLD_FTS_REPAIR
```

## Important limitation

The FTS5 route-cache index is **held unsynchronized**.

```text
L0 exact lookup: ACTIVE
L1 lexical/semantic FTS retrieval: HELD_UNSYNCED_FTS_INDEX
```

Do not claim FTS-based semantic cache retrieval works. Do not rebuild, synchronize,
or write the FTS index without a separately reviewed maintenance procedure.

## Safety boundary

This package does not:

- create a cache entry,
- mutate a live route cache,
- dispatch a model,
- repair FTS,
- commit, push, or publish,
- treat an approximate/semantic match as exact reuse.

Promotion to a cache write must remain explicitly human-confirmed.
