#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb

echo "=== COPY EVERYTHING BELOW THIS LINE INTO THE NEW AI WINDOW ==="
echo
echo "--- WINDOW OPENER ---"
cat /data/data/com.termux/files/home/WINDOW_OPENER.md
echo
echo "--- SCRIPT PROTOCOL ---"
cat /data/data/com.termux/files/home/SCRIPT_PROTOCOL.md
echo
echo "--- LIVE STATE (fetched now from optiplex) ---"
ssh optiplex 'cd ~/openroot && echo "HEAD: $(git rev-parse --short HEAD) ($(git log -1 --format=%s | head -c 60))" && echo && cat context_bridge/RIDE_ALONG_STATE.md && echo "--- LATEST HANDOFF ---" && cat "$(ls -t context_bridge/handoff-ai-window-*.md | head -1)"'
echo
echo "=== END OF SEED — add one intent line below when pasting ==="
