== STAGE A [inventory] GOALS/MASTER_TODO/TASK ==
[banked] GOALS.md: 19 lines, 1166 bytes, sha256=265212b51fb9fd7b
[banked] MASTER_TODO.md: 25 lines, 1614 bytes, sha256=41bd33ead3885590
[banked] TASK.md: 8 lines, 257 bytes, sha256=0887654193accac5
== STAGE B [rebuild-drafts] supersession check ==
[held] draft present: GOALS.rebuild.20260920_014329.md (10 lines) — superseded by on-disk original; delete after review
[held] draft present: MASTER_TODO.rebuild.20260920_014329.md (3 lines) — superseded by on-disk original; delete after review
[held] draft present: MASTER_TODO.rebuild.v2.md (4 lines) — superseded by on-disk original; delete after review
== STAGE C [git-state] ==
[banked] HEAD: 89563927 | working-tree dirty lines: 18
     A GOALS.rebuild.20260920_014329.md
     A MASTER_TODO.rebuild.20260920_014329.md
     A MASTER_TODO.rebuild.v2.md
    ?? bin/master_harvest_v3_20260920.py
    ?? bin/next_actions_20260920_v1.sh
    ?? bin/next_actions_v2_20260920.py
    ?? bin/secure_and_commit_v4_20260920.py
    ?? bin/secure_and_commit_v5_20260920.py
    ?? context_bridge/report-master-harvest-20260920_020335.md
    ?? context_bridge/report-next-actions-20260920_014329.md
    ?? context_bridge/report-next-actions-v2-20260920_015234.md
    ?? context_bridge/report-next-actions-v2-20260920_015411.md
    ?? data/master_heads_ledger_20260920_020335.json
    ?? data/recent_runs_20260920_014329.json
    ?? data/salvaged_tasks_20260920_014329.txt
== STAGE D [commit-proposal] ==
restore: GOALS.md (19 lines), MASTER_TODO.md (25 lines), TASK.md (8 lines) — v2.0 restructure survives on-disk post-crash

Provenance:
- GOALS/MASTER_TODO/TASK survived the filter-repo history rewrite; referenced 1ec3e352
- 2026-09-20 audit: 19+25+8 line artifacts present at repo root, hashes in report
- Fleet masters: 29 dangling refs (SHAs stripped), 0 recoverable via compare
- Rebuild drafts empty (salvage grep zero-hit across 17 context_bridge sources)

Actions:
- Commits ONLY the three surviving planning docs; no other working-tree changes
- Next: delete 29 dangling master refs fleet-wide (ledger: data/master_heads_ledger_20260920_020335.json)
[held] DRY-RUN: nothing staged, nothing committed; rerun with CONFIRM=1 to bank

## Handoff 20260920_021102
mode=DRY-RUN
next: CONFIRM commit, then fleet master deletion pass
