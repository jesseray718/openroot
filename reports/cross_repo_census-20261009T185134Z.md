# cross-repo thermal asset census — 20261009T185134Z

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

### OpenCell-Thermal-System (493b590)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  2
- build evidence (photos/measurements/receipts):  4
#### Thermal-knowledgeable filenames:
thermal-power-analysis.md

### openroot-canon (5b6df5f)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  0
- build evidence (photos/measurements/receipts):  0
#### Thermal-knowledgeable filenames:

### openroot-edge (6c87fab)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  0
- build evidence (photos/measurements/receipts):  0
#### Thermal-knowledgeable filenames:

### openroot-thesis (aa2f23c)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  3
- build evidence (photos/measurements/receipts):  5
#### Thermal-knowledgeable filenames:
docs/01_ENERGY/01_SOLAR_THERMAL_LOOP.md
docs/01_ENERGY/03_STIRLING_ENGINE.md
docs/03_LIFE/01_BLACK_LOCUST_KEYSTONE.md

### openroot-spoke-template (cb9ddb1)
- BOM/spec/packet/thermal files: 
- thermal-keyword files:  1
- build evidence (photos/measurements/receipts):  2
#### Thermal-knowledgeable filenames:
bom/.gitkeep

## 2. Hygiene debt — openroot flagship
- tracked pyc:  0
- tracked bak:  0
- tracked log:  38
- tracked gz/binaries:  0

### tracked files > 5MiB (repo bloat source)
106804550	reports/gh-audit-20261008-194709/local_files.tsv
84053506	reports/zero_dimension_theory_discovery_20260929T052331Z/all_hits.txt
10493889	reports/gh-audit-20261008-194709/github_timeline.tsv

### .git size trend
300M	/home/jesse/openroot/.git

### Proposed untrack list (report only — execute separately with CONFIRM=1)
...(full list: git ls-files | grep -E '\.(pyc|bak|before)$')

## 3. Orphan deepdive_latest.md
- path: /home/jesse/deepdive_latest.md
- size:  0 bytes
- sha256: 
- verdict: integrate into reports/deepdive/ as historical baseline, then remove from home
---
CANARY:OPENROOT-CROSS-REPO-CENSUS-V1 COMPLETE
sha256: fa7ba357c587762fa2d1c9da791ba76201d96ec4f993bd174653c5468f286a76
[held] review, then human-gated commit
