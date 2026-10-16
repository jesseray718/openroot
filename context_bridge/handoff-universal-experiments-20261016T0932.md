# Handoff: Universal Pod — Experiment Arc Complete
## Verified State
- Walker: pid 423871, SD leg, resume-safe, launcher: ~/launch_universal_walker_v1.sh (singleton-guarded)
- Live pod: /home/jesse/pods/pod_universal/pod.db — 24548 files, quick_check ok, agape-probe ok
- Lab: /home/jesse/pods/lab_universal/pod.db (pristine, 24548 files)
- Exp clone: /home/jesse/pods/exp_universal_20261016T090321Z/ (throwaway + dossier_audit.md)
- Backups: pod_universal_repaired.db + 20261016T071945Z.db (sealed)

## Measured Results (all on exp clone)
- EXP2 cache: build 128ms avg, cached 0.09ms → 1462x speedup
- EXP3 stress: 'data' 62602 hits in 6.5ms (worst); prefix/phrase sub-ms
- EXP4 hybrid: semantic neighbors found aerocement/thermal content for query with NO shared keywords (cos 0.52-0.57); FTS NEAR(5) returns literal co-occurrences with provenance tables
- VERDICT: hybrid dossier (FTS + cosine top-k) is v2 direction

## Scars (COMPOST candidates)
1. Triple-walker: manual relaunch under fatigue → launcher owns singleton check, not human
2. pgrep -cf false zero → verify with pgrep -af before declaring death
3. SSH-drop mid-paste → tail lines executed on Termux; wrap in single ssh 'bash -s'
4. Raw NL keywords hit FTS5 → sanitize to alphanumerics, phrase-quote
5. Crashed-run residue (4-col dossiers table) → DROP IF EXISTS before CREATE, assert shape
6. NEAR/5 vs NEAR(5) — narrated fix, pasted bug twice; diff prose vs payload
7. Nested quoting kills parens in SQL → heredoc SQL to file, redirect into sqlite3

## Next Actions
1. Wait for SEAL line in walker log → run ~/closeout_universal_v1.sh
2. Grade /home/jesse/pods/exp_universal_20261016T090321Z/dossier_audit.md (human gate)
3. Bench resume at q15 via run_dossier_agent_bench_v1.py against sealed pod
4. v2: hybrid_dossier() = FTS hits + cosine top-k fused into one pack
