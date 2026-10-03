<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# OpenRoot Release Process

## Purpose

OpenRoot releases are reviewed snapshots of versioned repository content.
They make source, documentation, design files, and test artifacts easier to
find and reproduce.

A release is not proof that an associated physical system is validated,
safe, certified, deployable, or appropriate for every environment.

## Release authority

Automation may prepare validation reports, draft notes, and release candidates.

A human maintainer must explicitly approve:

- Git commits and pushes
- Version tags
- GitHub releases
- Public performance, safety, or readiness claims
- Evidence-level changes
- Physical test execution and field deployment

## Pre-release checks

Before creating a release:

```bash
python3 -m compileall -q scripts tests
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate_design_packets.py
python3 scripts/validate_permaculture_context.py data/router_examples designs
python3 scripts/permaculture_ci.py
git diff --check
git diff --cached --check
```

The release candidate must also be reviewed for:

- Correct target commit and branch
- Accurate release title and scope
- Explicit evidence boundary
- No accidental credentials, personal data, runtime state, or generated noise
- No staged protected paths
- Passing GitHub Actions on the exact target commit

## Protected local state

Private operational systems, raw corpora, local databases, embeddings, logs,
receipts, recovery material, and machine-specific configuration are not part
of a public release. Do not add them to a release candidate merely because
they were used during development.

See [Public Boundary](PUBLIC_BOUNDARY.md) for the current inclusion and
exclusion policy.

## Evidence-release boundary

A repository release may publish:

- Design hypotheses
- Assumptions
- Calculations
- Simulations
- CAD and drawings
- BOMs
- Test protocols
- Raw measurements
- Failures and revision notes

It must not represent an L0/L1 packet as physically validated.

| Evidence level | Release-safe statement |
|---|---|
| L0 | Concept, intake, question, hypothesis, or design intent |
| L1 | Source-backed rationale, calculation, simulation, or documentation |
| L2 | Documented controlled physical measurement |
| L3 | Replicated measurement |
| L4 | Documented field validation |
| L5 | Independent replication or mature validation |

## Versioning

Use pre-1.0 tags until OpenRoot offers a stable, documented interface and
evidence boundary that downstream users can rely on.

| Change | Suggested version movement |
|---|---|
| Documentation correction or CI fix | Patch: `v0.1.0` → `v0.1.1` |
| New compatible framework capability | Minor: `v0.1.0` → `v0.2.0` |
| Changed structure or interface | Minor while pre-1.0, with migration notes |
| Stable public contract with mature evidence | Consider `v1.0.0` only after review |

## Manual release procedure

```bash
git switch main
git pull --ff-only origin main

python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate_design_packets.py
python3 scripts/validate_permaculture_context.py data/router_examples designs
python3 scripts/permaculture_ci.py

git status --short
git log -1 --oneline --decorate
```

Then inspect the target SHA and GitHub Actions results. Create a release only
after a human approves the exact tag, title, target commit, and release notes.

