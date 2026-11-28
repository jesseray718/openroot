# Evidence-backed answer loop: proposed contract

This is a proposal for a disposable reference implementation, not a claim
that the installed pipeline meets this contract. It does not authorize
modification of existing pods, ledgers, seals, or production services.
Payloads and private operational records must stay out of Git.

## Evidence and status

**CLAIMED:** The source and status document describe the following work.
The classifications describe the reviewed repository, not every local copy.
**OPERATOR-REPORTED:** Local runs and receipts may contain newer work, but
have not been independently reproduced here.

| Stage | Status | Boundary |
|---|---|---|
| Ingestion and provenance | PARTIAL | The cell schema exists; complete source provenance and lifecycle rules are not established. |
| Pod verification | PARTIAL | The existing schema verifier checks ledger blocks, not all file cells. |
| Retrieval | PARTIAL | The pinned query pipeline does bounded per-word retrieval. |
| Selection and excerpts | PARTIAL | It ranks candidates and uses leading excerpts; complete budgeted, coverage-aware selection is not established. |
| Prompt | PARTIAL | The pipeline builds a prompt; a versioned, reproducible contract is not established. |
| Generation and accounting | PARTIAL | A local generation route exists; model correctness and meter boundaries need independent evidence. |
| Pathway recording | PARTIAL | The existing route appends hash-linked records, but append does not first validate the entire chain. |
| Chain verification | PARTIAL | Implementations support particular serializations; compatibility cannot be assumed for every local chain. |
| Corrections | PARTIAL | The pinned helper supports exact-pathway BLOCKs, not the proposed cell-supersession contract. |
| Replay | PARTIAL | Existing replay validates recorded evidence and holds on failure; it is not automatic regeneration. |
| Reproduction and CI | PARTIAL | Existing CI checks repository tests and tracked chains; it does not establish this proposed end-to-end loop. |

The current source identities and evidence boundaries are documented in
[the implementation status](STATUS-2026-11-23.md). Those pinned files are
not to be edited for this proposal.

## Reference boundary

Use synthetic, disposable fixtures and a stub model. No real model request,
network service, production ledger, local pod, or payload is needed. This is
not an installed CLI, a migration, or a recommendation to run against live
data. It must surface errors instead of silently treating malformed state as
an empty chain or successful replay.

1. Open a supplied SQLite pod with `mode=ro` and `query_only`, check the
   expected cell and FTS schema before querying, and compare pod hashes
   before and after the operation. Refuse a schema mismatch or a changed pod.
   The test fixture must also demonstrate that writes are rejected. A main
   database file hash alone does not capture outstanding WAL state: use
   quiescent, checkpointed fixtures and do not claim live snapshot safety.
2. Tokenize the question deterministically, quote the tokens for one FTS5
   OR query, and order bounded candidates by BM25 and cell ID. Reject invalid
   inputs explicitly. Select a deterministic evidence packet under a stated
   budget using relevance, question-term coverage, redundancy, and per-file
   limits. Extract relevant snippets rather than assuming a leading excerpt
   contains the answer; apply a documented redaction policy before prompting.
   These heuristics do not prove answer quality or exhaustiveness.
3. Construct a deterministic, versioned prompt from the question and packet.
   The stub records how many generation requests it receives; a fresh answer
   records the actual stub request, not an inferred request count.
4. Record a versioned JSONL pathway with the question, selected cell IDs and
   body hashes, prompt and answer hashes, answer, model, route, timing, tokens,
   separately identified measured and estimated energy, previous link, and
   hash. Define the canonical JSON bytes and digest algorithm explicitly.
   Unknown measurements remain absent or null, never converted into measured
   values. Hashes provide integrity relative to a trusted tip, not authorship.
5. Validate every chain row and link before replay or append. Support only
   explicitly specified legacy serialization recipes and report which recipe
   matched; never silently skip malformed rows or guess a hash algorithm from
   digest length. An independently trusted external tip is necessary to
   detect removal of a valid tail. Without one, say so.
6. Validate exact question identity, answer and prompt hashes, route and
   evidence bodies, and correction state before replay. A BLOCK or a
   superseded cell invalidates affected pathways. An optional retrieval-drift
   check may warn without independently refusing replay. A valid replay
   returns the saved answer with **zero** model requests.
7. An ordinary miss or invalidated pathway may lead to fresh retrieval and
   generation only after all required input and chain checks succeed.
   Corrupt, ambiguous, or unverifiable chains must hold: never append to a
   chain that failed validation. Writers and correction authority need an
   explicit concurrency/trust design before any production integration.

The historical field named `blake3` and the `b3` helper use BLAKE2b-256 in
the reviewed schema: 32 bytes, represented by 64 hexadecimal characters.
Do not rename the algorithm or change historical identities. Python's
standard library does not supply native BLAKE3; an additive migration would
need a separately reviewed dependency and compatibility plan.

## Acceptance evidence

Focused synthetic tests should cover deterministic retrieval, budget and
prompt, non-leading evidence and redaction, read-only and unchanged pods,
schema mismatch, generation count and zero-request replay, changed or missing
cells, BLOCK and supersession, corrupted and truncated chains with a trusted
tip, supported legacy recipes, and a warning-only drift check. Tests must
demonstrate no append on corrupt chains. A passing fixture is evidence for
the reference behavior only, not for answer accuracy, physical performance,
security of a live deployment, or the state of an operator's local system.

Review the specification, implementation, and CI as separate proposals.
The CI proposal depends on the reference files landing first; no proposal
should merge itself or change the real ledger.
