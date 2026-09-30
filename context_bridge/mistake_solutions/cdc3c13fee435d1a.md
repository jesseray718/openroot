---
id: cdc3c13fee435d1a
ts: 2026-09-30 01:21:13
type: mistake-solution
status: solved
agape_score: high
---
# Mistake cdc3c13fee435d1a

SHA256-shape key: cdc3c13fee435d1a

## Solution
launcher line-join mangle + quoted "2>&1" treated as filename broke bot launch under set -eu — my bad double-nohup hack; fix: plain single redirect line, launchers capped under 20 lines
