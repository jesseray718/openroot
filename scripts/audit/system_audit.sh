#!/usr/bin/env bash
# =====================================================================
# system_audit.sh — READ-ONLY full-system audit, openroot node
# Output : ~/openroot/reports/audit-<timestamp>/AUDIT_SUMMARY.md
# Safety : no mutations. git via --no-optional-locks, sqlite mode=ro,
#          secret files flagged but never read, output token-redacted.
# Runtime: several minutes (disk walk is the slow part).
# =====================================================================
set -u
TS=$(date +%Y%m%d-%H%M%S)
AUD="$HOME/openroot/reports/audit-$TS"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$AUD"
SHELL_SECS="$AUD/10_shell_audit.txt"
PY_SECS="$AUD/20_data_audit.md"
SUMMARY="$AUD/AUDIT_SUMMARY.md"

redact() {
  sed -E \
    -e 's/gh[pousr]_[A-Za-z0-9]{16,}/<GH_TOKEN_REDACTED>/g' \
    -e 's/github_pat_[A-Za-z0-9_]{16,}/<GH_PAT_REDACTED>/g' \
    -e 's/sk-[A-Za-z0-9]{16,}/<API_KEY_REDACTED>/g' \
    -e 's/AKIA[0-9A-Z]{12,}/<AWS_KEY_REDACTED>/g' \
    -e 's/xox[baprs]-[A-Za-z0-9-]+/<SLACK_REDACTED>/g' \
    -e 's/([Bb]earer) +[A-Za-z0-9._-]{12,}/\1 <TOKEN_REDACTED>/g' \
    -e 's#https://[A-Za-z0-9._-]+@#https://<CREDS>@#g' \
    -e '/-----BEGIN [A-Z ]*PRIVATE KEY-----/,/-----END [A-Z ]*PRIVATE KEY-----/d'
}
exe()  { bash -c "$1" 2>&1 | redact; return 0; }
sec()  { printf '\n\n===== %s =====\n' "$*"; }
note() { echo "[audit] $*" >&2; }

note "audit $TS starting -> $AUD"

