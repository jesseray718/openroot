<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Changelog

All notable OpenRoot changes are documented here.

OpenRoot uses pre-1.0 semantic-style versioning while its interfaces,
design packets, test protocols, and evidence base are still evolving.

A GitHub release records a reviewed repository snapshot. A release does not,
by itself, establish physical performance, safety, certification, regulatory
approval, deployment readiness, or field validation.

## [Unreleased]

### Added

- Evidence-gated permaculture routing framework.
- Read-only Open Hardware Preview for design-packet readiness review.
- Local and GitHub Actions validation for router contexts.
- Initial `thermal-cascade` design packet with L0 evidence boundary.
- Structured paths for BOM, calculations, safety, build instructions,
  operations, maintenance, replication, test protocol, and results.

### Safety and evidence boundaries

- The Thermal Cascade packet remains an L0 concept/intake unless its packet
  contains appropriately documented evidence that supports a higher level.
- CI validates repository structure and deterministic checks only.
- CI passing does not validate physical performance, safety, construction,
  electrical work, pressure systems, water safety, food safety, or compliance.
- Protected local superloop runtime state remains outside normal source history.

## [0.1.0] - Planned

### Framework baseline

- OpenRoot design-packet framework.
- Evidence-level policy and claim boundary.
- Permaculture Router v0.1 decision-support implementation.
- Read-only open-hardware preview and CI validation path.


- Added contributor credit: Rehan Tariq (@Reh1t) — LLM & SQLite RAG integration (PR #63).
