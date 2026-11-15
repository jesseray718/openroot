# Recovered targeted dossier compiler v2

Project: OpenRoot, Jesse McMillen. Recovery date: 2026-11-15.

## Preserved implementation

[Compiler source](../../tools/recovered/compile_gate_dossier_v2.py)

The original source is preserved unchanged. SHA-256:

    1c96e4671b0c3a0da4457fe97e473a119e13580d99923e836e507a631e78546e

The operator's two-home forensic capture found eleven matching source
locations. Source reconstruction matched the complete SHA-256.
Publication preparation checked Python syntax without executing the compiler.

## Demonstrated historical scope

This is a targeted source-span compiler, not the complete all-pod autodossier.

It reads a stored question and captured Python source, checks the source-byte
hash, finds top-level statements containing named task receipt calls,
follows directly named local function dependencies, includes the CONFIRM
assignment, and produces a smaller packet with source-line references
and span hashes. It makes no model or network calls and does not execute
the captured source.

October 17 records inspected by the operator contain:
- Original dossier: 4,916 characters.
- Compiled packet: 2,464 characters.
- Original model prompt: 1,994 tokens.
- Compiled model prompt: 810 tokens.
- Recorded wall times: 72.20 versus 44.33 seconds.

Both test answers rejected the supposed task-1 blocking statement.
These are historical stored results, not a newly executed benchmark or
a causal speedup claim. Cache/runtime conditions were not fully controlled.
The test records remain completed_unverified with verified=0.

## Required native data

This recovered version has fixed TEST_ID and ARTIFACT constants.
It is not a general-purpose CLI or standalone deployment.

It expects, relative to the executing user's home:

- pods/pod_interactions/pod.db:
  single_gate_tests_v1(test_id, question, dossier_json), ledger, and chunks.
- pods/pod_openroot_live_v1/pod.db:
  source_bytes(sha256, content), containing the exact captured artifact.

Private databases and their contents are not included. Cloning this
repository does not provision them. Do not treat running the script on
an ordinary checkout as a harmless smoke test.

## Writes when deliberately executed

The compiler initially opens inputs read-only, but main() later writes:

- openroot/data/compiled_dossiers/<new UUID>/ beneath the user's home,
  containing the original dossier, captured source, model packet and manifest.
- compiled_gate_dossiers_v2 in the interaction database.
- Compilation references and records in ledger and chunks.

Filesystem writes and the database commit are not one atomic transaction.
Repeated executions create new IDs. FTS maintenance depends on the
existing database setup; this source does not establish that integration.

Publication does not activate or execute the compiler.

## Limitations

- Task-receipt questions on one configured captured artifact.
- No FTS5/BM25 retrieval, cross-pod discovery, BLAKE3, file ingestion,
  mesh transport, or tar.gz packaging in this component.
- No complete dependency or control-flow analysis.
- Omitted globals and statements may matter.
- Absence from the packet is not proof of absence from the complete source.
- Hash/span integrity and size reduction do not establish answer correctness.

This component contributes to the existing question -> dossier -> compilation
-> reasoning -> verification workflow. It does not replace the pod
foundation, create a competing canonical database, or promote its own
outputs to verified answers.
