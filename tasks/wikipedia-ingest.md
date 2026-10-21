TASK: Add a read-only Wikipedia ingestion command to OpenLoom.

Requirements:
- Add: openloom ingest-wikipedia --pod demo-pod --title "HTTP Strict Transport Security"
- Fetch through the existing provenance-first adapter.
- Save the article text and receipt.
- Create source, record, and chunk rows.
- Do not create embeddings automatically.
- Do not commit, push, or create a PR.
- Print a receipt and run openloom verify.
