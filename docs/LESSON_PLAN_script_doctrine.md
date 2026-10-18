# OpenRoot Script Doctrine — Lesson Plan v1.0

**Author:** Z.ai (assistant) for Jesse McMillen / OpenRoot
**License:** CC-BY-SA 4.0
**Status:** Sealed as pod `lesson_plan_script_doctrine` (proof of concept)

## Foundational Principle

Every script is a receipt-producing artifact. The script's output IS the receipt. The receipt must be:

- **Canonical**: same input produces same output, byte-identical
- **Verifiable**: a third party can confirm integrity without trusting the author
- **Idempotent**: running twice produces the same state, not duplicate state
- **Auditable**: the log artifact can be inspected later to understand what happened

## The 12 Laws

### 1. File on disk first, never pipe
**NEVER** pipe a long script into an interactive shell. **ALWAYS** write to a file, then execute. Failure in inline execution forces regeneration from scratch. With a file on disk, you patch the one failing line and re-run.

### 2. Compile gate before execution
- Python: `python3 -m py_compile script.py` before `python3 script.py`
- Bash: `bash -n script.sh` before `bash script.sh`

### 3. Canary markers for log grep-ability
Every script starts and ends with a canary: `CANARY:OPENROOT-POD-LOADER-V1 ... COMPLETE [exit=0]`. Grep finds every successful run in seconds.

### 4. Stage markers: gate / banked / held
- `[gate]` — entering a stage
- `[banked]` — success
- `[held]` — soft failure (continues)

A 200-line log becomes scannable in 5 seconds.

### 5. Idempotency
Running twice = same result. No duplicate state. Don't regenerate keys if they exist. Don't re-ingest files with the same sha256. Use `INSERT OR IGNORE` for dedup.

### 6. Deterministic output (canonical serialization)
`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` — same logical object always produces the same bytes.

### 7. Separate code paths for sign and verify
Sign with `openssl pkeyutl -sign`. Verify with `openssl pkeyutl -verify`. Different binaries, different failure modes.

### 8. Pre-flight safety checks
Before commit: confirm private key is gitignored. Before chaining receipts: confirm parent receipt_id matches expected value.

### 9. One-paste execution
The entire script body lives in a heredoc that can be pasted in one shot. If the heredoc is too long, split into multiple smaller heredocs that each write one file.

### 10. Receipt logging
Every script run produces a log artifact: `exec > >(tee -a "$LOG") 2>&1`. When something goes wrong, you reconstruct what happened from the log.

### 11. Tool = subprocess
Use `openssl` for crypto. Use `git` for version control. Use `sqlite3` for DB. Don't reimplement battle-tested libraries in your own code.

### 12. Dry-run by default, CONFIRM=1 to arm
Destructive operations default to dry-run. Require explicit `CONFIRM=1` to arm.

## The Joules-per-Interaction Metric

The 12 laws optimize for "most output per unit of human effort":
- File-on-disk: saves 30 minutes per failed run
- Compile gate: saves 5 minutes per typo
- Canary + stage markers: saves 10 minutes per debug session
- Idempotency: saves "did I just double-create that?" anxiety
- Deterministic output: saves "why does this hash differ?" debugging
- Separate code paths: catches crypto bugs before they ship
- Pre-flight checks: catches security mistakes before they're irreversible
- One-paste execution: saves 4 minutes per workflow
- Receipt logging: saves "what did I do yesterday?" archaeology
- Tool = subprocess: saves 2 hours per crypto operation
- Dry-run default: saves you from irreversible mistakes

Total: ~3 hours saved per work session.

## Tools and Dependencies

### Required
- Python 3.10+
- bash
- sqlite3 (with FTS5 support)
- openssl (with Ed25519 support)
- git
- sha256sum

### Recommended
- Ollama (local model inference for embeddings)
- nomic-embed-text model (`ollama pull nomic-embed-text`)
- blake3 (`pip install blake3`)
- git-filter-repo (history rewriting)

### Environment
- Linux (Ubuntu 24.04 tested)
- Tailscale (mesh SSH access)
- Termux + proot-distro Alpine (phone-side sandbox)

## Workflow Pattern

1. Write the script to disk
2. Compile-gate (`python3 -m py_compile` or `bash -n`)
3. Dry-run (no CONFIRM)
4. Arm (CONFIRM=1)
5. Verify (independent command, e.g. `openssl pkeyutl -verify` with temp file)
6. Commit
7. Push

## The Pod Loader Architecture

The pod loader implements the doctrine:
1. Dual-hash content addressing — sha256 for file identity, blake3 for chunk identity
2. FTS5 indexing — every chunk indexed for BM25 retrieval
3. Optional nomic embeddings — via Ollama, for semantic search
4. Merkle-sealed pod root — every pod has a tamper-evident root hash
5. Idempotent ingestion — same file never ingested twice
6. Budget-capped retrieval — dossier engine returns only what fits in token budget

This is the receipt doctrine applied to knowledge itself.

One Human Family. Build what serves. Track transparently. Reward contribution and care.
