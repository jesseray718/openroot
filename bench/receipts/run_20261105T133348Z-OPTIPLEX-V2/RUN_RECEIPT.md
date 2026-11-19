# PODBENCH-100 v2 RUN RECEIPT (FTS5-grounded, model ladder)
- run_id: 20261105T133348Z-OPTIPLEX-V2
- node: OPTIPLEX | commit: 8300701
- grounding: real FTS5 lattice (BM25, 400-char chunks, survey+spec corpus) — runtime state at bench/state/
- ladder: qwen2.5-coder:0.5b draft -> qwen2.5:3b refine -> qwen2.5:7b adjudicate
- final_accuracy: 0/100 | draft_only_accuracy: 90/100
- ladder_delta: -90 questions improved by bigger models
- runtime_errors: 100
- cache_chain_final_sha256: f1c637dd355968db3a11863aec45c862fdf210766f5346db336f4bf61e6ce756
- classification: DERIVED grading / ATTESTED chain — unrefined system benchmark
- status: UNREFINED_BASELINE
- exit_code: 1
584c83beadcbd25200a95d0e72e751b78d23b88f551a43a48d59810e2acf615b  bench/receipts/run_20261105T133348Z-OPTIPLEX-V2/RUN_RECEIPT.md
