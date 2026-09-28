---
id: 70ccef38aa30cee1
ts: 2026-09-27 22:49:35
type: mistake-solution
status: solved
agape_score: high
---
# Mistake 70ccef38aa30cee1

SHA256-shape key: 70ccef38aa30cee1

## Solution
mistake_engine_v1.py exposes hook|solve|show|compost — no list subcommand. Ladder mistake_engine_ready runner invoked "list" causing a usage error on every real run. Fix: retargeted runner to the valid "compost" subcommand in launch_ladder_v1.py; re-ran rung to re-earn green.

## Correction (2026-09-28)
Root cause attribution refined: the runner was already 'compost' (line 60). The
invalid 'list' subcommand lived in the CALIB probe (line 59), masked by an
'|| echo engine alive' fallback that forced exit 0 — the classic error-swallow.
Occurrence #1 was triggered by the FUSEDIAG1 diagnostic invoking 'list'
directly. Class: ERROR-SWALLOW-BY-FALLBACK — calib probes must not mask
subcommand failures with || echo success strings.
