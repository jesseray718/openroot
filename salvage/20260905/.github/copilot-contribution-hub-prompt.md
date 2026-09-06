# Contribution Hub: Copilot Task Prompt

You are assisting with the OpenRoot Contribution Hub.

Read these files first:

- `README_CONTRIBUTION_HUB.md`
- `docs/CONTRIBUTION_WORKFLOW.md`
- `CONTRIBUTION_HUB_POLICY.md`
- `registry/contributions.yaml`
- `UNIFIED_ARCHITECTURE-1.md`, if it exists
- `OPENROOT_NODE001_FIELD.md`, if it exists

Then inspect this repository only. Do not inspect, modify, or contact external
repositories unless I explicitly approve a later task.

Your job is to produce a reviewable inventory, not to make external
contributions.

Create or update `registry/contribution-backlog.md` with no more than five
candidate contributions. For each candidate include:

1. Candidate ID and concise title
2. Exact local source files
3. One-sentence smallest useful unit
4. Evidence label: OBSERVED, SOURCED, SIMULATED, HYPOTHESIS, or VISION
5. Known evidence and missing evidence
6. License/provenance status
7. Safety, compatibility, and scope concerns
8. One possible target, or `keep internal`
9. A 0-3 score for every category in `CONTRIBUTION_HUB_POLICY.md`
10. Total priority score and routing decision
11. One human next action that takes 30 minutes or less

Rules:

- Do not change application code.
- Do not create issues, pull requests, discussions, releases, emails, or
  outreach anywhere.
- Do not state unmeasured concepts as validated engineering.
- Do not choose a target solely because it is popular; verify scope from local
  references if available, otherwise mark target fit uncertain.
- Do not invent licensing, test results, citations, measurements, performance
  values, compatibility claims, or maintainer approval.
- Favor low-maintenance documentation, reproducible measurement records,
  provenance cleanup, and carefully scoped maintainer questions.
- Preserve existing registry entries and update them only when you can point to
  local evidence.
- Keep the backlog concise and practical.

Before making edits, show the proposed file list and a short plan. After edits,
show a concise diff summary and stop for human review.
