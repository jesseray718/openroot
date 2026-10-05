#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
cd /home/jesse/openroot
CANARY=CANARY:OPENROOT-AUTH-SMOKE-V1; echo "[$CANARY] $(date -u +%FT%TZ)"

# [STAGE 0] finish esbuild approval (was cut off mid-command)
npm install-scripts approve esbuild || echo "[held] esbuild approve returned nonzero — inspect manually"

# [STAGE 1] audit snapshot (NO fix --force; next vuln is deliberate hold at 14.2.35)
AUDIT=$(npm audit --json 2>/dev/null || true)
CRIT=$(echo "$AUDIT" | grep -c '"severity": *"critical"' || true)
echo "[gate] audit critical-severity lines: $CRIT (expected 1 = next@14.2.35 hold, documented)"

# [STAGE 2] JWT_SECRET must exist locally; rotate since tokens appeared in pasted logs
if grep -qs '^JWT_SECRET=' .env.local; then echo "[held] JWT_SECRET present — rotate it now (real tokens pasted in session log)"; else echo "[held] MISSING JWT_SECRET in .env.local — middleware falls back to hardcoded secret"; fi

# [STAGE 3] dev server up?
if curl -s -o /dev/null --max-time 3 http://localhost:3000/; then
  echo "[banked] dev server already on :3000"
else
  nohup npm run dev > /home/jesse/openroot/logs/dev_$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 &
  echo "[held] dev server starting — waiting"
fi
for i in $(seq 1 30); do curl -s -o /dev/null http://localhost:3000/ && break; sleep 1; done
curl -s -o /dev/null --max-time 3 http://localhost:3000/ || { echo "[gate] server never came up — abort"; exit 1; }

# [STAGE 4] full smoke: register unique user -> login -> capture token -> protected route
TS=$(date +%s); EMAIL="smoke_${TS}@openroot.dev"; PASS="smoketest123"
REG=$(curl -s -o /tmp/reg.json -w '%{http_code}' -X POST http://localhost:3000/api/auth/register -H 'Content-Type: application/json' -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASS}\"}")
echo "[STAGE 4] register=$REG"
LOGIN_HDRS=$(mktemp)
LOGIN=$(curl -s -o /tmp/login.json -D "$LOGIN_HDRS" -w '%{http_code}' -X POST http://localhost:3000/api/auth/login -H 'Content-Type: application/json' -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASS}\"}")
TOKEN=$(grep -i '^set-cookie: token=' "$LOGIN_HDRS" | sed -n 's/[Ss]et-[Cc]ookie: *token=\([^;]*\).*/\1/p' | head -n1)
rm -f "$LOGIN_HDRS"
echo "[STAGE 4] login=$LOGIN token_len=${#TOKEN}"
[ -n "$TOKEN" ] || { echo "[gate] no token captured — abort"; exit 1; }

NOAUTH=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/dashboard)
WITHAUTH=$(curl -s -o /dev/null -w '%{http_code}' -H "Cookie: token=${TOKEN}" http://localhost:3000/dashboard)
BADAUTH=$(curl -s -o /dev/null -w '%{http_code}' -H "Cookie: token=garbage.jwt.sig" http://localhost:3000/dashboard)
echo "[STAGE 4] dashboard: noauth=$NOAUTH withauth=$WITHAUTH badtoken=$BADAUTH (want 307/200/307)"
[ "$WITHAUTH" = "200" ] || { echo "[gate] WITHAUTH != 200 — middleware or JWT verify broken"; exit 1; }

# [STAGE 5] stage untracked work, show what would be committed
git add -N middleware.ts app/components/AuthCard.tsx app/register/page.tsx app/login/page.tsx app/dashboard/page.tsx 2>/dev/null || git add -N .
echo "--- git diff --stat (untracked now visible via add -N) ---"
git diff --stat
git add middleware.ts app/components app/register app/login app/dashboard
if [ "${CONFIRM:-0}" = "1" ]; then
  git commit -m "feat(auth): UI pages + jose middleware protecting /dashboard; smoke-tested register/login/token redirect"
  echo "[banked] commit sealed"
else
  echo "[gate] dry-run: re-run with CONFIRM=1 to commit ($(git diff --cached --stat | tail -n1))"
fi
echo "[banked] smoke_auth_v1 complete — artifacts: /tmp/reg.json /tmp/login.json"
echo "[exit=0]"
