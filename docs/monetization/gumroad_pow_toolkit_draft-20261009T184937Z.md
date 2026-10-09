# Gumroad Listing Draft — PoPW Evidence Chain Toolkit (v1, PIVOTED from thermal packet)

## Why pivoted
Cross-repo census 20261009T181129Z: sibling thermal repos thin (15 files) / mostly
missing locally. Flagship inventory: 97 ledger/chain/PoPW files. Sell what's deep.

## Title
Proof-of-Physical-Work Evidence Chain Toolkit — tamper-evident logging for makers, labs, and builds

## Price
$19 launch, raise to $29 after 30 sales. Free tier: core scripts stay GPL-3.0 in repo.

## Pitch
Chain of custody for physical work: sensor readings, energy measurements (RAPL
microjoules), and build evidence hashed SHA-256, chained, and timestamped into SQLite.
Broken links expose tampered or corrupted evidence — automatically, not by vibes.

## Contents
- popw_ledger.py lineage (chained append, tamper detection, audit walk)
- Joule accounting harness: RAPL reads with ESTIMATE fallback, thermo ledger schema
- Dedup + cache pathway layer (hash lookup prevents recomputation — the eta lever)
- Multi-model gate integration (3B grader pre-check, human commit gate)
- Setup runbook: Ollama + nomic-embed + SQLite + FTS5, tested on Ubuntu 24.04 + Termux
- Verification checklist: how to prove a chain is intact, what broken links mean
- 3 worked examples from live deployments (compute energy, thermal cascade, corpus sweep)

## Honesty layer
Everything's GPL-3.0 in the public repo. You're buying curation, the runbook,
worked configs, and a support thread. State it plainly.

## Needed from Jesse
[ ] pick 3 cleanest worked examples from live runs
[ ] smoke-test runbook end-to-end on fresh clone
[ ] support channel decision (email/GitHub Discussions)
[ ] screenshots: audit walk output, broken-link detection demo (THE money shot)
