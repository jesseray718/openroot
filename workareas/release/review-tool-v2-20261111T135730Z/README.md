# OpenRoot sandbox review v2

Noncanonical experimental workflow. Not a canonical foundation replacement.

- Original A15 files and v1 artifacts are not modified.
- Preview commands do not record events.
- --record explicitly writes only this package's review_events.jsonl.
- Writes use a cooperative process lock and atomic whole-file replacement.
- Symlink paths are rejected.
- Existing chains are verified before writes.
- Duplicate workflow operations are idempotent.
- Rules record pass and fail checks.
- Scores are heuristics, not ETA seconds, measured efficiency, or truth.
- Approval labels are self-asserted, not authenticated identities.
- No seal command and no canonical ledger.
- Review events must not be imported as canonical evidence automatically.

Operational limits:
- Local trusted Linux account and local filesystem expected.
- Cooperative locks are not protection against a hostile same-user process.
- No adversarial sandbox or authenticated approval service is provided.
- Ledger file limit: 16 MiB.
- Full-file replacement favors small bounded experiments, not high-volume service.
- Canonical integration requires the existing native OpenRoot writer/schema.
- Negative tests and deployment-specific review remain required.
