## AM Window Close - 2026-09-21 (verified seal)

### Banked this window
- 668249c0 HEAD, 0 divergence from origin/main
- Rebase converged after 6 blocked attempts; root cause class fixed at source
- lessons.db UNTRACKED - rebase can never clobber chain state again
- lesson_ingest.py (0e4517a9) - argv-based idempotent ingest
- lesson_stage_v1.py (668249c0) - THE foundational entry point:
  staging chain, deterministic gates, tiered graduation, flunked-forever
- Proven live: garbage flunked id 1, real entry graduated id 17
- Chain: 17 main entries, 3 staging entries
- Bot: alive, 5 min cadence, runtime state fully quarantined from git
- Issues #68-72 tracked under milestone 7

### The self-interference class (5+ sightings, all chained or staged)
pgrep wrapper self-match, ssh heredoc quoting, daemon git-churn,
ingest dirtying tracked db, tracked-db swap during rebase, quote stripping.
Audit lens for all future tools: decouple write-paths and check-paths from
the state that contains or verifies the tool.

### Next window top-3
1. Port REAL refine_next.sh from session-2026-09-16 remnants - replace stub
2. Route all new lessons through lesson_stage_v1 - legacy ingest retired
3. README: merge docs/README.draft.md with live Four Engines README (human gate)

Launch line: "Read context_bridge/handoff_window-close-20260921-am.md.
New entry point is lesson_stage_v1 - stage, check, then human gate.
Port the real refinery worker."
