# Existing cell fast path: AeroCement retrieval-only probe

Date: 2026-11-22. Evidence: operator-provided terminal output and publication-review JSON from the OptiPlex, controlled from an A15. This report documents an existing implementation; it does not activate it or certify the complete system. Source preservation and README updates are separate publication steps and are not established by this report alone.

## Observed run

Question: `What is AeroCement?` The existing stopword logic retained `aerocement`.

| Stage | Seconds |
|---|---:|
| Keyword retrieval | 1.1420193089870736 |
| Ranking / selection | 0.0007234379881992936 |
| Context capture and source-body hashing | 0.40383031201781705 |
| Retrieval through context | 1.54657305899309 |

The run retained 40 distinct cells, selected eight, and assembled a 2,524-byte prompt. Model requests: zero. Production pathway appends: zero. No generated answer or physical performance was evaluated. One local observation is not a cold-start benchmark, latency distribution, independent replication, or speedup comparison.

## Actual mechanism

The inspected local `bin/query_pipeline.py` performs per-word FTS retrieval through `cell_schema`, combines the retained incidences, selects eight cell IDs, captures full-body hashes, and builds a model context from each selected body's first 300 characters. Its `ask` branch then generates and appends a pathway. The diagnostic invoked only existing retrieval, ranking, and context functions, replacing the database opener with a read-only connection; it did not run `ask`, the normal initialization DDL, generation, or sealing.

The database is a unified cell store, not the 24 standalone pod databases tested earlier. The earlier recovered pod engine failed on all 24 pods because its expected schema did not match; that failure is not evidence of absent AeroCement material.

## Candidate and selection audit

| Kind | Retained candidates | Selected |
|---|---:|---:|
| file_cell | 22 | 3 |
| git_commit | 8 | 0 |
| learned_cell | 5 | 1 |
| pathway | 5 | 4 |
| Total | 40 | 8 |

A later operator-side audit reported that all eight selected full-body hashes and byte counts still matched the saved evidence snapshot. This check establishes body continuity at that audit, not truth, completeness, or source authority. The uploaded review includes the aggregate audit, not the private candidate bodies or database.

## Limits exposed by this run

- At most 400 fetched rows and 40 distinct retained cells per question word; no claim of total recall.
- For this one-word probe every retained cell received the same ranking contribution, 1/41. Selection preserved incoming FTS order among ties; it added no source-authority preference.
- Four selected cells were stored pathways and one was learned text containing a previous answer. These are not independent corroboration of physical claims.
- Model context contains leading 300-character fragments, not complete bodies or match-centered excerpts. It may omit the relevant passage or end inside JSON.
- The prompt does not carry the diagnostic's cell IDs, kinds, and source references alongside the excerpts.
- Source-body hashes do not certify original-file freshness or answer quality. Those remain separate review obligations.
- No new retrieval, model generation, learning, corpus expansion, correction recording, replay test, energy measurement, or CI run was performed while preparing this report.

## Reviewed local source identities

These are SHA-256 identities of the five files decoded and checked from the operator's uploaded review, not a statement that all five are already published at these paths.

| Local source path | SHA-256 |
|---|---|
| `bin/query_pipeline.py` | `e89715dc4ad3c1b9452e8e1ba180c9b11c7428cb8157143fd3872f502def3f04` |
| `bin/cell_schema.py` | `cf24560024aaffcaad15b6961cc0a90f0cee73a8a79cd2c5fe0b578ae2bec0b9` |
| `bin/query_correction_gate_v1.py` | `692bd1bb5d3c294247aed670563c7a7579b494f9bcfa1f32233cb95e4bc66eb0` |
| `bin/corpus_expand_v1.py` | `bc28b86320c257f6c1a6fb91af9f1daeca03b0cd0ddfbfbe285ff0125f952b54` |
| `bin/chained_inquiry_v1.sh` | `9e96ef5641e9f032fcbd32d900d25759edb6ab4f8ac8cf99c9b4795a3446f706` |

## Execution hazards and review boundary

The reviewed scripts retain absolute paths under a home directory and are not a portable turnkey installation. Do not execute their write-capable modes merely to inspect this report. `cell_schema.open_db()` executes initialization DDL. `ask` and `baseline` require an available Ollama endpoint/model and the configured privileged RAPL helper; `ask` appends a pathway. `expand` and `learn` change the cell corpus. The chained inquiry runs up to ten model calls, learns answers, and appends logs. The correction command appends a correction hold. No database, raw ledger, model, privileged helper, credential, or original corpus is supplied here.

Replay checks exact-question records, recorded source-body identities, and a local correction gate; this retrieval-only probe does not establish that those features passed end-to-end. A correction block in the reviewed code targets an exact cached pathway, not every learned descendant or imported prior answer. Historical names such as `b3` and `blake3` in these files use BLAKE2b in the inspected implementation.

Publication preparation checked all five uploaded source hashes, compiled four Python files without execution, and checked the shell file with `bash -n`. Limited offline credential-pattern checks found no matches; this was not an exhaustive security audit. No CI or deployment outcome was checked.

## Evidence identity and exclusions

- Prompt SHA-256: `90bd7f4fec1609e9a26cb526d1631a1c69bcb8bd78470d01cf773e4cc1d6f696`
- Original local report SHA-256, as reported in the uploaded review: `8d7c5d0eaa9f394cf7632da2bfdc12e126100d987d4155efc61e473778f26d01`

Raw evidence packets, retained excerpts, local database copies, ledger bodies, and the private publication-review JSON are excluded from this public change. Their omission limits independent reproduction of the exact original result. The aggregate observation can be inspected without presenting previous answers as verified material science.
