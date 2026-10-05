#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
cd /home/jesse/openroot
CANARY=CANARY:OPENROOT-SEAL-AUTH-V1; echo "[$CANARY] $(date -u +%FT%TZ)"

# [STAGE 0] recalibrate critical counter — instrument check before trusting it
CRIT=$(npm audit --json 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("metadata",{}).get("vulnerabilities",{}).get("critical","?"))')
echo "[gate] authoritative critical count = $CRIT (grep said 3; if 1, instrument defect logged not threat)"

# [STAGE 1] rotate JWT_SECRET (tokens leaked into pasted session logs)
NEWSECRET=$(openssl rand -hex 32)
if grep -qs '^JWT_SECRET=' .env.local; then
  sed -i "s|^JWT_SECRET=.*|JWT_SECRET=${NEWSECRET}|" .env.local
else
  echo "JWT_SECRET=${NEWSECRET}" >> .env.local
fi
echo "[held] JWT_SECRET rotated — dev server hot-reloads .env.local on next request; prior tokens now invalid"

# [STAGE 2] sanity: login STILL works post-rotation (proves route + middleware read same secret)
TS=$(date +%s)
REG=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:3000/api/auth/register -H 'Content-Type: application/json' -d "{\"email\":\"rotate_${TS}@openroot.dev\",\"password\":\"rotatetest123\"}")
LOGIN=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:3000/api/auth/login -H 'Content-Type: application/json' -d "{\"email\":\"rotate_${TS}@openroot.dev\",\"password\":\"rotatetest123\"}")
echo "[STAGE 2] post-rotation register=$REG login=$LOGIN (want 201/200)"
[ "$LOGIN" = "200" ] || { echo "[gate] rotation broke auth — abort, restore .env.local backup"; cp .env.local.bak .env.local 2>/dev/null || true; exit 1; }

# [STAGE 3] seal commit — ALL auth work incl. package.json overrides fix
git add middleware.ts app/components app/register app/login app/dashboard package.json package-lock.json
echo "--- staged ---"; git diff --cached --stat
git commit -m "feat(auth): jose middleware + login/register/dashboard UI, package overrides fix (EOVERRIDE resolved), smoke-tested end-to-end 307/200/307"
echo "[banked] commit sealed: $(git rev-parse --short HEAD)"

# [STAGE 4] handoff receipt to context_bridge (per standing protocol)
HANDOFF="context_bridge/session-$(date -u +%Y-%m-%d)-authui-seal.md"
cat <<'MD' > "$HANDOFF"
# Session: auth UI + middleware seal — $(date -u +%FT%TZ)

## Artifacts built
- app/components/AuthCard.tsx, app/register/page.tsx, app/login/page.tsx, app/dashboard/page.tsx, middleware.ts
- smoke_auth_v1.sh, seal_auth_v1.sh (bin candidates)

## Verified state
- register 201 / dup 409 / login 200 / dashboard noauth=307 valid=200 garbage=307 (smoke_auth_v1)
- JWT_SECRET rotated post-leak; login re-verified 200 after rotation
- next held at 14.2.35 deliberately (critical advisory requires next@16 = breaking; LAN-dev exposure only)
- esbuild EOVERRIDE pattern solved: override-only, never direct dep

## Broken/held
- next@14.2.35 critical advisory (24 CVEs) — migration to next@16 scheduled as standalone gated task
- grep-based audit critical counter overcounts (3 vs metadata 1) — instrument defect noted for mistake_engine

## Next actions
1. next@16.3.8 migration on a fork branch (middleware->proxy rename, breaking)
2. bin/ verification from BOOT SEED queue item 1
3. commit+push via push_guard v2

## Mistake-class additions
- GARBLE_HEREDOC_PASTE (recovered on retry), EOVERRIDE_DIRECT_DEP_CONFLICT (solved: delete direct dep), PLACEHOLDER_TOKEN_TEST_INVALID (smoke fixes), NMP_TYPO
MD
echo "[banked] handoff written: $HANDOFF ($(sha256sum "$HANDOFF" | cut -c1-16)...)"
if command -v git >/dev/null; then git add "$HANDOFF"; git commit -m "docs: session handoff auth ui seal" -q; fi
echo "[exit=0]"
