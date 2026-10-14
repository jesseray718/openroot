# OPENROOT INTERACTION ACCESS V1

Every new AI interaction receives access to the established Pioneer stack:

1. GitHub documentation pod.
2. Local Qwen2.5-Coder 7B inference stack.
3. Full Pioneer retrieval and routing stack.
4. Jesse's GitHub scan and intake estate.
5. Newton-chain ledger and provenance records.

## Binding access contract

```text
interaction
  -> GitHub-docs pod
  -> 7B coder
  -> Pioneer stack
  -> GitHub scan / intake estate
  -> Newton ledger
  -> unified evidence database
```

## Established assets

| Asset | Path or identity | Access |
|---|---|---|
| GitHub-docs pod | `/home/jesse/pods/github-docs/pod.db` | Read-only retrieval |
| Pod seal | `a9689710e727bd1c72911aeba231be78` | Verified corpus identity |
| 7B coder | `qwen2.5-coder:7b` via Ollama `:11434` | Bounded grounded synthesis |
| Phi-4 router | Existing Pioneer routing front door | Route classification and dispatch |
| GitHub intake manifest | `/home/jesse/recovery-evidence/github-intake-final-ZbSItoBZ/` | Read-only source inventory |
| Filesystem census | `/home/jesse/openroot/data/device_ledgers/optiplex_fs_ledger.db` | Read-only 768,255-file identity layer |
| Newton chain | `/home/jesse/openroot/ledger/newton_chain.jsonl` | Append-only provenance, human-gated |
| Ultimate plan | `/home/jesse/openroot/docs/OPENROOT_ULTIMATE_PLAN_DRAFT_V1.md` | Read-only architecture contract |

## Interaction protocol

Every interaction begins with:

```text
1. Read the window seed.
2. Identify the active task and required pods.
3. Check exact SHA-256 / cache reuse first.
4. Retrieve BM25 and Nomic evidence.
5. Assign the correct specialist runner.
6. Execute only the bounded approved action.
7. Return an answer with exact SHA-256 citations.
8. Write an interaction receipt.
9. Human approves any canonical commit, adoption, or irreversible action.
```

## Specialist boundaries

Each runner has read-only access to the whole evidence estate but writes only inside its own specialty:

| Runner | Specialty | Write boundary |
|---|---|---|
| Database reader | Query SQLite, schema, metadata, provenance | Read-only |
| Ledger auditor | Verify chains, seals, receipts, lineage | Read-only audit receipt |
| Document retriever | FTS5/BM25 + Nomic evidence packets | Read-only retrieval receipt |
| Code specialist | Read, analyze, propose, and test code | Sandbox or explicitly approved path |
| Router | Classify task and choose route/model | Router state only |
| 7B coder | Synthesize grounded answers and code | Explicit task receipt |
| Census runner | Hash and inventory one explicit root | Its own manifest and receipt |
| Thermodynamic accountant | Measure or estimate energy/resource cost | Energy receipt only |
| REPL logger | Preserve interaction evidence | Append-only interaction ledger |

## Pioneer stack contract

```text
human command
  -> router classifies task
  -> cache / SHA-256 reuse check
  -> BM25 + Nomic retrieval
  -> specialist runner receives evidence packet
  -> 7B coder synthesizes only when required
  -> answer returns SHA-256 citations
  -> interaction receipt enters evidence database
  -> human approves canonical adoption
```

## Non-negotiables

- Every interaction receives the GitHub-docs pod, 7B coder, Pioneer stack, GitHub scan, and ledger context.
- Every runner has read-only access to the whole corpus.
- No runner may write outside its specialty boundary.
- No model may answer outside supplied evidence without returning `NOT IN EVIDENCE`.
- No embedding score is proof.
- No source ledger is overwritten or deleted during reconciliation.
- No canonical adoption occurs without human confirmation.
