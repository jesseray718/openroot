#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-V10
# OPERATOR: Copy this entire block; do not paste it into the watcher terminal.
# OPERATOR: Leave the clipboard unchanged for 10 seconds, then paste it into this chat.
# hygiene: read-only verification; no commits, pushes, or tracked-content changes.
printf '%s\n' \
  '[banked] V8 proved server execution and archived report delivery; this tests clipboard delivery.' \
  '[gate] COMMIT=1, PUSH=1, CONFIRM=1 unused; no repository mutation.'

if [ "$(id -un)" != jesse ] || [ "$(hostname -s)" != optiplex3060 ]; then
  printf '%s\n' '[held] wrong execution host or user.' '[exit=0]'
  exit 0
fi

prior=/home/jesse/openroot/relay/relay_canary_v8.sh
expected=07b0908ce68ad6c0e067ed979f72a75d8abb7d471aa87177c9dc724db7b9db01
if [ ! -f "$prior" ]; then
  printf '%s\n' '[held] prior verified canary missing.' '[exit=0]'
  exit 0
fi
actual=$(sha256sum "$prior" | awk '{print $1}')
if [ "$actual" != "$expected" ]; then
  printf '[held] prior canary changed sha256=%s\n' "$actual"
  printf '%s\n' '[exit=0]'
  exit 0
fi

self=/home/jesse/openroot/relay/relay_clipboard_canary_v10.sh
if ! bash -n "$self" >/dev/null 2>&1; then
  printf '%s\n' '[held] installed v10 syntax invalid.' '[exit=0]'
  exit 0
fi
printf '[banked] server=%s user=%s\n' "$(hostname -s)" "$(id -un)"
printf '[banked] v10-sha256=%s\n' "$(sha256sum "$self" | awk '{print $1}')"
printf '%s\n' \
  '[banked] prior V8 artifact hash=PASS; installed V10 bash-n=PASS.' \
  '[banked] CANARY:PPLX-RELAY-V10 remote execution=PASS.' \
  '[gate] Clipboard receipt is verified only when this report returns to the chat with remote-exit=0.' \
  '[exit=0]'
