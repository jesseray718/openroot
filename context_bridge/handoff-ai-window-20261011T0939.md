# HANDOFF: Superlinear Spine Complete — 2026-10-11

## VERIFIED STATE
- HEAD: main @ (parse-fix commit) — pushed
- Ledger: 12 rows, 1 theorem (83c3b4f7, ROOT+bin full-audit), 0 broken, 0 lineage errors, GREEN
- Spine organs, all live:
  1. HASH replay: double cache-hit proven (id=9, id=11), 0 model calls on stable state
  2. MERKLE lineage: compose/descend/verify, backward-compatible seal formula
  3. SEMANTIC layer: thresholded cosine, MEASURED 0.42 (gap 0.385–0.551, SEPARABLE)
  4. ROUTER front door: hash-first → embed-second → model-last, three branches proven
- Key commits this arc: 5de90de (self-churn) → 9d52c9d (ride-along) → 9c67da2 (Merkle) → 20f9115 (semantic) → 28d0256 (router) → parse-fix

## SCARS (do not repeat)
- sed patching multi-line Python = 3 strikes. Full-file rewrites only.
- .bak drops in bin/ poison the audit manifest → one-time cache misses. Exclusions fixed the root cause.
- Guessed thresholds are stub-blind: 0.75 default sat ABOVE the related-floor. Probe measured 0.42.
- Committing data/pathways.db = self-churn. Git carries code; SQLite carries live truth.

## BROKEN / UNPROVEN
- Router seal→embed auto-invocation of embed_backfill_v1.py: CLI signature unverified. Exercise once, check [banked] vs [held].
- Audit prompt quality: 7B echoes scripts instead of per-file risk enumeration. Unvalidated.

## NEXT ACTIONS (priority)
1. Triage untracked backlog revealed by git status (41 files: phi_router_harness_v2/v3, estate topology, router receipts v2-v4, relay canaries, scripts/audit/*)
2. Verify embed_backfill_v1.py interface from router seal path
3. Tighten audit system prompt (per-file risks)
4. Populate embedding store — more diverse seals = firmer threshold = higher semantic-cache rate
5. Absorb into weekly onepass_v3.sh
