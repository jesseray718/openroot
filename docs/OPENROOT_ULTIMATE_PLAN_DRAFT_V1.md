# OPENROOT ULTIMATE PLAN V1

## North star

Build an open-source knowledge organism: a federated commons of local-first, provenance-bearing knowledge pods.

OpenRoot turns scattered files, code, manuals, laws, logs, projects, and operational experience into SHA-256-addressed evidence that can be searched, cited, corrected, reused, and shared without surrendering control to a centralized service.

Its purpose is to increase maximum computable systemic benefit while routing capability and benefit toward the least-served nodes.

## One universal pattern

Every knowledge domain uses the same self-similar pod contract:

```text
source artifact
  -> SHA-256 content identity
  -> metadata: path, URI, mtime, size, license, capture time, revision
  -> semantic chunks
  -> chunk SHA-256 identities
  -> FTS5 lexical index
  -> Nomic vector embeddings
  -> hybrid retrieval
  -> grounded local-model answer
  -> cited query receipt
  -> human correction
  -> verified reusable pathway
```

The same pattern can ingest:

- Your own files, projects, notes, ledgers, and terminal history.
- GitHub repositories, documentation, issues, releases, and history.
- GitHub official documentation.
- Linux, Ubuntu, and OptiPlex documentation.
- Automotive repair manuals by make, model, and year.
- Municipal, state, and federal law.
- Supreme Court decisions and subject-specific legal research.
- Open-source hardware and appropriate-technology knowledge.
- Local community knowledge and permaculture practice.
- The AI system's own terminal logs, mistakes, diagnoses, and verified fixes.

## The four separations

Never collapse these layers:

| Layer | Question | Rule |
|---|---|---|
| Evidence | What exact bytes exist? | SHA-256 proves identity, not truth |
| Retrieval | What is most relevant? | FTS5/vector score is relevance, not proof |
| Reasoning | What answer follows from evidence? | Local model synthesizes only supplied evidence |
| Verification | What was tested, corrected, or confirmed? | Only verified outcomes promote pathways |

A SHA-256 proves identity. FTS5 proves lexical match. Nomic measures similarity. A local 7B model synthesizes. Only a verified correction or outcome promotes a result into a reusable pathway.

## Unified evidence database

Build one unified SQLite evidence substrate from the partial ledgers:

```text
sources
  sha256 PRIMARY KEY
  path
  source_uri
  source_class
  mtime_epoch
  size_bytes
  captured_at
  license
  revision

records
  record_sha256 PRIMARY KEY
  source_sha256
  record_type
  timestamp
  canonical_json

records_fts
  FTS5 searchable record text

embeddings
  record_sha256
  model
  dimensions
  vector
  embedded_at

queries
  question
  matched_record_sha256
  score
  answer
  citations
  receipt

corrections
  query_id
  verdict
  missed_evidence
  correction
  verified_outcome

pathways
  pathway_sha256
  input_conditions
  procedure
  evidence_hashes
  verification_status
```

The current 768,255-file census is the first major source:

- 768,255 distinct files SHA-256 hashed
- 2,736,595 scanned rows
- source database: `/home/jesse/openroot/data/device_ledgers/optiplex_fs_ledger.db`
- unified evidence database: import `files` rows by `sha256` and `path`
- preserve `mtime`, file size, source path, source database, and source row ID
- build FTS5 over paths and later selected text
- add Nomic embeddings only after the hash/metadata layer is stable

## Existing sealed assets

Do not rebuild or discard these:

| Asset | Status | Role |
|---|---|---|
| GitHub-docs pod | Sealed and operational | 3,748 docs, 26,430 chunks, 26,372 Nomic embeddings, FTS5 + vector retrieval |
| Pod seal | `a9689710e727bd1c72911aeba231be78` | Identity of sealed GitHub-docs corpus |
| Filesystem census | Complete | 768,255 distinct files hashed |
| Unified intake manifest | Complete | 391 unique GitHub-intake records |
| Newton chain | Active | Append-only provenance and telemetry |
| Query harness | v1.1 live | Hybrid retrieval + grounded local synthesis |
| Correction ledger | Active | Human-labeled good/partial/bad answers |
| CODEOWNERS | Ratified | Review gate for external PRs |

## Development order

### Phase 1 — Unified evidence core

1. Finish importing the 768,255-file census into `unified_evidence.db`.
2. Verify SHA-256 uniqueness, path/mtime metadata, SQLite integrity, and FTS5 search.
3. Register Newton, ACRE, GitHub-intake, terminal, pathway, and knowledge ledgers as sources.
4. Map each source schema without rewriting or deleting source ledgers.
5. Import only schema-mapped records into the unified evidence database.

### Phase 2 — Retrieval organ

1. Create FTS5 indexes over selected text fields.
2. Add Nomic embeddings in bounded batches.
3. Build hybrid retrieval: exact hash, FTS5, vector similarity.
4. Add evidence-sufficiency gating before model synthesis.
5. Return `NOT IN EVIDENCE` when evidence is insufficient.

### Phase 3 — Learning organ

1. Preserve every terminal command, error, diagnosis, correction, and verified outcome.
2. Classify mistakes into a small stable taxonomy.
3. Turn each correction into an evaluation case.
4. Promote only verified reusable pathways.
5. Measure reuse: fewer repeated errors, fewer model calls, less human rediscovery.

### Phase 4 — Federated pods

1. Keep the GitHub-docs pod as Pod #1.
2. Build the OpenRoot self-corpus pod as Pod #2.
3. Add Ubuntu/Linux and OptiPlex documentation pods.
4. Add GitHub repository/history pods by source class.
5. Add legal, automotive, municipal, and community pods only after the pod contract is stable.
6. Let pods remain sovereign while sharing hashes, citations, and optional public mirrors.

## Routing doctrine

Route work in this order:

```text
L0: exact SHA-256 / exact query reuse
L1: FTS5 lexical retrieval
L2: Nomic vector similarity
L3: local 7B grounded synthesis
L4: external research or human investigation
```

The goal is not to eliminate models. The goal is to make repeated work cheaper:

- Same question -> L0.
- Similar question, known evidence -> L1/L2.
- New question over known corpus -> L3 with citations.
- Unknown question -> L4, then seal what was learned.

## Human gates

The human remains the only gate for:

- Canonical schema adoption.
- Git commits and pushes.
- Merges to main/master.
- ACRE minting or issuance claims.
- Newton-chain canonical adoption.
- Public release of private material.
- Replacement of a verified core.
- Claims promoted from candidate to theorem.

## Immediate queue

1. Verify the 768k unified-evidence import completes with integrity GREEN.
2. Inspect its schema, row count, FTS count, and sample records.
3. Ratify `POD_SCHEMA_V1.md`.
4. Build the OpenRoot self-corpus pod from a small explicit allowlist.
5. Add Nomic embeddings only after hash/metadata/FTS layers verify.
6. Add correction-ledger evaluation cases.
7. Merge additional partial ledgers only through schema-preserving, append-only imports.

## Non-negotiables

- Never treat an embedding score as proof.
- Never let a high aggregate score conceal harm at the lowest-served nodes.
- Never overwrite or delete a source ledger during a merge.
- Never automatically promote a claim to theorem status.
- Never let a model answer outside supplied evidence without saying so.
- Never bulk-commit unrelated work.
- Never lose a receipt: every operation writes an inspectable artifact.
