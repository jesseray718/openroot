# OpenLoom Coder Workspace

This is the single operating environment for the OpenLoom coder.

## Access policy

- The coder operates from this workspace.
- It may read all linked pods, databases, evidence, ledgers, and recovery areas.
- It must treat every SQLite database as read-only unless a user explicitly requests a write.
- It must never delete, overwrite, migrate, or schema-change a source database.
- It must not autonomously push, force-push, merge, publish, or contact GitHub.
- It must cite source database, source path, file SHA-256, and chunk provenance when answering from retrieved evidence.

## Canonical locations

- Workspace: ~/openloom-build/workspace
- Pods: ~/openloom-build/workspace/pods
- Unified RAG corpus: ~/openloom-build/grand-unification/unified_rag.sqlite3
- Staging: ~/openloom-build/grand-unification/staging
- Inventory: ~/openloom-build/grand-unification/manifests/grand-unification-inventory.json
- Model-access catalog: ~/openloom-build/pods/model-access/model_access_catalog.json

## Pod roles

- github-docs: authoritative GitHub product/workflow documentation.
- openroot-knowledge: OpenRoot sessions, wikis, code, and operational history.
- tiny-model-training: training and evaluation corpus.
- a15-mobile: A15 device corpus and shared ledger.
- github-history: GitHub historical evidence.
- self-corpus: personal/project self-corpus.
- recovery: recovery and forensic evidence snapshots.
- ledger: unified and specialized ledgers.
