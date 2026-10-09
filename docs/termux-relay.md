# Termux / OptiPlex clipboard relay

CANARY:PPLX-RELAY-V15

The operator-approved v3 watcher passed automatic clipboard acceptance on
2026-10-09: payload SHA256
d9fcb73bc38f81f000a2aef562e7d19287c0086d7ad130bd77e2ee0065602e88,
remote-exit=0, and wrapper-to-report replacement verified by v13.

## Deployment

Run these four shell artifacts on Termux, not Ubuntu. Copy the files from
scripts/termux_relay/ to /data/data/com.termux/files/home/ with their basenames
unchanged. Leave the previous v1 watcher stopped.

Run:
bash /data/data/com.termux/files/home/relay_arm_v7.sh

At its terminal gate, enter RUN=1 EXECUTE=1. Keep that terminal running.
In a separate Termux terminal run relay_acceptance_v13.sh and enter TEST=1
to perform controlled acceptance.

Copy a complete server scripts/ or relay/ heredoc wrapper to the clipboard.
Do not paste that server wrapper into the phone shell. Wait for the report,
then paste the clipboard directly into the pairing chat.

## Safety and limitations

This is a trusted-operator execution channel, not a sandbox. Once armed,
validated clipboard payloads can run arbitrary commands as the server user.
Script paths and syntax are checked; behavior is not authorized per command.
Different existing destinations require CONFIRM=1; symlinks are refused.
Clipboard changes during execution are preserved; reports are archived under
/data/data/com.termux/files/home/.pplx_relay/. Retrieve archived reports rather
than replaying scripts after uncertain outcomes.

Known debt: no durable exactly-once replay ledger, no cross-process execution
lock in v3, a read/write clipboard race remains possible, remote output is
captured in memory, and staging files accumulate. Timeout does not prove
remote execution stopped. Start only one watcher and stop with Ctrl-C.
The launcher screens existing watchers but is not an atomic lock.

## Release gates

Only explicit release paths are committed; unrelated ledger edits and
generated canaries are excluded. push_guard.py defaults to dry-run.
Authorized push:
PUSH=1 python3 /home/jesse/openroot/bin/push_guard.py --push

The guard verifies main, an empty index, fresh remote ancestry, linear outgoing
history, prohibited paths, tracked deletions, and blobs above 5 MiB.
It never force-pushes. Dirty unstaged files are not included in a push.

Mistake classes encountered: SSH stdin omission, wrong-host absolute-path paste,
syntax-check mistaken for patch verification, missing intermediate artifact,
stale clipboard report, and preserved concurrent clipboard change.