{
sec "0. AUDIT META"
echo "Started : $(date -Is)"
echo "Host    : $(hostname)"
echo "Mode    : read-only"

sec "1. HOST & HARDWARE"
exe 'hostnamectl 2>/dev/null | grep -E "hostname|Chassis|Operating System|Kernel" || uname -a'
exe 'uptime'
exe 'lscpu 2>/dev/null | grep -E "^CPU\(s\)|Model name|Thread|Core\("'
exe 'free -h'
exe 'lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT 2>/dev/null'

sec "2. FILESYSTEM USAGE"
exe 'df -h -x tmpfs -x devtmpfs -x squashfs'

note "walking ~ for du (slowest step)"
sec "3. HOME FOOTPRINT (top 35 by size)"
exe 'du -xh --max-depth=1 "$HOME" 2>/dev/null | sort -rh | head -35'

sec "4. SERVICES & SCHEDULERS"
exe 'echo "--- newton-daemon (system scope) ---"
     systemctl is-active newton-daemon.service 2>&1
     systemctl is-enabled newton-daemon.service 2>&1'
exe 'systemctl show newton-daemon.service -p ActiveState,SubState,NRestarts,ExecMainPID,ExecMainStartTimestamp,ExecStart --no-pager 2>/dev/null'
exe 'echo "--- newton-daemon (user scope) ---"
     systemctl --user is-active newton-daemon.service 2>&1'
exe 'echo "--- running system services ---"
     systemctl list-units --type=service --state=running --no-pager | head -30'
exe 'echo "--- running user services ---"
     systemctl --user list-units --type=service --state=running --no-pager 2>/dev/null | head -25'
exe 'echo "--- self-hosted actions runner ---"
     pgrep -af "Runner.Listener|actions-runner" | head -5'
exe 'echo "--- cron ---"
     crontab -l 2>&1 | head -20'

sec "5. NEWTON DAEMON LOG (tail)"
exe 'journalctl -u newton-daemon.service -n 30 --no-pager 2>&1 | tail -35'
exe 'journalctl --user -u newton-daemon.service -n 30 --no-pager 2>&1 | tail -35'

sec "6. PROCESSES & LIVE SCRIPT PATHS"
exe 'ps aux --sort=-%mem | head -14'
exe 'pgrep -af python | head -15'
exe 'pgrep -af "bot_loop|handoff|launch_ladder|newton|lumo|a1_core|tinycrew|governor|context_bridge|openclaw" | head -20'
exe 'find "$HOME/openroot" -maxdepth 3 \( -name "handoff_manager.py" -o -name "bot_loop_v1.py" -o -name "launch_ladder_v1.py" -o -name "a1_core_v1.py" \) 2>/dev/null'
if [ -f "$HOME/openroot/bot_loop.pid" ]; then
  exe 'P=$(cat "$HOME/openroot/bot_loop.pid"); echo "bot_loop.pid -> $P"; ps -p "$P" -o pid,etime,cmd 2>/dev/null || echo "PID $P IS NOT RUNNING"'
fi

sec "7. NETWORK LISTENERS & LOCAL LLAMA"
exe 'ss -tlnp 2>/dev/null | head -25'
exe 'R=$(curl -s --max-time 3 http://127.0.0.1:8080/api/tags); if [ -n "$R" ]; then echo "$R" | head -c 600; else echo "NO RESPONSE on :8080"; fi; echo'
exe 'R=$(curl -s --max-time 3 http://127.0.0.1:11434/api/tags); if [ -n "$R" ]; then echo "$R" | head -c 600; else echo "NO RESPONSE on :11434"; fi; echo'
exe 'command -v ollama >/dev/null 2>&1 && ollama list 2>&1 | head -10 || echo "ollama CLI not in PATH"'

sec "8. OPENROOT GIT STATE (jesseray718/openroot)"
exe 'cd "$HOME/openroot" && git --no-optional-locks status -sb | head -5
     echo "porcelain entries: $(git --no-optional-locks status --porcelain | wc -l)"'
exe 'cd "$HOME/openroot" && git --no-optional-locks status --porcelain | head -25'
exe 'cd "$HOME/openroot" && git remote -v'
exe 'cd "$HOME/openroot" && git --no-optional-locks log --oneline --decorate -8'
exe 'cd "$HOME/openroot" && git --no-optional-locks branch -vv | head -12'
exe 'cd "$HOME/openroot" && git rev-list --left-right --count @{upstream}...HEAD 2>&1 | head -2'
exe 'cd "$HOME/openroot" && git count-objects -vH'
exe 'cd "$HOME/openroot" && echo "--- .gitignore ---" && cat .gitignore'
exe 'cd "$HOME/openroot" && for f in knowledge_index.db openroot_vector.db node_modules data/fts_index.db reports; do
       if git check-ignore -q "$f" 2>/dev/null; then echo "IGNORED     : $f"; else echo "NOT IGNORED : $f"; fi
     done'
exe 'command -v gh >/dev/null 2>&1 && { gh auth status 2>&1 | head -6; gh repo view jesseray718/openroot --json name,pushedAt,diskUsage,defaultBranchRef 2>&1 | head -10; } || echo "gh CLI not installed or not authed"'

sec "9. REPO SPRAWL MAP (git metadata; sizes in section 3)"
for d in "$HOME"/openroot* "$HOME"/github* "$HOME"/jesseray718*; do
  [ -e "$d" ] || continue
  if [ -d "$d/.git" ] || { [ -f "$d/HEAD" ] && [ -d "$d/objects" ]; }; then
    br=$(git --no-optional-locks -C "$d" branch --show-current 2>/dev/null)
    lc=$(git --no-optional-locks -C "$d" log -1 --format='%ci' 2>/dev/null)
    or=$(git --no-optional-locks -C "$d" remote get-url origin 2>/dev/null)
    echo "$(basename "$d") | branch=${br:-?} | last=${lc:-none} | origin=${or:-none}" | redact
  fi
done

sec "10. SENSITIVE FILE POSTURE (flagged only — contents never read)"
for f in "$HOME/.api_keys" "$HOME/.git-credentials" \
         "$HOME/github-recovery-codes.txt" "$HOME/openroot/.env.local" \
         "$HOME/kai-settings.json" "$HOME/.bash_history"; do
  [ -e "$f" ] && stat -c '%A  %s bytes  %n' "$f" | redact
done
exe 'stat -c "%A  %s bytes  %n" "$HOME/how-user jesse -p Linger" 2>/dev/null || echo "odd-named capture file not present"'
exe 'ls -la "$HOME/.ssh" 2>/dev/null | head -12'
echo "Rule: anything secret above with group/world read bits needs chmod 600."

sec "11. LIVE-STATE FILES (recent mtimes = active automation)"
exe 'ls -la "$HOME/openroot/data_bot_state.json" "$HOME/.openroot_tap.tsv" "$HOME/openroot/bot_loop.pid" 2>/dev/null'
exe 'head -5 "$HOME/.openroot_tap.tsv" 2>/dev/null | cut -c1-160'

sec "12. DATABASE FILES ON DISK"
exe 'ls -la "$HOME/openroot/data" 2>/dev/null | head -30'
exe 'ls -la "$HOME/openroot"/*.db "$HOME/openroot"/*-journal "$HOME/openroot"/*-wal 2>/dev/null'
exe 'command -v sqlite3 >/dev/null 2>&1 && sqlite3 --version || echo "sqlite3 CLI absent"'
} > "$SHELL_SECS" 2>&1

note "shell sections done; running python data audit"
PY="$HOME/openroot/venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"
"$PY" "$SCRIPT_DIR/audit_detail.py" > "$PY_SECS" 2>&1 \
  || echo "PYTHON AUDIT FAILED — see errors above" >> "$PY_SECS"

{
  echo "# OPENROOT NODE AUDIT — $TS"
  echo
  echo "Read-only. Tokens redacted. Secret-file contents not read."
  cat "$SHELL_SECS"
  cat "$PY_SECS"
} > "$SUMMARY"

BYTES=$(wc -c < "$SUMMARY")
note "done"
echo
echo "==================================================================="
echo " AUDIT COMPLETE"
echo " Report : $SUMMARY"
echo " Size   : $BYTES bytes"
if [ "$BYTES" -gt 60000 ]; then
  echo " Large report — paste back in chunks, or start with:"
  echo "   sed -n '1,220p' \"$SUMMARY\""
fi
echo "==================================================================="
