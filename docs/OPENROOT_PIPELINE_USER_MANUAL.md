# OpenRoot Local Pipeline User Manual

## Purpose

OpenRoot Local Pipeline captures text, indexes explicitly selected UTF-8
files, retrieves relevant excerpts with SQLite FTS5, and prepares context
for a human-operated AI session.

This manual describes the standalone `or-pipeline` rollout script.
It does not certify that installation or an end-to-end test has succeeded
on any particular node.

The pipeline is not an autonomous agent. It does not call a model,
execute retrieved instructions, or independently verify factual claims.

## Requirements

- Bash
- Python 3 with SQLite FTS5 support
- A writable home directory
- Optional Termux:API clipboard commands on Android

On Termux, install Python if absent:

    pkg install python

Clipboard integration additionally requires the Termux:API Android app,
its compatible command-line package, and Android clipboard access.

Installation of packages or applications is separate from this pipeline.

## Installation and portability

The rollout installer creates:

- A versioned directory named `~/openroot-pipeline-release.*`
- The launcher `~/bin/or-pipeline`
- Runtime storage under `~/.local/share/openroot-pipeline`

The installer refuses to replace an existing launcher.

Install separately on each host. The launcher contains absolute paths
to that host's Python interpreter and release file; copying the launcher
from Android to Linux is not a portable installation.

The installer and runtime do not modify existing OpenRoot capture
databases, Newton ledgers, Git history, or universal-database symlinks.

## First check

Run:

    "$HOME/bin/or-pipeline" doctor

Review:

- Python and SQLite versions
- Database location
- Record count
- SQLite quick-check result
- Available disk space
- Clipboard command availability

A successful doctor run checks basic runtime readiness.
It does not prove end-to-end correctness or factual accuracy.

Each command creates a timestamped run directory and prints its location.

## Capture text

Capture an explicitly supplied observation:

    "$HOME/bin/or-pipeline" capture \
      "A15 repository updated; runtime behavior remains untested."

Attach an operator-supplied category:

    "$HOME/bin/or-pipeline" capture --kind observation \
      "The measured inlet temperature was 25 C."

The category is a label, not automatic classification or verification.

Capture the clipboard:

    "$HOME/bin/or-pipeline" capture

With no text arguments, the command reads the Android clipboard.
It reports an error if clipboard access is unavailable or times out.

Do not capture passwords, API keys, private keys, or confidential
information that you do not intend to retain.

## Import files

Import only files selected explicitly:

    "$HOME/bin/or-pipeline" add \
      "$HOME/openroot/SESSION_STATE.md" \
      "$HOME/openroot/WORKLOG.md"

Input limits:

- Regular files only
- Final-path symlinks rejected
- UTF-8 text required
- NUL-containing input rejected
- Maximum 2,000,000 bytes per imported file

No recursive phone or repository scan occurs.

Each successful import creates a separate record.
Identical bytes share a content-addressed object, but repeated imports
still create additional searchable records.

Batch imports are not all-or-nothing: earlier successful imports remain
if a later file fails. Inspect the run directory before retrying.

Imported content is labeled `imported_unverified`.

## Search indexed evidence

Run:

    "$HOME/bin/or-pipeline" search census status

Limit results:

    "$HOME/bin/or-pipeline" search census --limit 5

The current search:

- Uses SQLite FTS5 keyword matching
- Combines up to 24 unique query words with OR
- Orders matches using SQLite BM25 ranking
- Returns between 1 and 20 results
- Shows excerpts rather than complete documents

Keyword relevance is not semantic understanding or factual confidence.

Only material explicitly captured or imported into this standalone
database is searched. Existing Float databases, other pods, receipts,
and repository files are not automatically included.

## Prepare an AI handoff

Run:

    "$HOME/bin/or-pipeline" ask \
      "What evidence supports the current rollout status?" --clip

The command creates:

- `question.txt`
- `retrieval.json`
- `briefing.md`
- `ai_prompt.md`
- `receipt.json`

