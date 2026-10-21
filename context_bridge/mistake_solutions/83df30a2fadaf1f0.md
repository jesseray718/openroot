---
id: 83df30a2fadaf1f0
ts: 2026-09-27 22:16:51
type: mistake-solution
status: solved
agape_score: high
---
# Mistake 83df30a2fadaf1f0

SHA256-shape key: 83df30a2fadaf1f0

## Solution
heredoc redirect to a path whose parent directory does not exist fails with 'No such file or directory' before the file is ever opened. Pattern fix: mkdir -p <parent-dir> must precede any cat > file heredoc to a new subtree; grep pasted docs for claimed-tracked paths (infra/systemd/) before assuming they exist — verify with ls, not prose. Class: PARENT-DIR-MISSING, do not requeue.
