# OpenRoot README and knowledge-system audit

You are working in an isolated Git worktree:

/home/jesse/openloom-build

Your job is to audit the current OpenRoot repository and produce a
read-only improvement plan. Do not modify, delete, overwrite, commit,
push, or publish anything.

## Context sources

Use these read-only sources:

1. Current OpenRoot repository files in this worktree.
2. GitHub how-to documentation at:
   /home/jesse/pods/github-docs-src/content
3. OpenRoot local documents in:
   /home/jesse/openroot/docs
4. Personal databases and ledgers, but only through read-only SQLite connections:
   - /home/jesse/recovery-evidence/openroot_canonical_v1.db
   - /home/jesse/recovery-evidence/command-ledger/command_ledger.db
   - /home/jesse/openroot/data/embeddings.db
   - /home/jesse/openroot/openroot_vector.db
   - /home/jesse/pods/github-docs-src (documentation corpus)

Do not modify any database, ledger, WAL/SHM file, backup, secret,
credential, model binary, or recovery-evidence artifact.

## Objective

Compare the current README with:

- The actual repository contents
- The organized GitHub documentation corpus
- The OpenRoot canonical architecture
- The local documents
- The command ledger and model-call receipts
- The available logs and recovery evidence

Then recommend a README overhaul that accurately describes what OpenRoot
currently does, what is operational, what is experimental, and what is
not yet implemented.

## Required audit

Produce a report at:

docs/README_AUDIT_V1.md

It must include:

1. Current README assessment
   - What it claims
   - What the repository actually contains
   - What is accurate
   - What is missing
   - What is overstated or unclear

2. Repository inventory
   - Major directories and their purpose
   - Operational assets
   - Experimental assets
   - Deprecated or unclear assets
   - Files that should not be published

3. GitHub-docs alignment
   - Which GitHub documentation patterns OpenRoot already follows
   - Which documentation practices would improve clarity
   - Specific documentation gaps

4. Knowledge-system assessment
   - Canonical database status
   - Sources, records, chunks, embeddings, queries, corrections, pathways
   - Command-ledger and model-call provenance status
   - What is proven operational versus planned

5. Log-ingestion design
   - Which logs exist
   - Which logs are safe to ingest
   - Which logs contain secrets or private material and must be excluded
   - A proposed ingestion schema:
     source artifact -> normalized record -> chunk -> embedding -> query receipt
   - A bounded first ingestion batch using only explicitly approved logs

6. README overhaul proposal
   - A proposed information architecture
   - Section-by-section outline
   - A short, honest project description
   - A clear distinction between operational and experimental features
   - A privacy and local-control statement
   - A contribution and safety boundary statement

## Hard boundaries

- Do not ingest secrets, API keys, passwords, private backups, browser
  data, wallet data, model binaries, WAL/SHM files, or unrelated repos.
- Do not treat embedding similarity, FTS matches, or model output as proof.
- Do not claim that a feature is operational unless there is inspectable
  evidence in the repository or a receipt.
- Do not run git commit, git push, gh pr create, or any network write.
- Do not modify README.md, SECURITY.md, CODEOWNERS, canonical schemas,
  recovery evidence, databases, or runtime scripts.
- Use read-only SQLite connections.
- Use parameterized queries.
- Write only:
  docs/README_AUDIT_V1.md
  docs/LOG_INGESTION_PLAN_V1.md
  AUDIT_SUMMARY.md

## Deliverables

1. docs/README_AUDIT_V1.md
2. docs/LOG_INGESTION_PLAN_V1.md
3. AUDIT_SUMMARY.md

AUDIT_SUMMARY.md must contain:
- Top 10 README problems
- Top 10 documentation improvements
- Top 10 operational claims supported by evidence
- Top 10 claims that need evidence before publication
- Recommended first public README structure
- Recommended first safe log-ingestion batch
- Exact commands you would run to validate the audit
- A clear list of actions requiring human approval

Do not implement the README overhaul yet.
Do not ingest any logs yet.
Do not commit or push.
