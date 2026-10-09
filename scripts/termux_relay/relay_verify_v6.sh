#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-V6
# hygiene: self-contained verification; no dependency on missing v4 or v5.
printf '%s\n' \
  '[gate] Missing v4 bypassed; this artifact contains the complete transport test.' \
  '[gate] Default: read-only smoke test; no persistent remote changes or clipboard changes.' \
  '[gate] RUN=1 EXECUTE=1 would start existing v3 after transport verification.' \
  '[gate] COMMIT=1, PUSH=1, CONFIRM=1 unused; existing files preserved.'

relay=/data/data/com.termux/files/home/relay_v3.sh
if [ ! -f "$relay" ] || ! bash -n "$relay" >/dev/null 2>&1; then
  printf '%s\n' '[held] v3 missing or bash-n failed.' '[exit=0]'
  exit 0
fi
printf '[banked] v3 bash-n=PASS sha256=%s\n' "$(sha256sum "$relay" | awk '{print $1}')"

payload=$(cat <<'INNER_CANARY'
#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-TRANSPORT-V6
printf '%s\n' '[banked] explicit-stdin canary=PASS'
INNER_CANARY
)
if ! printf '%s\n' "$payload" | bash -n >/dev/null 2>&1; then
  printf '%s\n' '[held] local payload syntax failed.' '[exit=0]'
  exit 0
fi
expected_sha=$(printf '%s\n' "$payload" | sha256sum | awk '{print $1}')
expected_bytes=$(printf '%s\n' "$payload" | wc -c | tr -d ' ')

if report=$(
  printf '%s\n' "$payload" |
    ssh -T -o BatchMode=yes -o ConnectTimeout=10 \
      -o ServerAliveInterval=10 -o ServerAliveCountMax=2 \
      jesse@100.122.169.43 \
      'set -eu
export GIT_PAGER=cat TERM=dumb
tmp=$(mktemp /tmp/pplx-relay-v6-XXXXXXXX)
trap '\''rm -f -- "$tmp"'\'' EXIT
cat > "$tmp"
test -s "$tmp"
bash -n "$tmp"
printf "[banked] remote-sha256=%s\n" "$(sha256sum "$tmp" | awk '\''{print $1}'\'')"
printf "[banked] remote-bytes=%s\n" "$(wc -c < "$tmp" | tr -d '\'' '\'')"
bash "$tmp"' 2>/dev/null
); then
  expected=$(printf '[banked] remote-sha256=%s\n[banked] remote-bytes=%s\n[banked] explicit-stdin canary=PASS' \
    "$expected_sha" "$expected_bytes")
  if [ "$report" != "$expected" ]; then
    printf '%s\n' '[held] remote response differs from exact expected bytes/hash/output.'
    printf '%s\n' "$report" | awk 'NR<=8 {printf "[held] received: %s\n", $0}'
    printf '%s\n' '[exit=0]'
    exit 0
  fi
  printf '%s\n' "$report"
  printf '%s\n' '[banked] actual SSH stdin transport=PASS; isolated remote temporary file cleaned.'
else
  printf '%s\n' '[held] transport failed; watcher not started; no automatic retry.' '[exit=0]'
  exit 0
fi

old_watchers=$(pgrep -f '(^|[ /])pplx_relay_v1\.sh([ ]|$)' 2>/dev/null || true)
new_watchers=$(pgrep -f 'python[^ ]* .*/relay-worker-v3-[^ ]+\.py' 2>/dev/null || true)
if [ -n "$old_watchers$new_watchers" ]; then
  printf '[held] existing watcher PID(s)=%s; duplicate launch withheld.\n' \
    "$(printf '%s\n%s\n' "$old_watchers" "$new_watchers" | tr '\n' ',' | cut -c1-120)"
elif [ "${RUN:-0}" = 1 ] && [ "${EXECUTE:-0}" = 1 ]; then
  printf '%s\n' '[banked] transport verified; launching v3 watcher with explicit authorization.'
  if RUN=1 EXECUTE=1 bash "$relay"; then
    :
  else
    printf '%s\n' '[held] watcher returned nonzero; no automatic restart.'
  fi
else
  printf '%s\n' \
    '[held] transport verified; watcher remains stopped by default.' \
    '[gate] Authorized launch: RUN=1 EXECUTE=1 bash /data/data/com.termux/files/home/relay_verify_v6.sh'
fi
printf '%s\n' '[exit=0]'
