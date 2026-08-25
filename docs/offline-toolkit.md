# OpenRoot Offline Toolkit — Architecture

> Works **fully offline**. No internet connection required to use any feature on this page.

---

## Overview

The offline toolkit provides a persistent local workspace so you can keep making forward
progress even when you have no internet connection.  When connectivity returns, a
deterministic sync replay applies queued work to any configured remote endpoint.

```
┌──────────────────────────────────────────────────────────────┐
│  OpenRoot Offline Toolkit                                     │
│                                                               │
│  ┌────────────┐   enqueue   ┌──────────────┐                 │
│  │   CLI      │ ──────────► │ OperationQueue│                │
│  │  offline/  │             │  (JSONL file) │                │
│  │  cli.py    │             └──────┬────────┘                │
│  └────────────┘                    │ pending items           │
│                                    ▼                         │
│  ┌─────────────┐  rank()   ┌──────────────┐                 │
│  │ PriorityScorer│◄────────│ replay/sync  │                  │
│  │ urgency²×impact│        └──────┬────────┘                │
│  └─────────────┘                   │ apply                   │
│                                    ▼                         │
│  ┌─────────────┐  hash    ┌──────────────────┐              │
│  │ DedupIndex  │◄─────────│ Remote / Local   │              │
│  │ SHA-256     │          │ Store            │              │
│  └─────────────┘          └──────────────────┘              │
│                                                               │
│  ┌─────────────────────┐  ┌──────────────────────┐          │
│  │ DataLifecycle       │  │ ThermalRegulator      │         │
│  │ soft-delete / purge │  │ CPU/mem → concurrency │         │
│  └─────────────────────┘  └──────────────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

---

## Modules

### `offline/queue.py` — OperationQueue

Append-only JSONL file.  Each entry has:

| Field | Description |
|---|---|
| `idem_key` | UUID – prevents double-apply during replay |
| `op_type` | String tag (e.g. `"task"`, `"note"`) |
| `payload` | Arbitrary JSON |
| `urgency` / `impact` | Scores for priority ranking |
| `status` | `pending` → `applied` or `failed` |

**Idempotency:** re-enqueuing an existing `idem_key` is silently skipped.

**Replay:** `offline:sync` sends `pending` entries to the configured endpoint in
priority order, marking each `applied` on success or `failed` on error.

---

### `offline/dedup.py` — DedupIndex

Content-addressed deduplication using SHA-256.

- First time a payload is seen → stored as canonical record, returns `(hash, False)`.
- Subsequent identical payloads → returns `(hash, True)`, increments `ref_count`.
- Index persists to a JSON file; a fresh `DedupIndex` reloads it automatically.

**Collision strategy:** SHA-256 collisions are computationally infeasible for
practical payloads.  The index stores the first-seen record as canonical;
future collisions (if any) would be treated as duplicates.  This is
documented as a known theoretical limitation.

---

### `offline/lifecycle.py` — DataLifecycle

Lifecycle events are appended to a JSONL ledger (fully auditable).

```
soft_delete(id)   →  marked deleted, retained for retention_days
purge_eligible()  →  records past their retention window
hard_purge(id, confirmed=True)  →  removes from ledger + dedup index
restore(id)       →  cancels a soft-delete
```

**Safety:** `hard_purge` requires `confirmed=True`.  The CLI `offline:purge`
lists eligible records and asks for `--confirm` before executing.

---

### `offline/priority.py` — PriorityScorer

```
score = urgency² × impact × w_u × w_i
```

Quadratic weighting on urgency means small increases in urgency produce
large jumps in score, ensuring the most urgent needs are served first.

Weights `w_u` and `w_i` are configurable in `.env` or `config.json`.

---

### `offline/thermal.py` — ThermalRegulator

Reads CPU load (Linux `/proc/stat` or `psutil`) and reduces the allowed
concurrency when pressure is high:

| CPU % | Concurrency |
|---|---|
| ≥ `cpu_high` (80%) | 1 (throttled) |
| between thresholds | scaled linearly |
| ≤ `cpu_low` (40%) | `max_concurrency` |

Temperature readings use `psutil.sensors_temperatures` where available;
silently skipped on unsupported platforms.

---

## Configuration

All settings have safe offline defaults.  Override via:

1. Environment variables (see `.env.example`)
2. `~/.openroot/offline/config.json` (written by `offline:init`)

---

## What works offline vs. requires connectivity

| Feature | Offline | Requires connectivity |
|---|---|---|
| `offline:init` | ✅ | |
| `offline:status` | ✅ | |
| `offline:work` | ✅ | |
| `offline:purge` | ✅ | |
| `offline:doctor` | ✅ | |
| `offline:sync` (no endpoint) | ✅ no-op | |
| `offline:sync` (with endpoint) | ❌ | ✅ HTTP POST to endpoint |
