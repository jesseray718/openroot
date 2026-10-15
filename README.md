# OpenRoot

OpenRoot is a local-first knowledge and appropriate-technology system.

It turns source material into SHA-256-addressed, searchable, citation-capable knowledge pods. Each pod preserves provenance, supports hybrid lexical and semantic retrieval, records query receipts, and learns from human-labeled corrections.

## Pod Era v1

The first operational knowledge pod is live:

- **GitHub documentation pod**: 3,748 documents, 26,430 chunks, and 26,372 Nomic embeddings.
- **Hybrid retrieval**: SQLite FTS5 lexical search fused with vector similarity.
- **Grounded local synthesis**: a local Qwen2.5-Coder 7B model answers only from retrieved evidence and cites sources.
- **Query receipts**: every question stores its evidence chunk IDs, model, answer, token count, and elapsed time.
- **Correction ledger**: human verdicts distinguish good, partial, and bad answers.
- **Merkle-sealed corpus**: pod seal `a9689710e727bd1c72911aeba231be78`.
- **Machine census**: 768,255 distinct files SHA-256 hashed across the primary OpenRoot node.

## How it works

```text
source document
  -> SHA-256 content identity
  -> semantic chunks
  -> FTS5 lexical index
  -> Nomic vector embeddings
  -> hybrid retrieval
  -> grounded local-model synthesis
  -> cited answer
  -> query receipt
  -> human correction
  -> improved retrieval pathway
```

OpenRoot separates four concerns:

| Layer | Purpose |
|---|---|
| Evidence | Exact source identity through SHA-256 |
| Retrieval | FTS5 and vector similarity |
| Reasoning | Local model synthesis from supplied evidence |
| Verification | Human correction, evaluation, and reusable pathways |

A hash proves what source bytes existed. Retrieval identifies relevant evidence. A model synthesizes an answer. Only a verified correction or outcome promotes a result into a reusable pathway.

## A/B test: do the GitHub how-to docs help?

`bin/ab_test_github_docs_v1.py` runs the same questions, model, prompt template, seed, and `temperature=0` under two conditions and logs both configurations:

- `A_with_docs`: retrieval over every supplied pod, including the GitHub docs pod.
- `B_without_docs`: retrieval over the same pods minus the GitHub docs pod.
- `C_no_retrieval` (optional, `--include-baseline`): no evidence at all.

```bash
bin/pod ab \
  --pod github-docs=pods/github-docs/github_docs.sqlite3 \
  --pod self-corpus=/path/to/other/pod.db \
  --question "How do I create a branch protection rule?" \
  --include-baseline
# or: --questions-file q.jsonl  (lines of {"question": "...", "expected_terms": ["..."]})
# --no-generate gives retrieval-only signals without calling Ollama
```

What it measures (identical scoring for every condition): evidence hits and how many come from the docs pod, `evidence_term_coverage` (share of question terms found in retrieved evidence), `valid_citation_rate` (answer citations that match retrieved chunk tags), optional `expected_term_recall`, and a `composite` mean of these. `delta_composite_A_minus_B` is the comparative metric.

Reading the output: a JSON report is written to `runs/ab/` with per-condition evidence provenance (pod, chunk id, chunk SHA-256), prompt and answer SHA-256, pod file SHA-256 before and after, and a summary of wins/ties plus the mean delta. A positive mean delta across many questions suggests the docs help; with few questions treat it as anecdotal, and have a human label answers in the correction ledger. Retrieval is lexical FTS5 (bm25 scores are not strictly comparable across pods), so the result measures evidence and grounding signals, not semantic recall.

Safety: pods are opened `mode=ro` with `query_only`, hashed before and after (the run fails if a pod changed), and the output directory may not sit inside a pod directory. The GitHub docs pod is a sealed source corpus and is never written. Use `bin/pod check` and `bin/pod push "msg"` as usual; both compile this script.

## Current status

- Pod #1: GitHub documentation corpus is sealed and queryable.
- Query harness v1.1: hybrid retrieval and cited local-model answers are live.
- Correction ledger: active for human-labeled evaluation.
- Known limitation: retrieval recall is still experimental; a hierarchy-oriented GitHub Actions query missed its best evidence and was labeled `partial`.
- Next milestone: OpenRoot self-corpus dogfood pod, retrieval metadata, evidence-sufficiency gating, and correction-driven evaluation.

## Repository structure

- `bin/`: operational scripts and tools.
- `data/`: local runtime state, indexes, and non-canonical operational artifacts.
- `ledger/`: append-only Newton-chain and provenance records.
- `context_bridge/`: cross-window handoff and operational state.
- `canon/`: human-ratified canonical definitions and schemas.
- `docs/`: project documentation.
- `.github/CODEOWNERS`: all paths require review by `@jesseray718`.

## Principles

- Local-first: useful capability should run on hardware you control.
- Provenance-first: every important artifact carries an inspectable identity.
- Cache proven work: a verified pathway should not be recomputed.
- Route benefit toward the least-served nodes.
- Keep humans in control of canonical adoption, commits, releases, and irreversible actions.
- Distinguish evidence, retrieval, reasoning, and verification.

## License

See repository licensing and individual source-file headers for applicable terms.
