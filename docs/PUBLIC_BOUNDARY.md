# Public Boundary

## Purpose

OpenRoot is a public systems-design, documentation, and open-hardware repository. It publishes reviewed material that helps others understand, evaluate, reproduce, adapt, or contribute to the work.

This repository is a curated public projection. It is not a complete archive of every draft, tool run, corpus record, personal workspace, or historical experiment associated with OpenRoot.

## Included Material

Public repository material may include:

- Mission, scope, architecture, governance, and contribution documents.
- Claim and evidence standards, including Newton Chain records.
- Public schemas, validation rules, examples, and fixtures.
- Reviewed and reproducible software tools.
- Open-source hardware design packets with build, safety, measurement, provenance, status, and licensing information.
- Test plans and results that are appropriate for public review.

## Excluded Material

The following remain outside the public repository unless separately reviewed and explicitly approved for release:

- Raw research corpora, content-addressed archives, search indexes, embeddings, and local databases.
- Credentials, tokens, device identifiers, personal data, and infrastructure-specific configuration.
- Runtime logs, workflow reports, terminal captures, receipts, inbox/outbox state, and generated indexes.
- Backup trees, recovery material, vendor copies, quarantine material, and unreviewed historical artifacts.
- Drafts, experiments, or claims lacking provenance, licensing, safety, and evidence review.

## Claim Status

Public documents should label substantive claims using one of these statuses:

- `demonstrated` — supported by accessible methods, measurements, artifacts, or repeatable results.
- `documented` — described with available sources or provenance, but not independently reproduced within this repository.
- `proposed` — a design, hypothesis, or planned method that has not yet been demonstrated.
- `speculative` — an exploratory idea or interpretation that should not be treated as established fact.

## Publication Review

Before material enters this repository, it should receive review for:

- Provenance and authority to publish.
- Applicable licenses and third-party obligations.
- Privacy, credentials, and operational-security exposure.
- Safety information for hardware, chemistry, energy, or field work.
- Claim status, evidence links, and reproducibility.
- Stable public value independent of private operational context.

## Design Packets

Physical and open-hardware work is published as a design packet rather than as an unsupported claim. A packet should identify its purpose, scope, bill of materials, build procedure, safety constraints, measurement method, test plan, provenance, license, and current status.

The `designs/thermal-cascade/` directory is structured as one such packet. Its documents define its specific scope and evidence status.

## Private Preservation

OpenRoot maintains private preservation and discovery systems for raw materials, historical records, and local retrieval. Those systems may inform public work, but their contents are not automatically public and are not a substitute for release review.
