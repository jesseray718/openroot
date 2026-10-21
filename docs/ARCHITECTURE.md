# OpenRoot Architecture

```text
capture -> SHA-256 inventory -> duplicate report
        -> SQLite FTS5 + Nomic embeddings
        -> routing -> validation -> Newton Chain receipt
        -> human review -> GitHub
```

- A15/Termux is a mobile capture and control node.
- OptiPlex is the durable local compute, indexing, and archive node.
- SQLite manifests and FTS5 support local lexical retrieval.
- Nomic embeddings support local semantic retrieval.
- Routing generates bounded candidate pathways.
- Newton Chain records evidence, assumptions, validation, and outcomes.
- Human review is required before GitHub promotion.
