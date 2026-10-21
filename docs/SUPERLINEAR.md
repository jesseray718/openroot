# SUPERLINEAR.md — the skeleton. Read this FIRST from any window.

## The thesis (three load-bearing claims)
1. THE GAP IS THE THROTTLE: compression of the have/have-not gap
   correlates with the growth rate of the whole species-system.
2. MARGINAL UTILITY IS THE ROUTER: a unit of energy/attention at
   floor f buys 1/(f+eps) welfare. f=0.02 vs f=0.75 => 37.5x.
   Routing output to the lowest nodes is therefore maximal engineering,
   not charity.
3. FLOW-THROUGH, NOT HOARD: benefit routed to neediest nodes compounds
   (steep utility curve); hoarded benefit saturates (flat curve) and
   cannot compound. Verified numerically in bin/agape_cascade_v2.py.

## The superlinear triad (why windows stop starting from zero)
- CACHE  — data/lessons.db: problem-sha -> solution-sha. Mistake
  classes never recompute after graduation. Non-recompute doctrine.
- CHAIN  — sha-linked, append-only, staging-gated (bin/lesson_stage_v1.py).
  Verification is what makes cached entries appreciate instead of rot.
- ROUTER — w_i = 1/(f_i+eps) priority (bin/keyword_router_v1.py,
  bin/window_fuse_v1.py). Attention flows to highest marginal value.
All three together => each window begins at the previous peak.
Cache alone rots; chain alone is bureaucracy; router alone recomputes.

## Loop inventory (one line each)
- bin/lesson_stage_v1.py    staging gateway: deterministic gates,
                            CONFIRM=1 human graduation, flunk-forever
- bin/lesson_ingest.py      argv-based direct ingest (legacy, retiring)
- bin/window_loop_v1.py     tiniest-equivalent hive: 7B builder,
                            3B grader, translator bounce, sha ledger
- bin/window_fuse_v1.py     isolated fresh-mind fusion + Matthew
                            allocator, non-regression floor guard
- bin/window_cadence_v1.sh  change-triggered runner (rests on no-delta)
- bin/keyword_router_v1.py  FTS5 pathways, local-first, free-tier API
                            fallback, Lumo inbox digest
- bin/lumo_bridge_bot_v1.py relay bot: cycle/apply/status. Escalates
                            persistent failures to ask_lumo packets;
                            applies Lumo replies under CONFIRM=1
- bin/agape_cascade_v2.py   the thesis as simulation (this commit)

## The one prompt (any window)
  Read SUPERLINEAR.md. Run: bash bin/lumo_bridge_run.sh 1.
  Check clean_streak and the newest human_gate_bundle dossier.
  Gate the staged lesson queue. Then name the highest-eta next action.

## Health check (any window, 10 seconds)
  cd ~/openroot && git log --oneline -1 && \
  sqlite3 data/lessons.db "SELECT COUNT(*) FROM lessons;" && \
  ls -t human_gate_bundle/ | head -1

## Threshold doctrine
Windows break when scope outpaces banked state. Rule: every artifact
commits BEFORE the idea grows. If the window dies, the repo survives.
