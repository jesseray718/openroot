# Operations

## Promotion loop

1. Capture locally.
2. Hash into host-local SQLite manifests.
3. Generate report-only duplicate candidates.
4. Index approved local material.
5. Retrieve through FTS5 and semantic embeddings.
6. Route to a bounded candidate solution.
7. Validate using deterministic checks.
8. Record evidence in a Newton Chain receipt.
9. Human reviews the staged diff before promotion.

## Hard stops

- Never bulk-delete from duplicate reports.
- Never use `git add .` during recovery.
- Never commit credentials, private documents, live databases, logs, models,
  archives, Android exports, runtime state, or local reports.
