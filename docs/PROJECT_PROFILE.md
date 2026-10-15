<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# OpenRoot / OpenLoom Project Profile

OpenRoot is a local-first, provenance-first knowledge system. OpenLoom turns sources into SHA-256-addressed pods (SQLite: `sources`, `records`, `chunks`, `chunks_fts`, `embeddings`, `queries`, `corrections`, `pathways`). Everything runs offline against Ollama on localhost.

## Where the GitHub how-to docs corpus fits

The GitHub documentation pod (`pods/github-docs/github_docs.sqlite3`) is a sealed, public, read-only source corpus. It supplies evidence for GitHub workflow questions (branches, PRs, Actions, releases). It is queried by the grounded-answer harness and may be merged into the unified RAG store, but is never modified by evaluation tooling.

## Scientific comparison: with vs. without the docs pod

Run `bin/pod ab --pod github-docs=<db> --pod <other>=<db> --question "..." [--include-baseline]` (see README, "A/B test").

- Controlled: same questions, model (`qwen2.5-coder:7b` by default), prompt template, seed, `temperature=0`, scoring.
- Varied: only the pod set (A with docs, B without docs, optional C no retrieval).
- Measured: docs-pod hits, evidence term coverage, citation validity, optional expected-term recall, composite, and `delta_composite_A_minus_B`.
- Provenance: pod/chunk id/chunk SHA-256 per evidence item, prompt and answer hashes, pod file hashes before/after, in `runs/ab/*.json`.
- Interpretation: positive mean delta over many questions supports a benefit; verdicts remain human (correction ledger). Small samples and lexical-only retrieval limit conclusions.
- Safety: read-only pod access, no mutation of sealed corpora, output kept outside pod directories. Commit and push remain human-gated through `bin/pod check` and `bin/pod push`.
