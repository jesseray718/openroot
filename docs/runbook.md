# OpenRoot Offline Toolkit — Runbook

This playbook gives **copy-paste commands** for common ops situations.
No coding knowledge required.

---

## Bootstrap (first time)

```bash
bash scripts/offline_bootstrap.sh
```

That's it.  All directories and a default `config.json` are created automatically.

---

## Daily offline workflow

```bash
# Check state
python3 -m offline.cli status

# Add a task to the local queue
python3 -m offline.cli work --type note --payload '{"text":"investigate aerocement mix"}' --urgency 3 --impact 5

# Check again
python3 -m offline.cli status
```

---

## Syncing when back online

```bash
# If you have a sync endpoint set in .env or config.json
python3 -m offline.cli sync
```

If `OFFLINE_SYNC_ENDPOINT` is empty the command is a no-op and will list
what is queued without modifying anything.

---

## Recovering from a failed sync

1. Run `python3 -m offline.cli status` – look at the `failed` count.
2. The failed entries remain in `~/.openroot/offline/queue.jsonl`.
3. Fix the underlying issue (network, endpoint URL, auth).
4. Run `python3 -m offline.cli sync` again.
   - Entries with `status=failed` are **not** retried automatically – open
     `~/.openroot/offline/queue.jsonl` in a text editor, change `"status":"failed"`
     back to `"status":"pending"`, save, then re-run `sync`.

---

## Safe purge steps

```bash
# Step 1 – see what would be purged (dry-run, no --confirm)
python3 -m offline.cli purge

# Step 2 – actually purge (irreversible)
python3 -m offline.cli purge --confirm
```

Purge only affects records that have been soft-deleted **and** whose
retention window has expired (`soft_delete_retention_days` in config).

---

## Troubleshooting

### "Data directory missing" from doctor

```bash
python3 -m offline.cli init
```

### "No module named offline"

Make sure you are running from the repository root:

```bash
cd /path/to/openroot
python3 -m offline.cli status
```

Or activate the virtual environment first:

```bash
source .venv/bin/activate
python3 -m offline.cli status
```

### Corrupt queue or dedup file

The JSONL queue and JSON dedup index are plain text files.
Back them up first:

```bash
cp ~/.openroot/offline/queue.jsonl ~/.openroot/offline/queue.jsonl.bak
cp ~/.openroot/offline/dedup_index.json ~/.openroot/offline/dedup_index.json.bak
```

Then delete the corrupt file and re-run `offline:init` to create a fresh one.

### High CPU / throttling

`offline:status` shows current pressure.  If state is `high` the toolkit
automatically reduces concurrency to 1 to protect your system.
This is normal behaviour – just wait for load to drop.

---

## Config reference (quick)

| Setting | Default | What it does |
|---|---|---|
| `OFFLINE_DATA_DIR` | `~/.openroot/offline` | Where queue/dedup/lifecycle files live |
| `OFFLINE_SOFT_DELETE_RETENTION_DAYS` | 30 | Days before soft-deleted records become purge-eligible |
| `OFFLINE_PRIORITY_WEIGHT_URGENCY` | 1.0 | Multiplier on urgency in priority score |
| `OFFLINE_PRIORITY_WEIGHT_IMPACT` | 1.0 | Multiplier on impact in priority score |
| `OFFLINE_THERMAL_CPU_HIGH` | 80.0 | CPU % at which concurrency drops to 1 |
| `OFFLINE_THERMAL_CPU_LOW` | 40.0 | CPU % below which full concurrency is restored |
| `OFFLINE_THERMAL_MAX_CONCURRENCY` | 4 | Maximum parallel workers |
| `OFFLINE_SYNC_ENDPOINT` | *(empty)* | Remote URL for queue replay; leave empty for offline-only |
