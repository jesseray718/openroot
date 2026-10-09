# UPGRADE PLAN — DRAFT (nothing executed)

Sources: github=/home/jesse/openroot/reports/gh-audit-20261008-194709 | mirror=/home/jesse/.openroot_gh_audit/mirror-openroot.git

## A. Recovery candidates (local content absent from GitHub)
See sessions marked ADD-CANDIDATE / CLONE-REVIEW in RECONCILE.md.

## B. GitHub-only content (local restore candidates), top 40 by size

- scripts/permaculture_router.py  28400 bytes  first seen 2026-10-03T13:27:02-05:00
- scripts/openroot_audit.py  13705 bytes  first seen 2026-10-05T14:26:21-05:00
- README.md  8803 bytes  first seen 2026-10-03T12:36:45-05:00
- bin/ecosystem_v2.py  8185 bytes  first seen 2026-10-08T05:52:05-05:00
- scripts/permaculture_ci.py  7610 bytes  first seen 2026-10-03T13:27:02-05:00
- automation/checks/public_boundary.py  7423 bytes  first seen 2026-10-03T04:58:21-05:00
- scripts/validate_newton_chain.py  6326 bytes  first seen 2026-10-03T14:00:20-05:00
- bin/audit_bin_python_v1.sh  6281 bytes  first seen 2026-10-08T04:21:45-05:00
- bin/bottom_tier_nanobot_v1.py  6133 bytes  first seen 2026-10-04T22:05:45-05:00
- bin/file_ledger_v2.py  5832 bytes  first seen 2026-10-08T04:20:01-05:00
- bin/openroot_genesis_engine.py  5190 bytes  first seen 2026-10-08T16:14:55-05:00
- context_bridge/handoff-ai-window-2026-10-08T2200.md  5113 bytes  first seen 2026-10-08T16:21:33-05:00
- automation/checks/newton_chain_validate.py  4975 bytes  first seen 2026-10-03T04:58:21-05:00
- docs/newton_chain/EXAMPLES/thermal_energy_bound.yaml  4879 bytes  first seen 2026-10-03T03:09:07-05:00
- context_bridge/session-2026-10-06-hygiene-authui-extract-seal.md  4805 bytes  first seen 2026-10-05T22:27:16-05:00
- bin/workflow_dispatcher_v1.py  4805 bytes  first seen 2026-10-04T22:21:31-05:00
- bin/zone3_closeout_and_goals_rebuild_v1.sh  4611 bytes  first seen 2026-10-08T04:21:45-05:00
- bin/aerocement_cps_engine.py  4371 bytes  first seen 2026-10-08T16:14:55-05:00
- designs/thermal-cascade/THEORY_AND_EVIDENCE.md  4344 bytes  first seen 2026-10-03T13:18:50-05:00
- bin/spine_v1.py  3803 bytes  first seen 2026-10-08T06:03:24-05:00
- .github/workflows/public-boundary.yml  3803 bytes  first seen 2026-10-03T04:58:21-05:00
- designs/thermal-cascade/PROVENANCE.md  3764 bytes  first seen 2026-10-03T13:18:50-05:00
- bin/batch_nomic_embed_v3.py  3583 bytes  first seen 2026-10-08T04:21:45-05:00
- docs/PERMACULTURE_ROUTER.md  3524 bytes  first seen 2026-10-03T13:27:02-05:00
- bin/hash_ledger_v1.py  3523 bytes  first seen 2026-10-08T04:20:01-05:00
- .github/workflows/docs-build.yml  3506 bytes  first seen 2026-10-03T04:58:21-05:00
- docs/RELEASE_PROCESS.md  3444 bytes  first seen 2026-10-03T13:18:50-05:00
- scripts/ledger.py  3388 bytes  first seen 2026-10-05T06:07:47-05:00
- docs/newton_chain/ELEMENTS.md  3221 bytes  first seen 2026-10-03T03:09:07-05:00
- docs/PUBLIC_BOUNDARY.md  3218 bytes  first seen 2026-10-03T12:36:45-05:00
- scripts/knowledge_ledger.py  2979 bytes  first seen 2026-10-05T04:01:08-05:00
- bin/file_ledger_parallel_v1.py  2789 bytes  first seen 2026-10-08T04:20:01-05:00
- bin/file_ledger_v1.py  2765 bytes  first seen 2026-10-08T04:20:01-05:00
- bin/kai  2739 bytes  first seen 2026-10-05T02:11:26-05:00
- bin/newton_chain.py  2649 bytes  first seen 2026-10-08T16:14:55-05:00
- context_bridge/mistake_solutions/hashing-session-20261008.md  2634 bytes  first seen 2026-10-08T04:20:01-05:00
- .github/public-docs-policy.yaml  2622 bytes  first seen 2026-10-03T04:58:21-05:00
- automation/checks/claim_boundary.py  2555 bytes  first seen 2026-10-03T04:58:21-05:00
- bin/newton_daemon.py  2533 bytes  first seen 2026-10-08T16:14:55-05:00
- bin/ledger_seed_merge_v1.py  2508 bytes  first seen 2026-10-08T04:20:01-05:00

## C. CRLF variants — normalize before re-adding (up to 40)


## Proposed next actions (awaiting sign-off)
1. Per ADD-CANDIDATE session: explicit `git add` file list, one commit
   per session — preserves the work timeline in history.
2. CLONE-REVIEW dirs: diff each clone's HEAD vs origin before retiring
   (scriptable on request).
3. If CRLF variants appear: settle a .gitattributes policy once, then
   normalize in a single commit.
4. GITHUB-ONLY items: restorable via checkout; verify none are files
   you deliberately deleted locally.

Caveats: clone working-tree mtimes reflect clone/checkout time, not
authoring — authoring time for cloned dirs lives in that clone's git
log. GITHUB-ONLY accuracy depends on the local inventory's coverage.
Nothing above runs without explicit approval.
