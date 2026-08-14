#!/data/data/com.termux/files/usr/bin/bash
# Logs every Lumo/AI interaction session into git-tracked build log
LOG=~/openroot/build-log/node-zero/session-$(date '+%Y%m%d').md
mkdir -p "$(dirname "$LOG")"

echo "" >> "$LOG"
echo "## Session $(date '+%H:%M') — Lumo v2.0" >> "$LOG"
echo "" >> "$LOG"

# Auto-detect what changed since last commit
CHANGES=$(git -C ~/openroot diff --name-only HEAD 2>/dev/null)
NEW_COMMITS=$(git -C ~/openroot log --oneline -5 2>/dev/null)

echo "### Commits this session:" >> "$LOG"
echo '```' >> "$LOG"
echo "$NEW_COMMITS" >> "$LOG"
echo '```' >> "$LOG"
echo "" >> "$LOG"

if [ -n "$1" ]; then
  echo "### Input:" >> "$LOG"
  echo "$1" >> "$LOG"
  echo "" >> "$LOG"
fi

echo "### Changed files:" >> "$LOG"
echo '```' >> "$LOG"
git -C ~/openroot status --short >> "$LOG" 2>/dev/null
echo '```' >> "$LOG"
echo "" >> "$LOG"

echo "### Disk: $(df -h ~ | awk 'NR==2{print $4}') free" >> "$LOG"
echo "" >> "$LOG"

git -C ~/openroot add "$LOG"
git -C ~/openroot commit -m "Auto-session-log $(date '+%H:%M')" 2>/dev/null
git -C ~/openroot push origin main 2>/dev/null

echo "
Logged: $LOG"
