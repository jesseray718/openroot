#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-V8
# hygiene: read-only payload; watcher handles transport and installation.
printf '%s\n' \
  '[gate] End-to-end test: clipboard wrapper -> extracted payload -> SSH -> server -> clipboard report.' \
  '[gate] COMMIT=1 would authorize a reviewed commit; PUSH=1 would authorize guarded push; neither performed.' \
  '[gate] CONFIRM=1 would authorize identified destructive changes; none requested.'

if [ "$(id -un)" != jesse ] || [ "$(hostname -s)" != optiplex3060 ]; then
  printf '%s\n' '[held] unexpected execution host or user; server canary withheld.' '[exit=0]'
  exit 0
fi
self=/home/jesse/openroot/relay/relay_canary_v8.sh
if ! bash -n "$self" >/dev/null 2>&1; then
  printf '%s\n' '[held] installed canary bash-n failed.' '[exit=0]'
  exit 0
fi
printf '[banked] server=%s user=%s\n' "$(hostname -s)" "$(id -un)"
printf '[banked] installed-canary bytes=%s sha256=%s\n' \
  "$(wc -c < "$self" | tr -d ' ')" \
  "$(sha256sum "$self" | awk '{print $1}')"
printf '[banked] repo-head=%s\n' "$(git -C /home/jesse/openroot rev-parse --short HEAD)"
printf '%s\n' \
  '[banked] CANARY:PPLX-RELAY-V8 remote execution=PASS.' \
  '[gate] Return the clipboard report containing remote-exit=0 to verify the complete round trip.' \
  '[exit=0]'
