# OpenRoot OSHW Supporting Documents Catalog

- Generated: `2026-09-28T14:03:19-05:00`
- Host: `optiplex3060`
- Repository: `/home/jesse/openroot`
- Mode: read-only discovery and catalog generation; no tracked-source edits, staging, commits, pushes, GitHub changes, service changes, or process changes.
- Human hold: `/home/jesse/openroot/data/operator_holds/HUMAN_HOLD`

## Repository identity

```text
/home/jesse/openroot
main
HEAD=2e9c68398fb4d2be67c08bde2441bf8826925788
DATE=2026-09-27T23:58:33-05:00
SUBJECT=[FIX] handoff: fill PR #9 URL placeholder (AI-assisted, human-gated)
Reh1t	https://github.com/Reh1t/openroot.git (fetch)
Reh1t	https://github.com/Reh1t/openroot.git (push)
origin	git@github.com:jesseray718/openroot.git (fetch)
origin	git@github.com:jesseray718/openroot.git (push)
upstream	https://github.com/jesseray718/openroot.git (fetch)
upstream	https://github.com/jesseray718/openroot.git (push)
MM .gitignore
A  bin/concept_sweep_v1.sh
A  bin/doc_gap_scan_v1.py
A  bin/mistake_index_v1.py
 M bin/refine_next.sh
A  bin/tidbit_registry_v1.py
A  context_bridge/concepts/a_language_agape_v1.md
A  context_bridge/concepts/modular_turing_tidbit_v1.md
A  context_bridge/handoffs/session-20260928_004510-superlinear-instruments.md
A  context_bridge/handoffs/session-20260928_010158-concepts-banked-corrected-sweep.md
?? bin/a15_courier_endpoint_v1.py
?? bin/dedup_pipeline_v1.py
?? bin/expertise_orchestrator_v1.py
?? bin/lumo_relay_full_v1.py
?? bin/openroot_deepdive_v1.sh
?? bin/openroot_local_loop_v2.sh
?? bin/quarantine_pyfails_final_v2/
?? bin/refine_next.sh.bak_20260928_051638
?? bin/run_expertise_auto_v1.py
?? bin/vision_all_v1.sh
?? context_bridge/compost-20260926_053011.md
?? context_bridge/compost-20260926_160713.md
?? context_bridge/compost-20260926_160847.md
?? context_bridge/compost-20260926_160848.md
?? context_bridge/compost-20260927_144218.md
?? context_bridge/compost-20260927_224935.md
?? context_bridge/compost-20260928_053006.md
?? context_bridge/composted_scripts_20260927/
?? context_bridge/concept_mining/
?? context_bridge/concept_sweeps/
?? context_bridge/concepts/core_atomic_enum_draft.md
?? context_bridge/court-v6-report-20260926_040026.md
?? context_bridge/court-v6-report-20260927_144215.md
?? context_bridge/court-v6-report-20260928_040010.md
?? context_bridge/gov_promote_proofs_20260928_041935/
?? context_bridge/gov_smoke_final_20260928_045548/
?? context_bridge/governor_promote_20260928_041935.md
?? context_bridge/grep_sweep_20260927_205737/
?? context_bridge/grep_sweep_20260927_205916/
?? context_bridge/handoffs/session-20260926_225700-ladder-7of8.md
?? context_bridge/handoffs/session-20260927_230746-fusion-sealed-2265c4aa.md
?? context_bridge/handoffs/session_20260926T221516Z_c6f0d97375d6355b.md
?? context_bridge/handoffs/session_20260926T221629Z_6916f7ea0432b4f2.md
?? context_bridge/handoffs/session_20260926T221842Z_d97bcefd328c622f.md
?? context_bridge/handoffs/session_20260926T221843Z_c6414b332a20e5d7.md
?? context_bridge/handoffs/session_20260926_215535_55b7ba7c.md
?? context_bridge/handoffs/session_20260926_215639_69ae6e70.md
?? context_bridge/handoffs/session_20260926_220435_6c2d280e.md
?? context_bridge/handoffs/session_20260926_220617_80fa6c9e.md
?? context_bridge/handoffs/session_20260926_220805_6953c9af.md
?? context_bridge/handoffs/session_20260928T040209Z_d7e48356999db7ff.md
?? context_bridge/handoffs/session_session_20260926T221132+0000_7c2056b18e27b61c.md
?? context_bridge/handoffs/session_session_20260926T221133+0000_5a4cf6fec1712d95.md
?? context_bridge/hive_canonical_20260928_041449/
?? context_bridge/kai_deep_harvest_20260928_024955/
?? context_bridge/lumo_inbox/
?? context_bridge/mistake_solutions/06ad87aa44efc30b.md
?? context_bridge/mistake_solutions/193af16dcf503af5.md
?? context_bridge/mistake_solutions/27ab944372909f1c.md
?? context_bridge/mistake_solutions/a71a4e72670407be.md
?? context_bridge/mistake_solutions/ab68e66064bffdd0.md
?? context_bridge/mistake_solutions/afbd8ad75c5a820b.md
?? context_bridge/mistake_solutions/e579225f90e59b48.md
?? context_bridge/relay-recovery-20260926_040359.md
?? context_bridge/session-handoff-20260928-0456/
?? context_bridge/tree_optiplex_home.txt
?? context_bridge/tree_optiplex_openroot.txt
?? context_bridge/tree_optiplex_src.txt
?? context_bridge/tree_snapshot_latest.txt
?? context_bridge/turing_tidbits/
?? data/kai_import_20260928_015017.tar.gz
?? data/ladder_diagnostics/
?? data/openroot_knowledge/
?? data/operator_holds/
?? data/superlinear/
?? data/turing_tidbits/
?? hash_assign_smoke/
?? hash_assign_v1.sh
?? quarantine_compile_fails_20260926_142638/
?? quarantine_handoff_corrupt/
```

