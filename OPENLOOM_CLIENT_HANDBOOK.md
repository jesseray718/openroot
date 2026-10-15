# OpenLoom Local Client Handbook

OpenLoom is a local-first evidence and research system. You give it a task,
it records the task, uses local evidence, produces a reviewable output, and
never autonomously publishes or destroys data.

## Core command

```bash
pod "your task"
```

or, for project research:

```bash
pod project thermal-cascade "your task"
pod project aerocement "your task"
pod project black-locust "your task"
```

## Daily commands

| Command | Purpose |
|---|---|
| `pod ask "..."` | Ask a general local-AI question |
| `pod project <name> "..."` | Research a specific project |
| `pod verify` | Verify the OpenLoom demo pod |
| `pod check` | Compile, test, verify, and inspect database |
| `pod load` | Rebuild the manual evidence database |
| `pod ui` | Start the local evidence UI |
| `pod status` | Show Git status and latest model output |
| `pod sync-status` | Show synchronized evidence files |
| `pod help` | Show command help |

## Projects

### Thermal cascade

Research heat capture, heat reuse, thermal storage, and cascading energy
flows.

Example:

```bash
pod project thermal-cascade "Identify heat sources, temperature tiers, storage options, useful loads, and three low-cost experiments."
```

### Aerocement

Research low-cost, lower-carbon cementitious materials, curing, and small
test coupons.

Example:

```bash
pod project aerocement "Compare candidate mixes and define safe coupon tests."
```

### Black locust

Research propagation, agroforestry, biomass, soil improvement, and
Missouri-specific ecological safeguards.

Example:

```bash
pod project black-locust "Create a safe propagation and management plan."
```

## Evidence rules

1. Raw evidence is never overwritten.
2. Every imported artifact has a SHA-256 hash.
3. AI output is a proposal, not canonical evidence.
4. SQLite databases stay local.
5. JSONL, Markdown, manifests, and receipts are safe to synchronize.
6. Nothing is committed or pushed without human review.

## Safe synchronization

Sync these:

- `tasks/`
- `runs/*/output.md`
- `evidence/*/exports/`
- `evidence/*/receipts/`
- `evidence/*/tables/tables_manifest.json`
- `evidence/*/tables/*.jsonl`

Do not sync:

- `*.sqlite3`
- `*.db`
- `*.db-wal`
- `*.db-shm`
- `.venv/`
- `demo-pod/`
- model caches

## Local model

Default model:

```bash
qwen2.5:1.5b
```

Start Ollama:

```bash
ollama serve
```

Pull the model:

```bash
ollama pull qwen2.5:1.5b
```

Use a coding-focused model instead:

```bash
export POD_MODEL=qwen2.5-coder:1.5b
```

## Local UI

Start:

```bash
pod ui
```

Open:

```text
http://127.0.0.1:8000
```

The UI is local-only and read-only.

## Recovery

If something seems broken:

```bash
pod check
pod verify
pod status
```

To rebuild only the manual evidence database:

```bash
pod load
```

To inspect the latest AI result:

```bash
pod status
```

## Publishing boundary

The local client may:

- Create task files
- Query local evidence
- Run local models
- Write run outputs
- Prepare proposed changes

The local client may not, without explicit human approval:

- Commit
- Push
- Open or merge PRs
- Delete evidence
- Spend money
- Access non-allowlisted network services
- Execute destructive system commands
