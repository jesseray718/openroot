# Repository Layout

## Public Core

The public OpenRoot repository is organized around reviewed, reusable work:

| Path | Role |
|---|---|
| `docs/` | Public documentation, standards, architecture, and design guidance |
| `docs/newton_chain/` | Claim and inference-record documentation |
| `schemas/` | Public machine-readable interfaces and validation contracts |
| `designs/` | Open-hardware design packets |
| `examples/` | Small reproducible examples and fixtures |
| `tests/` | Validation and regression checks |
| `tools/` | Reviewed, reusable developer or corpus-support tools |
| `.github/` | Public collaboration and automation configuration |

## Transitional Legacy Areas

Some historical paths remain while OpenRoot is being consolidated. Their
presence does not make them supported public interfaces.

| Path category | Treatment |
|---|---|
| Runtime logs, reports, inbox/outbox, and generated indexes | Local operational state; do not depend on or publish new material here |
| Archives, attic, backups, recovery, and quarantine directories | Preservation material; retain privately and migrate only reviewed items |
| Large script collections and experimental analysis | Review individually before promotion to `tools/`, `examples/`, `designs/`, or `docs/` |
| Corpus databases, embeddings, and local retrieval state | Private infrastructure; excluded from releases |

## Promotion Path

A candidate becomes public core only after:

1. Its purpose is understandable outside the original local workspace.
2. Its provenance and licensing are known.
3. It has no secrets, personal data, or machine-specific assumptions.
4. Its claims use the public claim-status vocabulary.
5. It has adequate documentation, validation, and safety context.
6. It is placed in the appropriate public-core path.

## Separate Projects

OpenRoot is the shared hub. A component should move to a separate repository
only when it has an independent audience, release cycle, maintainer path,
test surface, and licensing boundary.
