# OpenRoot

**OpenRoot is an open-source technology commons for preserving, validating,
improving, and implementing knowledge that can materially improve the world.**

OpenRoot is a local-first, evidence-oriented workflow for converting captured
artifacts into verified, reusable engineering knowledge. It connects open
hardware, engineering research, technical literature, experiments, local
computation, and practical infrastructure through reproducible evidence.

## Evidence workflow

```text
capture -> SHA-256 inventory -> report-only dedupe
        -> local SQLite FTS5 + semantic retrieval
        -> bounded routing -> validation
        -> Newton Chain receipt -> human-reviewed GitHub promotion
```

Automation can inspect, propose, and validate bounded work. Human review
controls commits, pushes, public publication, physical implementation, and
other consequential actions.

## Public repository boundary

This repository contains reusable source code, tests, schemas, documentation,
and redacted examples. It intentionally excludes personal documents, live
SQLite databases, model files, embeddings, archives, logs, device exports,
credentials, and machine-specific runtime state.

## Appropriate technology

OpenRoot supports open hardware designs, reproducible experiments, fabrication
and maintenance workflows, local-first computing, and resource-aware technical
documentation. A passing workflow validates repository checks; it does not
prove physical performance, safety, field readiness, certification, or
regulatory compliance.

## Project maps

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Routing contract](docs/ROUTING.md)
- [Newton Chain contract](docs/NEWTON_CHAIN.md)
- [Newton Chain foundations](docs/newton_chain/README.md)
- [Security policy](SECURITY.md)

## Licensing

- Code and software: GPL-3.0-only unless a file states otherwise.
- Documentation and design material: CC BY-SA 4.0 unless a file states otherwise.

See [LICENSE](LICENSE) and applicable file headers.
