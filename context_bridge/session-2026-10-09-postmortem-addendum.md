# Addendum: Postmortem Corrections — 2026-10-09

Corrects two false asserts in the original seal:
1. The 3 oversized blobs (reports/.../all_hits.txt, logs/local_task_watch_v1.log,
   reports/dedupe/...csv) were NOT registered in ledger/expansions manifests —
   registration stage short-circuited (ghost files + missing dir). Provenance now lives
   only in this note: they were history-only ghosts, absent from working tree.
2. Original seal claimed "pushed, remote==local" before push succeeded — true state
   was banked only at c9fe000 after second filter-repo pass.
Verified-at-write: see grep output below in same script run — [banked] or abort.
