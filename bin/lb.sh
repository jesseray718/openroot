#!/usr/bin/env bash
# lb.sh v2 — Lumo bridge, fully-autonomous mode with parachute
#   lb auto   : snapshot repo → run inbox.sh → on nonzero exit or failed gate, auto-revert
#   lb tail N : last N lines of latest log (paste back to Lumo)
#   lb snap   : manual snapshot |  lb undo : revert to last snapshot
# Fully autonomous EXCEPT irreversible-remote ops (push/delete/filter-repo) → human gate.
set -u
DIR=/home/jesse/lumo
IN=$DIR/inbox.sh
REPO=/home/jesse/openroot
SNAP=$DIR/last_snap.txt
mkdir -p "$DIR/logs"
TS=$(date +%Y%m%d_%H%M%S)
LOG=$DIR/logs/run-$TS.log

# Irreversible list — SHORTHENED to network-destruction only; local mutations are parachute-covered
if grep -qiE 'git push|push origin|--delete|filter-repo|gh repo delete|gh api .*DELETE|reboot|mkfs|dd if=' "$IN" 2>/dev/null; then
  echo "[held] inbox.sh touches REMOTE/IRREVERSIBLE surface — human gate, run manually: bash $IN"
  exit 1
fi

snap () {  # record HEAD + tree fingerprint; cheap, pre-every-run
  git -C "$REPO" rev-parse HEAD > "$SNAP" 2>/dev/null
  git -C "$REPO" status --porcelain | sort > "$SNAP.dirty"
  echo "[gate] snapshot: $(cat "$SNAP") · $(wc -l < "$SNAP.dirty") dirty file(s)"
}

undo () {
  if [ ! -f "$SNAP" ]; then echo "[held] no snapshot — nothing to revert"; exit 0; fi
  git -C "$REPO" reset --hard "$(cat "$SNAP")"
  # restore tracked files only; untracked debris listed, never rm-rf'd (standing rule)
  git -C "$REPO" status --porcelain | grep '^??' | cut -c4- || true
  echo "[banked] reverted to $(cat "$SNAP") — untracked leftovers listed above, clean by hand"
}

case "${1:-}" in
  auto)
    [ -f "$IN" ] || { echo "[held] no inbox.sh"; exit 1; }
    snap
    if bash "$IN" >"$LOG" 2>&1; then
      tail -n 60 "$LOG"
      echo "[banked] PASS · log: $LOG · (lb tail 200 for more)"
    else
      RC=$?
      tail -n 60 "$LOG"
      echo "[held] FAIL exit=$RC · auto-reverting"
      undo
      echo "[held] failed-state corpse preserved: $LOG"
    fi ;;
  tail) tail -n "${2:-60}" "$(ls -t $DIR/logs/run-*.log 2>/dev/null | head -1)" 2>/dev/null ;;
  snap) snap ;;
  undo) undo ;;
  *) echo "usage: lb auto | lb tail [N] | lb snap | lb undo" ;;
esac
exit 0
