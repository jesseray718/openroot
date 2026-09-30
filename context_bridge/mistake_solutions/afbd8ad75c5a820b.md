---
id: afbd8ad75c5a820b
ts: 2026-09-27 23:07:38
type: mistake-solution
status: solved
agape_score: high
---
# Mistake afbd8ad75c5a820b

SHA256-shape key: afbd8ad75c5a820b

## Solution
Ctrl+C mid-paste over unstable SSH strands partial scripts. Fix: DETACH-RUNNER PATTERN — write long scripts to /tmp/<name>.sh via heredoc, gate with bash -n, then run with nohup + tee log. Allows reconnection without losing execution. Demonstrated working in fusefix3b run 2026-09-28.
