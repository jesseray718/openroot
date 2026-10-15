# OpenLoom MVP

OpenLoom is a minimal, local-first CLI for creating portable,
provenance-bearing SQLite knowledge pods.

## Commands

```bash
python3 -m openloom.cli init --pod my-pod
python3 -m openloom.cli ingest --pod my-pod --source ./notes
python3 -m openloom.cli verify --pod my-pod
```

## Supported inputs

- SQLite databases
- CSV files
- JSONL files
- Markdown files
- Plain-text files
- Directories containing those files

## Invariants

- Every source has a SHA-256 identity.
- Every chunk links to a source.
- Every embedding links to a chunk.
- Every query produces a receipt.
- No reusable pathway is promoted without verification.

## Model boundary

OpenLoom uses a pluggable model-runtime interface.
Local execution is the default.
Remote execution is disabled unless explicitly enabled.

## Status

MVP scope:

- SQLite, CSV/JSONL, Markdown, and text ingestion
- SHA-256 provenance
- FTS5 retrieval
- Pod manifest and verification
- Optional model adapters

Not yet implemented:

- PDF, OCR, web crawling, and proprietary database adapters
- Automatic remote ingestion
- Automatic commits, pushes, releases, or PR merges
