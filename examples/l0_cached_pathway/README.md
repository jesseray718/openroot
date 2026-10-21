# L0 Cached Pathway Evidence

This directory contains only reviewed source copies and sealed evidence receipts
for the first documented OpenRoot exact cache pathway.

It intentionally excludes:

- live SQLite databases,
- Turing Tidbit object storage,
- user documents,
- model artifacts,
- secrets,
- runtime logs,
- unrelated worktree state.

Run:

```bash
OPENROOT_LIVE_ROOT=/path/to/live/openroot \
  scripts/verify_cached_pathway_l0.sh
```

The live root must contain `data/route_cache.db` with the documented exact record.

The verifier is read-only with respect to the route cache. It performs syntax checks,
validates copied evidence receipts, checks SQLite integrity, confirms the exact key,
and invokes the existing read-only cache probe.
