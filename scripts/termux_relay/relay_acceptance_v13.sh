#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-V13
# hygiene: run this PHONE paste in a separate terminal; keep the watcher terminal running.
printf '%s\n' \
  '[held] Received V11 again; automatic watcher delivery is still unverified.' \
  '[gate] TEST=1 would submit one unique canary through the running clipboard watcher.' \
  '[gate] Default dry-run; no commit, push, deletion, or overwrite of server scripts.'

approval=
if [ "${TEST:-0}" != 1 ] && [ -t 0 ]; then
  printf '%s\n' '[gate] Type TEST=1 and press Enter to test; Enter alone leaves clipboard unchanged.'
  IFS= read -r approval || approval=
fi
if [ "${TEST:-0}" != 1 ] && [ "$approval" != 'TEST=1' ]; then
  printf '%s\n' '[held] test not authorized.' '[exit=0]'
  exit 0
fi
if ! pgrep -f 'python[^ ]* .*/relay-worker-v3-[^ ]+\.py' >/dev/null 2>&1; then
  printf '%s\n' '[held] v3 watcher absent; clipboard unchanged.' '[exit=0]'
  exit 0
fi

token=$(date -u +%Y%m%dT%H%M%SZ)-$$
name=relay_acceptance_v13_${token}.sh
target=/home/jesse/openroot/relay/$name
marker="[banked] CANARY:PPLX-RELAY-V13 token=$token execution=PASS"
body=$(printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -eu' \
  'export GIT_PAGER=cat TERM=dumb' \
  '# CANARY:PPLX-RELAY-V13' \
  "printf '%s\n' '$marker' '[exit=0]'")
if ! printf '%s\n' "$body" | bash -n >/dev/null 2>&1; then
  printf '%s\n' '[held] local payload bash-n failed.' '[exit=0]'
  exit 0
fi
hash=$(printf '%s\n' "$body" | sha256sum | awk '{print $1}')
state=/data/data/com.termux/files/home/.pplx_relay
mkdir -p "$state"
if ! termux-clipboard-get > "$state/clipboard-before-v13-$token.txt" 2>/dev/null; then
  printf '%s\n' '[held] clipboard backup failed; submission withheld.' '[exit=0]'
  exit 0
fi
wrapper=$(printf "cat > %s <<'OUTER_EOF'\n%s\nOUTER_EOF\nbash %s\n" "$target" "$body" "$target")
if ! printf '%s\n' "$wrapper" | termux-clipboard-set >/dev/null 2>&1; then
  printf '%s\n' '[held] canary publication failed.' '[exit=0]'
  exit 0
fi
printf '[banked] submitted=%s; wait without copying anything else.\n' "$name"

attempt=0
success=0
while [ "$attempt" -lt 30 ]; do
  attempt=$((attempt + 1))
  if ! current=$(termux-clipboard-get 2>/dev/null); then
    printf '%s\n' '[held] clipboard read failed; no replay.'
    break
  fi
  if printf '%s\n' "$current" | grep -Fq "script=$name" &&
     printf '%s\n' "$current" | grep -Fq "$marker" &&
     printf '%s\n' "$current" | grep -Fq "payload-sha256=$hash" &&
     printf '%s\n' "$current" | grep -Fxq '[banked] remote-exit=0'; then
    success=1
    printf '%s\n' '[banked] automatic clipboard watcher roundtrip=PASS.'
    printf '%s\n' "$current" | awk 'NR<=20 {printf "[gate] receipt: %s\n", $0}'
    printf '%s\n' '[gate] Verified report remains on clipboard; switch to chat and paste it directly.'
    break
  fi
  if [ "$current" != "$wrapper" ]; then
    printf '%s\n' '[held] unrelated clipboard change preserved; no replay.'
    break
  fi
  sleep 2
done
if [ "$success" != 1 ]; then
  printf '%s\n' '[held] automatic delivery not established; inspect watcher output; no retry.'
fi
printf '%s\n' '[exit=0]'
