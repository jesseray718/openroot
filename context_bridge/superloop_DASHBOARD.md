<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# OpenRoot Superloop Dashboard

- Generated UTC: `2026-09-25T11:35:23.550859+00:00`
- Branch: `chore/superloop-ci-cd-foundation`
- HEAD: `05595397fadf`
- Working tree: `12 changed/untracked path(s); details intentionally omitted`
- Last commit: `05595397 2026-09-25T06:13:26-05:00 [SEAL] superloop session provenance: v1→v4 script evolution, paste-truncation lessons; AI-assisted, human-gated`

## Command Flow Health

- Source: sanitized local superloop state; no raw command history is emitted here.
- Drift review compares categorized activity with `MASTER_TODO` and accepted work.

## Routing Evidence
- Registry: `data/model_registry.json`
- Registry SHA-256: `1c3bda2cc810a5022cc7b0eb9e7c5fd0cb54b944a4900c1356cf7038a5f1c8fc`
- Registry entries: `6`

## Local AI Boundary

- FTS5/Git retrieval provides bounded evidence.
- A local small model may classify or summarize evidence.
- A local coder may propose a minimal patch and tests.
- No model output is applied, committed, pushed, tagged, released, or deployed without human review.

## Publication Boundary

- Never publish tokens, secrets, raw prompts, raw command history, private paths, private IPs, databases, or telemetry.
- The public status pulse is a redacted summary, not a source of authority.
