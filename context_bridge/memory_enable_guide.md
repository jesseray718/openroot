# OpenRoot Context Bridge

Generated: 2026-09-23T22:42:50
Canary: CONTEXT_GUIDE_V2_20260923

## Canonical shared context

Use the local SQLite context store for durable cross-terminal and cross-process coordination:

```bash
export SESSION_ID="window_A"

python3 ~/openroot/bin/shared_context_store.py \
  store task_key \
  '{"status":"complete","result":"example","canary":"TASK_V1"}'

python3 ~/openroot/bin/shared_context_store.py get task_key
python3 ~/openroot/bin/shared_context_store.py sessions
```

## Quote rule

At a Bash prompt, surround JSON with single quotes:

```bash
'{"key":"value","message":"double quotes are safe here"}'
```

Inside Python, use `json.dumps()` and pass the value as an argument-list element to
`subprocess.run()`. Avoid `shell=True`, `echo`, pipes, and `$(cat)` for JSON payloads.

## OpenRoot paths

- Base: `/home/jesse/openroot`
- Scripts: `/home/jesse/openroot/bin`
- Data: `/home/jesse/openroot/data`
- Context database: `/home/jesse/openroot/data/shared_context.db`
- Context bridge: `/home/jesse/openroot/context_bridge`

## Workflow boundary

- Review all changes with `git status`, `git diff --check`, and `git diff`.
- Use `CONFIRM=1` for destructive operations.
- Commit messages use OpenRoot tags such as `[ADD]`, `[FIX]`, `[CASCADE]`, and `[SEAL]`.
- Git push remains explicitly human-gated.
