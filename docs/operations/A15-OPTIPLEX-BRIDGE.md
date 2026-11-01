# A15 ↔ OptiPlex Blueprint Bridge

The bridge syncs only `data/wealth_retention/` and
`bin/ewaste_manager.py`. It does not publish to GitHub, run commands on the
hub, or copy unrelated repository state.

Configure the private `.env` file with:

```dotenv
OPENROOT_HUB_HOST=hub-hostname-or-address
OPENROOT_HUB_USER=remote-user
OPENROOT_HUB_PATH=~/openroot
```

SSH authentication must already be configured through the local SSH agent or
SSH config. Do not put private-key contents in `.env`. The remote destination
directory must exist and be writable by the configured user.

Run `bin/sync_to_optiplex.sh` to inspect an `rsync --dry-run`; it is the
default and does not transfer files. Add `--apply` only when an operator
intends to transfer the listed files. Both modes create a SHA-256 chained,
deduplicated receipt at `data/bridge_receipts.jsonl`. No live sync is run by
the repository tests.

## E-waste pickup slots

Run `python3 bin/ewaste_manager.py YYYY-MM-DD HH:MM` to reserve a slot from
`data/ewaste/slots.json`. A reservation is idempotent and emits a hash-sealed
record in `data/ewaste/newton_chain.jsonl`. The slot file is an availability
projection; a retry repairs it from an existing booking receipt if a prior
process stopped between receipt and projection writes.

This automates slot reservation only. Route optimization and collection
dispatch remain gated on verified pickup locations, capacity, and operator
constraints; the current repository data does not provide those inputs.
