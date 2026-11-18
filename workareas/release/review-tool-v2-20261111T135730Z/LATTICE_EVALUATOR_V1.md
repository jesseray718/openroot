# Lattice Evaluator v1

A sandbox-only OpenRoot-compatible evaluator inspired by the A15
`lattice_cli.py` reference implementation.

It evaluates one explicit JSON task, produces a proof trace and Merkle
root, and can append a hash-chained entry only to its own sandbox ledger.

## Boundary

- Reads only an explicit sandbox task JSON file.
- Writes only inside `workareas/a15-engine-sandbox/`.
- Never writes to the live OpenRoot tree.
- Never executes an original A15 script.
- Requires `--approve-write` before creating or appending to the sandbox ledger.
- Does not promote sandbox entries to canonical OpenRoot evidence.

## Commands

Proposal only:

```bash
python3 workareas/a15-engine-sandbox/lattice_evaluator_v1.py \
  --task workareas/a15-engine-sandbox/tasks/demo_task.json
```

Gated sandbox append:

```bash
python3 workareas/a15-engine-sandbox/lattice_evaluator_v1.py \
  --task workareas/a15-engine-sandbox/tasks/demo_task.json \
  --approve-write
```

Verify sandbox chain:

```bash
python3 workareas/a15-engine-sandbox/lattice_evaluator_v1.py --verify
```

## Rules v1

| Rule | Condition | Effect |
|---|---|---|
| R001 | `observation_days < 7` | ETA penalty 6 |
| R002 | No feedback mechanism | ETA penalty 8 |
| R003 | Compute without joule accounting | ETA penalty 6 |

Claim eligibility requires ETA of at least 40.0. An empty proof trace
means no penalties fired; it does not make a task ineligible.

## Current artifacts

- Evaluator: `lattice_evaluator_v1.py`
- Sandbox ledger: `acre/ledger.jsonl`
- Task fixtures: `tasks/demo_task.json`, `tasks/demo_task_qualified.json`
- Milestone receipt: `MILESTONE_SANDBOX_LATTICE_EVALUATOR_V1.json`
