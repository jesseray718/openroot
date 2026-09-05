# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-08-15

### Added

- Initial public release
- `pin` command: local-first IPFS pinning with Pinata fallback
- `status` command: view last 12 ledger entries
- `get` command: fetch content by CID via public gateway
- `hash` command: deterministic SHA-256 tree hashing
- `proof` command: markdown proof + optional GitHub gist
- `return` command: trace CID lineage through ledger
- `verify` command: check CID retrievability via gateway
- `version` command: print version info
- Append-only JSONL ledger with timestamp, node, path, CID, SHA-256
- Post-pin verification (best-effort)
- JWT security: header files instead of inline curl args
- `.gitignore` for ledger privacy
- GitHub Actions CI workflow
- MIT License

### Security

- JWT tokens are passed via temporary header files, not inline `-H` arguments
- Header files are deleted immediately after use
- Process table never exposes credentials
