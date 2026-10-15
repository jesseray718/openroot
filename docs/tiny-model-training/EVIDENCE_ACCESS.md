# Database Access for Models

Models must receive evidence through retrieval, not through direct database
writes.

## Allowed access

- Read SQLite evidence databases.
- Query FTS5 indexes.
- Receive retrieved excerpts in the prompt.
- Read SHA-256 manifests and receipts.

## Restricted access

- No direct writes to canonical evidence databases.
- No deletion of evidence.
- No modification of source records.
- No synchronization of live SQLite, WAL, or SHM files.
- No autonomous GitHub publication.

## Retrieval contract

For each user question:

1. Convert the question to a safe FTS query.
2. Retrieve the top matching evidence excerpts.
3. Include table ID, page, excerpt, and hashes.
4. Tell the model to use only supplied evidence.
5. Record which evidence was used in the evaluation report.
