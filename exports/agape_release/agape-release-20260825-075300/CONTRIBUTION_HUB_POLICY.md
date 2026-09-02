# Contribution Hub Policy

## Objective

Convert reusable OpenRoot work into small, safe, evidence-labeled candidates
that can be reviewed by a human and, where appropriate, offered to an upstream
project with minimal coordination burden.

## Non-negotiable boundaries

- This system inventories and drafts; it never submits external issues, pull
  requests, releases, funding requests, outreach, or licensing changes without
  explicit human approval.
- Treat all safety, RF, electrical, chemical, thermal, structural, financial,
  medical, environmental, and performance statements as unverified unless their
  evidence label and supporting record say otherwise.
- Never promote `HYPOTHESIS` or `VISION` into `SOURCED` or `OBSERVED`.
- Preserve original authorship, source locations, licenses, uncertainty, and
  upstream project scope.
- Prefer a maintainer question, documentation correction, test, example, or
  field record over a large architecture proposal.
- Do not copy OpenRoot branding, philosophy, or system-level claims into an
  upstream repository unless that community requests it.

## Candidate scoring

Score each dimension 0 to 3:

- `user_value`: Helps real users, especially low-resource participants.
- `evidence`: Strength and traceability of support.
- `scope_fit`: Fits the target project's stated purpose.
- `license`: Reuse rights are known and compatible.
- `safety`: Risks are understood and appropriately bounded.
- `reversibility`: Can be withdrawn or changed cheaply.
- `maintenance`: Low long-term maintainer burden.
- `coordination`: Low need for meetings, permissions, or social overhead.

Calculate:

priority_score = user_value + evidence + scope_fit + license + safety +
                 reversibility + maintenance + coordination

## Routing rules

- `0-11`: Keep internal; identify missing evidence or provenance.
- `12-17`: Prepare a local evidence, provenance, or documentation task.
- `18-21`: Draft a maintainer-facing question; do not submit it.
- `22-24`: Draft the smallest possible issue or pull request, pending approval.

Any score with `license < 2`, `safety < 2`, or `scope_fit < 2` is automatically
"keep internal" regardless of its total score.

## Required output

Every proposed candidate must include:

- Source repository and exact file paths
- One-sentence smallest useful unit
- Evidence label and links or file paths supporting it
- Known limits and missing evidence
- License/provenance status
- Safety and compatibility notes
- Candidate target and documented reason for fit
- Score breakdown and routing decision
- One next human action estimated at 30 minutes or less
