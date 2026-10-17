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

## Current status

- Pod #1: GitHub documentation corpus is sealed and queryable.
- Query harness v1.1: hybrid retrieval and cited local-model answers are live.
- Correction ledger: active for human-labeled evaluation.
- Known limitation: retrieval recall is still experimental; a hierarchy-oriented GitHub Actions query missed its best evidence and was labeled `partial`.
- Unified evidence milestone: the canonical database contains 768,257 source rows, passes SQLite `integrity_check`, and has a populated FTS index.
- Local RAG milestone: five approved OpenRoot documents produced 14 chunks and 14 Nomic embeddings at 768 dimensions. A core-objectives test query ranked the goals chunk first (cosine similarity 0.7222).
- Vector inventory milestone: a read-only utility inventories likely embedding databases, checks schema and provenance mappings, and recommends compatibility without merging or modifying any database.
- Next milestone: run and review the inventory on the OpenRoot node. Decide on any future merge only after verifying vector identity, chunk text, and source provenance; then continue evidence-sufficiency and correction-driven retrieval evaluation.

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