## Human hold

```text
-rw------- 1 jesse jesse 657 Sep 28 08:06 /home/jesse/openroot/data/operator_holds/HUMAN_HOLD
OPENROOT HUMAN MUTATION HOLD

This local-loop system may inspect repository state, ingest text inbox items,
read SQLite ledgers, create reports, and generate local-model proposals.

It must not automatically:
- modify tracked project files
- stage, commit, push, merge, or create pull requests
- dispatch, rerun, or cancel GitHub Actions workflows
- restart, kill, or reconfigure services and processes
- delete files or databases
- use remote APIs, cloud models, external compute, blockchain, wallets,
  transactions, signing, bridges, token operations, mining, or P2P routing

Remove this file manually only after reviewing a bounded human-approved plan.
```

## Existing OSHW framework documents

```text
PRESENT README.md 8365 bytes
PRESENT docs/REPOSITORIES.md 4565 bytes
PRESENT docs/DESIGN_PACKETS.md 532 bytes
PRESENT docs/EVIDENCE_LEVELS.md 526 bytes
PRESENT docs/OPEN_HARDWARE_STATUS.md 1426 bytes
ABSENT  docs/SAFETY.md
PRESENT CONTRIBUTING.md 1559 bytes
PRESENT LICENSE 35149 bytes
ABSENT  LICENSE.md
PRESENT SECURITY.md 108 bytes
PRESENT CODE_OF_CONDUCT.md 77 bytes
PRESENT designs/thermal-cascade/README.md 1319 bytes
PRESENT designs/thermal-cascade/STATUS.md 535 bytes
PRESENT designs/thermal-cascade/BOM.md 1468 bytes
PRESENT designs/thermal-cascade/BUILD.md 1432 bytes
PRESENT designs/thermal-cascade/TEST_PLAN.md 1691 bytes
PRESENT designs/thermal-cascade/MEASUREMENTS.md 1162 bytes
PRESENT designs/thermal-cascade/SAFETY.md 1679 bytes
```

## OSHW candidate documents in active source paths

```text
grep: Unmatched ( or \(
```

## BOM, build, test, measurement, safety, license references