With `--clip`, it attempts to copy `ai_prompt.md` to the clipboard.
It prints whether copying succeeded, failed, or was unavailable.

Paste the prompt manually into your chosen AI.

The pipeline itself does not send a network request.
Pasting into a cloud AI may transmit every included excerpt to that
provider. Review and redact sensitive material before sharing.

The prompt requests evidence references, separation of facts from
inferences and unknowns, and exclusion of integrity-failed evidence.
These are instructions to the model, not an enforced verification gate.

## Read output files

Use the exact run directory printed by the command:

    cat "/exact/run/directory/briefing.md"
    cat "/exact/run/directory/ai_prompt.md"
    cat "/exact/run/directory/receipt.json"

No `latest` alias is created.

If clipboard copying fails, the saved files remain available.

## Storage layout

Runtime storage:

    ~/.local/share/openroot-pipeline/
      index.sqlite3
      objects/
        <sha256>.txt
      runs/
        <timestamp-and-random-id>/

Each run starts with `start.json`.
Successful commands normally finish with `receipt.json`.
Failures preserve partial output and an error JSON record.

Files are created without overwriting existing run files.
This is not write-once hardware, a signed ledger, or a Newton-chain
integration; a user with filesystem access can still change them.

## Integrity checks

Run:

    "$HOME/bin/or-pipeline" verify

This compares stored content-object bytes with hashes in the records
table and reports failed record IDs.

The command does not:

- Verify factual truth
- Verify the current original source file
- Validate every FTS index entry against the object
- Verify all past run receipts
- Provide cryptographic signatures or trusted timestamps

Search also checks stored-object integrity for each returned record.
A failed object is flagged; retrieval excerpts still require review.

SHA-256 establishes byte consistency against a recorded hash.
It does not establish truth, authorship, or scientific validity.

## Receipts and measurement

Receipts record run-file hashes and command details.

Model output is not automatically imported, reviewed, or learned.
Energy consumption is not measured; `energy_joules` is null.
No confidence percentage, thermodynamic benefit, or energy saving
should be inferred from a successful command.

## Troubleshooting

### Command not found

Use the full launcher path:

    "$HOME/bin/or-pipeline" doctor

No PATH modification is required.

### FTS5 unavailable

The preflight or database initialization will fail explicitly.
Use a Python installation with SQLite FTS5 enabled.

### No indexed evidence matched

Import relevant files, or use narrower terms:

    "$HOME/bin/or-pipeline" search census

This pipeline cannot retrieve files that were never indexed.

### Clipboard unavailable

Read the generated prompt file.
Check Termux:API installation and Android clipboard access.

### Import failed

Check file existence, UTF-8 encoding, size, and symlink status.
Earlier successful imports remain preserved.

### Integrity failure

Stop relying on the affected record.
Preserve its object, database, and error report for investigation.
Do not silently replace evidence to make the test pass.

### Old `or-ask` still fails

`or-pipeline` is a separate command.
It does not repair or replace the earlier `or-ask` script.
Use `~/bin/or-pipeline` explicitly.

## Backup and recovery

For a simple consistent backup, stop all pipeline commands before
copying the complete runtime directory and installed release directory.

Preserve the launcher as installation documentation, but reinstall
or adjust it deliberately on a different host.

Verify the copied objects after recovery.
No automatic synchronization, retention, or deletion is configured.

## Safety boundaries

The current implementation performs no automatic:

- AI API calls
- Git commits or pushes
- File deletion or deduplication
- Background daemon installation
- Model downloads
- Fleet rollout or SSH transfer
- Physical-system control
- Newton-chain append
- Automatic learning or promotion to verified truth

Human review remains necessary before consequential actions.

## Publication scope

This manual documents a proposed implementation.
Publishing this document alone does not publish the executable,
its installer, or a tested release.

A reproducible software release should separately include reviewed
source, installation instructions, license, and test results.
