# Task: OpenLoom UI Interface Upgrade v1

Build a minimal local web UI for the existing OpenLoom CLI and evidence databases.

## Hard boundaries

- Local-only by default; bind to 127.0.0.1 unless explicitly configured otherwise.
- Read-only UI in v1: no commit, push, PR, deletion, model invocation, or network retrieval from the UI.
- Use the existing OpenLoom CLI and SQLite pod schema; do not duplicate ingestion logic.
- Do not modify the canonical evidence schema without a separate reviewed task.
- Keep dependencies minimal; prefer Python standard library plus existing project dependencies.

## Required v1 views

1. Dashboard
   - Show OpenLoom verify status.
   - Show pod counts: sources, chunks, embeddings, FTS rows.
   - Show SQLite integrity status.

2. Manual evidence browser
   - Load `evidence/lubuntu-manual/lubuntu_manual_tables.sqlite3`.
   - List manual tables with PDF page, row count, column count, CSV SHA-256, and JSONL SHA-256.
   - Allow selecting a table and viewing its rows.
   - Provide FTS search across `manual_tables_fts`.

3. Provenance panel
   - Display source manifest path and manifest SHA-256.
   - Display per-table CSV and JSONL hashes.
   - Make every displayed table row traceable to its `table_id` and `row_sha256`.

## Deliverables

- `openloom/ui/__init__.py`
- `openloom/ui/app.py`
- `openloom/ui/templates/`
- `openloom/ui/static/`
- A CLI entry point: `python3 -m openloom.ui.app --db evidence/lubuntu-manual/lubuntu_manual_tables.sqlite3`
- Tests for database loading, FTS search, and route responses.
- Update `README.md` with local UI startup instructions.

## Acceptance gate

- `python3 -m py_compile $(find openloom -name '*.py')`
- Existing tests pass.
- New UI tests pass.
- `python3 -m openloom.cli verify --pod demo-pod` returns `"passed": true`.
- UI starts locally and displays the manual evidence database.
- No secrets, API keys, database credentials, or absolute personal paths are committed.

Stop after implementing and testing this bounded v1. Do not commit, push, or open a PR.