```text
README.md
designs/thermal-cascade/BOM.md
designs/thermal-cascade/BUILD.md
designs/thermal-cascade/INTAKE.md
designs/thermal-cascade/LICENSE.md
designs/thermal-cascade/MEASUREMENTS.md
designs/thermal-cascade/PROVENANCE.md
designs/thermal-cascade/README.md
designs/thermal-cascade/SAFETY.md
designs/thermal-cascade/STATUS.md
designs/thermal-cascade/SYSTEM.md
designs/thermal-cascade/TEST_PLAN.md
designs/thermal-cascade/THEORY_AND_EVIDENCE.md
designs/thermal-cascade/bom/BOM.md
designs/thermal-cascade/docs/build-instructions.md
designs/thermal-cascade/docs/safety.md
designs/thermal-cascade/docs/test-protocol.md
designs/thermal-cascade/metadata.yaml
designs/thermal-cascade/release-manifest.json
designs/thermal-cascade/release/REPRODUCE.md
designs/thermal-cascade/router_context.json
docs/DESIGN_PACKETS.md
docs/EVIDENCE_LEVELS.md
docs/LESSON_RECORD_SCHEMA.md
docs/LICENSING.md
docs/OPEN_HARDWARE_STATUS.md
docs/PERMACULTURE_ROUTER.md
docs/PROJECT_ROADMAP.md
docs/README.draft.md
docs/README.md
docs/RELEASE_PROCESS.md
docs/REPOSITORIES.md
docs/SCOPE.md
docs/SUPERLOOP.md
docs/research/argf-durability.md
docs/research/cardboard-membrane.md
docs/research/cascade-heatbalance.md
docs/research/cloud9-relay.md
docs/research/dish-mesh-reflector.md
docs/research/double-skin-catenary.md
docs/research/labyrinth-cooling.md
docs/research/opencell-absorber.md
docs/research/thixo-foam.md
```

## Current GitHub OSHW repositories

```text
bash: line 63: warning: here-document at line 5 delimited by end-of-file (wanted `PY')
bash: -c: line 64: syntax error: unexpected end of file
```

## Generated catalog summary

```text

## Generated catalog summary

