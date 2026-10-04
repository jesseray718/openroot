# OpenRoot Architecture

OpenRoot is a public systems-design and open-hardware repository. It publishes
reviewed documentation, schemas, examples, design packets, validation tools,
and tests. It is intentionally separate from private research corpora,
operational automation, retrieval indexes, local databases, and recovery
archives.

## Public structure

```text
docs/       Public documentation, policies, evidence standards, and roadmaps
designs/    Open-hardware design packets
schemas/    Public machine-readable contracts
examples/   Small reproducible examples and fixtures
data/       Small public fixtures used by examples and validation
scripts/    Public validators and design-packet utilities
tests/      Regression and public-contract tests
tools/      Reviewed reusable task and context helpers
templates/  Reusable documentation and design-packet templates
site/       Public landing-page source
.github/    Collaboration and CI configuration
```

## Design-packet model

Physical work is published as a versioned design packet. Each packet should
define its scope, status, system boundaries, bill of materials, build method,
safety limits, measurements, test plan, provenance, and license.

The initial packet is `designs/thermal-cascade/`. Its documentation labels
hypotheses, documented sources, proposed methods, and demonstrated results
according to the public claim-status standard.

## Evidence and claims

Public claims use the categories defined in
[`docs/CLAIM_STATUS.md`](docs/CLAIM_STATUS.md):

- `demonstrated`
- `documented`
- `proposed`
- `speculative`

A repository document or release is not by itself a safety certification,
performance guarantee, or physical validation.

## Private boundary

Private preservation systems may contain raw notes, historical artifacts,
search indexes, models, operational logs, and local databases. They are not
part of the public repository and are not automatically release candidates.

See [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md) for inclusion,
exclusion, and publication-review requirements.
