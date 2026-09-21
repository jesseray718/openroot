## WINDOW CLOSE — 2026-09-21 (sealed)

### Banked
- Release: v2026.09.21-superlinear-botloop @2026-09-21T06:07:30Z
- Commits: de78767 (lesson+extractor), 59e9b7a (M6 fix) — pushed, 0 divergence
- Milestone: #7 Superlinear Infrastructure — Bot Loop & Chain (open)
- Bot: pid 32762, watching 3 mobile ledgers @5min cadence
- Chain: lessons.db live on OptiPlex; M1–M6 documented

### Pending chain entries (next window)
- M7: ssh jesse@optiplex FROM OptiPlex → Connection refused (self-ssh; use localhost to test)
- M8: LAN broken pipe mid-session (192.168.1.193) — network, not scripts

### Top priority next
1. Port REAL refinery worker (refine_next.sh + _refine_advance.py) from
   context_bridge/session-2026-09-16-*.md remnants → replace 7-line stub on
   OptiPlex, wired to refinery.db 6-state machine
2. Ingest M7/M8 into lessons.db (full mistake_sha/solution_sha/link_sha schema)
3. Verify bot survived overnight: pgrep -f bot_loop_v1.py
4. Species graph expansion (osage orange, mulberry)

### Launch line for next window
"Read context_bridge/handoff_window-close-20260921.md and
lessons/window-20260921_004746.md. Verify bot_loop survived, then port the
real refinery worker from session-2026-09-16 remnants to replace the stub."