```text
files=65
bom=16
build=31
design=50
evidence=45
license=41
measurement=48
readme=20
safety=27
status=39
test=43

top_candidates:
designs/thermal-cascade/BOM.md | labels=bom,build,design,evidence,license,measurement,safety,status,test | bytes=1468
designs/thermal-cascade/bom/BOM.csv | labels=bom,design,measurement,test | bytes=429
designs/thermal-cascade/bom/BOM.md | labels=bom,build,design,license,test | bytes=418
designs/thermal-cascade/BUILD.md | labels=bom,build,design,evidence,license,measurement,safety,status,test | bytes=1432
designs/thermal-cascade/calculations/assumptions.md | labels=license | bytes=227
designs/thermal-cascade/calculations/formulas.md | labels=license | bytes=203
designs/thermal-cascade/docs/build-instructions.md | labels=bom,build,design,license,measurement,test | bytes=551
designs/thermal-cascade/docs/maintenance.md | labels=license | bytes=209
designs/thermal-cascade/docs/operation.md | labels=build,design,license | bytes=386
designs/thermal-cascade/docs/problem.md | labels=design,license | bytes=280
designs/thermal-cascade/docs/replication-notes.md | labels=build,evidence,license | bytes=227
designs/thermal-cascade/docs/results.md | labels=license,measurement,test | bytes=300
designs/thermal-cascade/docs/safety.md | labels=design,evidence,license,safety,test | bytes=535
designs/thermal-cascade/docs/system-architecture.md | labels=license,measurement | bytes=451
designs/thermal-cascade/docs/test-protocol.md | labels=bom,build,design,license,measurement,safety,test | bytes=587
designs/thermal-cascade/INTAKE.md | labels=bom,design,evidence,license,measurement,safety,test | bytes=2149
designs/thermal-cascade/LICENSE.md | labels=build,design,license | bytes=451
designs/thermal-cascade/MEASUREMENTS.md | labels=design,evidence,license,measurement,status,test | bytes=1162
designs/thermal-cascade/metadata.yaml | labels=design,evidence,license,measurement,safety,status | bytes=598
designs/thermal-cascade/PROVENANCE.md | labels=build,design,evidence,license,measurement,readme,safety,status,test | bytes=3139
designs/thermal-cascade/README.md | labels=bom,build,design,evidence,license,measurement,readme,safety,status,test | bytes=1319
designs/thermal-cascade/release-manifest.json | labels=design,evidence,safety,status | bytes=550
designs/thermal-cascade/release/REPRODUCE.md | labels=bom,build,design,evidence,license,measurement,safety,status,test | bytes=341
designs/thermal-cascade/router_context.json | labels=design,evidence,measurement,safety,test | bytes=1291
designs/thermal-cascade/SAFETY.md | labels=design,evidence,license,safety,status | bytes=1679
designs/thermal-cascade/STATUS.md | labels=design,evidence,license,measurement,safety,status,test | bytes=535
designs/thermal-cascade/SYSTEM.md | labels=build,design,evidence,license,measurement,readme,safety,status | bytes=4388
designs/thermal-cascade/TEST_PLAN.md | labels=design,evidence,license,measurement,safety,status,test | bytes=1691
designs/thermal-cascade/THEORY_AND_EVIDENCE.md | labels=design,evidence,license,measurement,readme,safety,status,test | bytes=3719
docs/BLOCKCHAIN-OF-CONTRIBUTIONS.md | labels=build,design,evidence,license,measurement,status,test | bytes=7558
docs/CONTRIBUTING.md | labels=evidence,measurement | bytes=290
docs/DESIGN_PACKETS.md | labels=bom,design,evidence,license,safety | bytes=532
docs/EVIDENCE_LEVELS.md | labels=design,evidence,license,measurement,safety | bytes=526
docs/GOALS.md | labels=build,design,status | bytes=863
docs/LESSON_RECORD_SCHEMA.md | labels=evidence,license,measurement,safety,status,test | bytes=662
docs/LICENSING.md | labels=build,design,license | bytes=378
docs/markdown/JSON_DATA.md | labels=measurement,status | bytes=756
docs/markdown/MARKDOWN_DOCS.md | labels=build,license,measurement,readme,status | bytes=742
docs/markdown/MASTER_INDEX.md | labels=build,measurement,readme,status | bytes=1036
docs/markdown/PYTHON_FILES.md | labels=evidence,test | bytes=1133
docs/markdown/SHELL_SCRIPTS.md | labels=build,measurement,status,test | bytes=1056
docs/MASTER_TODO.md | labels=build,design,evidence,readme,test | bytes=845
docs/OPEN_HARDWARE_STATUS.md | labels=bom,build,design,evidence,license,measurement,safety,status,test | bytes=1426
docs/OPEN_INVITATION.md | labels=build,evidence,measurement,test | bytes=698
docs/PERMACULTURE_ROUTER.md | labels=design,evidence,license,measurement,safety,test | bytes=3538
docs/PROJECT_ROADMAP.md | labels=bom,build,design,evidence,license,measurement,safety,status,test | bytes=2998
docs/README.draft.md | labels=bom,build,design,evidence,license,measurement,readme,status,test | bytes=6035
docs/README.md | labels=bom,build,design,evidence,license,measurement,readme,safety,status,test | bytes=29849
docs/RELEASE_PROCESS.md | labels=bom,build,design,evidence,license,measurement,safety,status,test | bytes=3396
docs/REPOSITORIES.md | labels=bom,build,design,evidence,measurement,safety,status,test | bytes=4565
docs/research/argf-durability.md | labels=design,evidence,measurement,readme,status,test | bytes=2084
docs/research/cardboard-membrane.md | labels=design,evidence,measurement,readme,status,test | bytes=2092
docs/research/cascade-heatbalance.md | labels=design,evidence,measurement,readme,status,test | bytes=2086
docs/research/cloud9-relay.md | labels=design,evidence,measurement,readme,status,test | bytes=2114
docs/research/dish-mesh-reflector.md | labels=design,evidence,measurement,readme,status,test | bytes=2084
docs/research/double-skin-catenary.md | labels=design,evidence,measurement,readme,status,test | bytes=2120
docs/research/labyrinth-cooling.md | labels=design,evidence,measurement,readme,status,test | bytes=2096
docs/research/opencell-absorber.md | labels=design,evidence,measurement,readme,status,test | bytes=2098
docs/research/thixo-foam.md | labels=design,evidence,measurement,readme,status,test | bytes=2074
docs/SCOPE.md | labels=build,design,evidence,measurement | bytes=1210
docs/SUPERLINEAR.md | labels=build,design,evidence,measurement,status,test | bytes=2832
docs/SUPERLOOP.md | labels=evidence,license,measurement,safety,status,test | bytes=3177
docs/SYSTEM_ACTION_PLAN.md | labels=build,design,measurement,readme,test | bytes=4123
docs/UNIFIED_ARCHITECTURE.md | labels=build,design,license,status | bytes=1664
README.md | labels=build,design,evidence,license,measurement,readme,safety,status,test | bytes=8365
```
