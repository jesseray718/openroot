# OpenRoot continuity and Copilot handoff

This document preserves reported observations and design intent.
It does not certify uninspected code or successful production integration.

## User priorities

- Preserve and recover the original trained non-generative router.
- Do not replace working routing with an LLM merely because it is available.
- Search existing pods and reuse applicable cached pathways before inference.
- Preserve mistakes, corrections, verification evidence and applicability.
- Prefer complete pasteable commands with explicit outcomes.
- Never claim success from file creation, a hash, or shell syntax alone.
- Preserve checkpoints in Git without uploading private pods or credentials.

## Desired pathway behavior

correct → verify → cached reusable pathway

wrong → diagnose → correct → verify → cached corrected pathway

A hash establishes identity, not truth.
A model-generated answer is not automatically verified.
Reusing a changed source or environment requires applicability checks.

## Known local locations, requiring current verification

Primary repository:
  /home/jesse/openroot

Universal pod successfully queried:
  /home/jesse/pods/pod_universal/pod.db
  FTS table: chunks_fts

Other observed locations:
  ~/.local/state/openroot-work-records/pod.db
  ~/.local/state/openroot-work-records/pods/euclid-book-I/
  ~/.local/state/openroot-work-records/pods/openrouter-setup/
  ~/.local/state/openroot-work-records/pod-access/
  ~/.local/state/openroot-integration/

Earlier router/cache investigation candidates:
  ~/openroot/bin/smart_router.py
  ~/openroot/data/route_cache.db
  ~/openroot/bin/router_cache_probe_v2.py

Existence and fitness must be checked, not assumed.

## Recent experiments and limitations

1. Nine paid question-chain rounds completed.
   Prior outputs were supplied as context.
   This did not demonstrate verified cache replay or improved correctness.

2. An OpenRouter advisory run repeated placeholder APIs.
   Its proposed installer was rejected.
   Do not reuse that output as an accepted implementation.

3. All-home SQLite discovery reported hundreds of FTS-bearing databases.
   Active pods, backups, experiments and old checkouts were mixed.
   Duplicate copies are not independent corroboration.

4. A broad adapter accumulated all matches in RAM before printing.
   It ran for minutes and held substantial memory.
   Replace that pattern with streaming evidence persistence and receipts.

5. Universal-pod OpenRouter keyword matches were demonstrated.
   This does not establish complete associated-record retrieval.

6. Euclid Book I source and question packets were created.
   Questions/evidence packets are not verified solution pathways.

7. An experimental sidecar installation script was supplied.
   Do not assume it ran, passed, was pushed, or was merged.
   Locate actual reports and commits before asserting its status.

## Next implementation acceptance criteria

- Recover the original router source, training artifacts and interfaces.
- Preserve originals; never execute unknown serialized models to inspect them.
- Inspect existing cache and pod schemas before integrating.
- Exact applicable verified reuse must avoid new model dispatch.
- Corrections must take precedence over rejected predecessors.
- Conflicts must hold, not silently pick an arbitrary answer.
- Retain source and record identities through retrieval.
- Separate retained full evidence from compiled model context.
- Record actual latency, charges, unknowns and failure outcomes.
- Energy measurements must name their hardware domain.
- Local energy does not establish remote-provider energy.
- Evaluate synthetic tests separately from real source-backed answer tasks.
- Keep experimental branches separate from production until reviewed.

## Git preservation boundary

Source checkpoints do not back up uncommitted files, ignored files,
private databases, model weights or external directories.

Use explicit file lists. Do not use `git add .` for a dirty workspace.
Never commit API keys, credential stores, private pod content or raw
unreviewed conversation archives.
