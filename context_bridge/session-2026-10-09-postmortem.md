# Session Seal: Post-Rewrite Postmortem — 2026-10-09

## Verified State
- HEAD on main, pushed to origin, remote == local (D-04 closed)
- .git: 5.8G -> 167M (size-pack 161 MiB)
- Ledger green: 798 files, verify.sh OK
- Newton: timer firing every 15 min, oneshot unit Result=success, chain restarted genesis-clean with hash:->prev fix baked in
- bin/: 9 scripts restored from 5 strata (mirror, staging, .bak siblings, tap log, disk trees); 8 remain missing

## Failure Classes Registered Tonight
- F-PLACEHOLDER-LITERAL: template command pasted with literal <commit-hash> — scripts must compute candidates themselves
- F-REWRITE-COLLATERAL: filter-repo expunged paths holding untracked working files; salvage-copy expunge list BEFORE rewrite
- F-ADD-PATHSPEC-ABSENT: git add on absent dir is fatal under set -e — guard each pathspec
- F-GATE-FALSE-NEGATIVE: is-active on a finished oneshot reads "inactive" = success; instrument must know the workload type

## Still Missing (rebuild-from-scar items)
watchdog_once.py, lumo_ingest.py, superloop_composite_v3.py, measure_thermal_v1.py,
task_dispatch_v1.sh, ws_auto_sync.sh, openroot_rapl_sampler_v1.py, 1349_bottom_tier.py
-> their 3 cron lines are parked as disabled; revive one by one as each is rebuilt

## Next Actions (priority)
1. D-06: fresh-window boot test — open a zero-context window, resume from this handoff alone
2. Rebuild the 8 missing scripts one per day, py_compile + grep gate each, revive its cron line
3. Reh1t PR #53 (gentle: their clone is stale post-rewrite)
4. CPS fabrication strip before any grant language

## Handoff
sha256 of this file recorded on commit; latest handoff = this file
