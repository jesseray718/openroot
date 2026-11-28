# Disposable answer-loop reference

This is an experimental, synthetic-fixture reference, not a production
pipeline, migration tool, or validator for every historic ledger. Run its
focused tests from the repository root:

```sh
python3 -m unittest discover -s tests -p test_answer_loop_reference.py
```

The tests create disposable SQLite pods and chains. No real model, network,
local pod, or operational ledger is needed. The API requires existing files
and assumes a single operator and quiescent, checkpointed inputs; it has no
locking, atomic multi-file snapshots, authentication, durable-write protocol,
or concurrency protection. Do not point it at real data. Questions and
answers are stored in the synthetic chain. The illustrative redaction of
simple `token=`, `api_key=`, and `password=` patterns is not a security or
privacy boundary.

FTS candidates are bounded at 100, ordered by BM25 and cell ID, and greedily
selected by new query-term coverage, rank, and ID, with a character budget,
per-source limit, and duplicate-snippet suppression. This does not establish
exhaustive retrieval or answer quality. Prompt snippets use a 300-character
window near the first matching term; hashes cover full evidence bodies.

Version `answer-loop/1` hashes compact, sorted, ASCII-escaped JSON with
SHA-256, excluding the `hash` field. A `prev` link chains the records.
For unversioned query-style legacy rows, verification accepts BLAKE2b-256
over sorted ASCII JSON with either default or compact separators, excluding
`ph`; it reports the matched recipe. A valid legacy chain row is not
automatically eligible for replay. Other legacy formats are not supported.
Native BLAKE3 is not provided by Python's standard library. Historical
`b3`/`blake3` identifiers are not rewritten.

The optional expected tip must come from an independently trusted source.
Without it, verification cannot detect removal of a valid tail; neither a
chain nor an expected tip proves authorship. Corrections are synthetic,
separately hash-chained `BLOCK` (pathway hash) or `SUPERSEDE` (cell ID)
records; their authority and completeness must be established externally.
Drift checking warns without rejecting an otherwise valid replay.

The sample model only counts calls and returns a stub answer. Token and
energy values are null, not measurements. Successful tests do not establish
correctness of a real model answer, live meter readings, or production safety.
