# cross-repo thermal asset census — 20261009T181639Z

## 1. Thermal/asset census per sibling repo

### aerocement (07c52be)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  13
- build evidence (photos/measurements/receipts):  13
#### Thermal-knowledgeable filenames:
docs/groq-cascade-reference.md
nanobots/L0_Thermal_Unit.sh
observations/thermal_20260717_041624.log
tools/groq/groq_cascade.py

### aerocement-panel-v0 (52ac273)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  0
- build evidence (photos/measurements/receipts):  1
#### Thermal-knowledgeable filenames:

### black-locust-rmh (e21d86e)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  2
- build evidence (photos/measurements/receipts):  0
#### Thermal-knowledgeable filenames:
from_sd/black-locust-rmh/ALPINE-SSH.md
from_sd/black-locust-rmh/FIRST_DELTA_T.md
- OpenCell-Thermal-System: MISSING at /home/jesse/OpenCell-Thermal-System
- openroot-canon: MISSING at /home/jesse/openroot-canon

### openroot-edge (6c87fab)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  0
- build evidence (photos/measurements/receipts):  0
#### Thermal-knowledgeable filenames:
- openroot-thesis: MISSING at /home/jesse/openroot-thesis
- openroot-spoke-template: MISSING at /home/jesse/openroot-spoke-template

## 2. Hygiene debt — openroot flagship
- tracked pyc:  89
- tracked bak:  35
- tracked log:  38
- tracked gz/binaries:  16

### tracked files > 5MiB (repo bloat source)
20118554	reports/theorem_discovery_20260929T044849Z/text_files.txt
20118554	reports/theorem_discovery_20260929T044755Z/text_files.txt
16718606	ledger/expansions/archives_openroot--1-.32534464.manifest.jsonl
14137262	reports/theorem_discovery_20260929T044849Z/keyword_hits.txt
14137262	reports/theorem_discovery_20260929T044755Z/keyword_hits.txt
11431754	reports/theorem_discovery_20260929T044849Z/direct_concepts.txt
9827341	.next/cache/webpack/client-development/1.pack.gz
6034523	.next/static/chunks/main-app.js

### .git size trend
253M	/home/jesse/openroot/.git

### Proposed untrack list (report only — execute separately with CONFIRM=1)
__pycache__/ecosystem.cpython-312.pyc
__pycache__/extract_3b.cpython-312.pyc
__pycache__/hybrid_search.cpython-312.pyc
__pycache__/kernel_gate.cpython-312.pyc
__pycache__/knowledge_ledger.cpython-312.pyc
__pycache__/openroot_core.cpython-312.pyc
__pycache__/openroot_engine.cpython-312.pyc
__pycache__/orchestrate.cpython-312.pyc
__pycache__/permaculture_gate.cpython-312.pyc
__pycache__/repair_loop.cpython-312.pyc
__pycache__/review_loop.cpython-312.pyc
__pycache__/search_index.cpython-312.pyc
__pycache__/setup_pipeline.cpython-312.pyc
__pycache__/une_cli.cpython-312.pyc
attic/quarantine-20261009/newton_daemon.py.pre_linkage_fix.20261009T030912Z.bak
attic/quarantine-20261009/newton_daemon.py.pre_linkage_fix.20261009T044159Z.bak
attic/quarantine-20261009/newton_daemon.py.pre_linkage_fix.20261009T044408Z.bak
automation/checks/__pycache__/claim_boundary.cpython-312.pyc
automation/checks/__pycache__/newton_chain_validate.cpython-312.pyc
automation/checks/__pycache__/provenance.cpython-312.pyc
automation/checks/__pycache__/public_boundary.cpython-312.pyc
bin/a1_core_v1.py.pre_bounded_roots.20260926T215133Z.bak
bin/a1_core_v1.py.pre_ledger_scan_repair.20260926T214851Z.bak
bin/a1_core_v1.py.pre_ledger_scan_repair.20260926T214957Z.bak
bin/handoff_manager.py.pre_bounded_end.20260926T215929Z.bak
bin/handoff_manager.py.pre_end_session_tuple_fix.20260926T220321Z.bak
bin/handoff_manager.py.pre_secrets_import.20260926T221131Z.bak
bin/handoff_manager.py.pre_session_id_collision_fix.20260926T220915Z.bak
bin/handoff_manager.py.pre_session_id_collision_fix.20260926T220956Z.bak
bin/handoff_manager.py.pre_session_id_collision_fix.20260926T221036Z.bak
bin/handoff_manager.py.pre_session_id_format_fix.20260926T221344Z.bak
bin/handoff_manager.py.pre_session_id_format_fix.20260926T221515Z.bak
bin/handoff_manager.py.pre_session_id_format_fix.20260926T221628Z.bak
bin/handoff_manager.py.pre_single_session_repair.20260926T220226Z.bak
bin/handoff_manager.py.pre_start_idempotency_fix.20260926T220804Z.bak
bin/launch_ladder_v1.py.pre_bounded_handoff.20260926T215929Z.bak
bin/launch_ladder_v1.py.pre_bounded_ledgers.20260926T215444Z.bak
bin/launch_ladder_v1.py.pre_mistake_runner_fix.20260926T210256Z.bak
bin/launch_ladder_v1.py.pre_mistake_runner_fix_v2.20260926T210713Z.bak
bin/launch_ladder_v1.py.pre_registration_fix_v2.20260926T201522Z.bak
...(full list: git ls-files | grep -E '\.(pyc|bak|before)$')

## 3. Orphan deepdive_latest.md
- path: /home/jesse/deepdive_latest.md
- size:  100403081 bytes
- sha256:  4d6a26f58bc40ac921ae361df082884e91c39f3fd5eed28a475b1f2412d60e14
- verdict: integrate into reports/deepdive/ as historical baseline, then remove from home
---
CANARY:OPENROOT-CROSS-REPO-CENSUS-V1 COMPLETE
sha256: f61553a515533d3afced8f5bc436a7867a6fb9d3ffd42146e12b00e3ce950075
[held] review, then human-gated commit
