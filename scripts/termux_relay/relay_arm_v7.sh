#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-V7
# hygiene: authorize at the terminal; never auto-execute clipboard content in dry-run.
printf '%s\n' \
  '[banked] v6 verified exact SSH payload bytes, SHA256, syntax, and canary output.' \
  '[gate] RUN=1 EXECUTE=1 would arm the clipboard watcher for validated server scripts.' \
  '[gate] Blank input keeps dry-run; existing v1 files remain unchanged.' \
  '[gate] COMMIT=1, PUSH=1, CONFIRM=1 remain disabled.'

base=/data/data/com.termux/files/home
relay="$base/relay_v3.sh"
verify="$base/relay_verify_v6.sh"
expected=85577b88c546a8482b0f4f43c99e256ac50e417f243dd0775be23a4151ceeb6c

for artifact in "$relay" "$verify"; do
  if [ ! -f "$artifact" ] || ! bash -n "$artifact" >/dev/null 2>&1; then
    printf '[held] required artifact missing or syntax-invalid=%s\n' "$artifact"
    printf '%s\n' '[exit=0]'
    exit 0
  fi
done
actual=$(sha256sum "$relay" | awk '{print $1}')
if [ "$actual" != "$expected" ]; then
  printf '[held] v3 changed since verification; actual-sha256=%s\n' "$actual"
  printf '%s\n' '[exit=0]'
  exit 0
fi
printf '%s\n' '[banked] verified v3 hash unchanged; v3/v6 bash-n=PASS.'

if [ "${RUN:-0}" != 1 ] || [ "${EXECUTE:-0}" != 1 ]; then
  approval=
  if [ -t 0 ]; then
    printf '%s\n' '[gate] Type exactly RUN=1 EXECUTE=1 and press Enter to arm; Enter alone leaves dry-run.'
    IFS= read -r approval || approval=
  fi
  if [ "$approval" != 'RUN=1 EXECUTE=1' ]; then
    printf '%s\n' '[held] watcher not authorized; clipboard untouched.' '[exit=0]'
    exit 0
  fi
fi

printf '%s\n' \
  '[banked] operator authorized RUN=1 EXECUTE=1; transport will be rechecked before arming.' \
  '[gate] Leave this terminal running; Ctrl-C stops the watcher.' \
  '[gate] Copy only complete /home/jesse/openroot/scripts/ or relay/ wrappers; copy reports back here.'
if RUN=1 EXECUTE=1 COMMIT=0 PUSH=0 CONFIRM=0 bash "$verify"; then
  :
else
  printf '%s\n' '[held] verifier/watcher failed; no automatic restart.'
fi
printf '%s\n' '[exit=0]'
