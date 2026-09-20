#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# mobile_audit_trigger.sh — A15/Android Termux launcher for detached OptiPlex audits
# [canary] mobile_audit_trigger_CANARY_MARKER
set -euo pipefail
TARGET_HOST="${TARGET_HOST:-optiplex3060}"
OPTIPLEX_USER="${OPTIPLEX_USER:-jesse}"
SCRIPT_PATH="${OPTIPLEX_SCRIPT:-/home/${OPTIPLEX_USER}/openroot/bin/gh_audit_v2.sh}"
REMOTE_LOG="${OPTIPLEX_LOG:-/tmp/gh_audit_run4.log}"
say(){ printf '[%s] %s\n' "$1" "$2"; }

[ -z "${TERMUX_VERSION:-}" ] && echo "[held] not on Termux — verify TERMUX_VERSION env" || say banked "on Termux (v${TERMUX_VERSION})"
command -v ssh >/dev/null || { say held "ssh not found in PATH"; exit 1; }

echo "== initiating Tailscale SSH to ${TARGET_HOST} =="
# SSH timeout 60s, no keepalive chatter, detach remote immediately
ssh -o ConnectTimeout=60 -o ServerAliveInterval=30 "${OPTIPLEX_USER}@${TARGET_HOST}" <<'SHELL_EOF'
set -uo pipefail
HOST=$(hostname)
[ "$HOST" != "optiplex3060" ] && { echo "[held] unexpected host: $HOST"; exit 1; }
pkill -f gh_audit_v2 2>/dev/null || true
sleep 2
rm -f /tmp/gh_audit_run4.log
nohup bash /home/jesse/openroot/bin/gh_audit_v2.sh > /tmp/gh_audit_run4.log 2>&1 &
REMOTE_PID=$!
disown
sleep 8
if ps -p $REMOTE_PID >/dev/null 2>&1; then
  echo "[banked] remote PID $REMOTE_PID alive"
  echo "[banked] log: /tmp/gh_audit_run4.log"
  tail -5 /tmp/gh_audit_run4.log
else
  echo "[held] remote process died instantly — check full log:"
  cat /tmp/gh_audit_run4.log
  exit 1
fi
echo "[banked] audit detached on optiplex3060 — safe to disconnect mobile"
SHELL_EOF
echo "[banked] launcher finished"
printf '[exit=0]\n'
