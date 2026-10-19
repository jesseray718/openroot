#!/usr/bin/env bash
# secret_scrub_env_local_v1.sh — purge leaked JWT_SECRET from openroot
# Usage: dry-run default; CONFIRM=1 for full purge; ROTATED=<newhex> optional
set -eu
export GIT_PAGER=cat TERM=dumb PYTHONDONTWRITEBYTECODE=1
cd /home/jesse/openroot
CANARY="CANARY:OPENROOT-JWT-SCRUB-V1"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG=/home/jesse/openroot/logs/secret_scrub_env_local_${STAMP}.log
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1

echo "[gate] $CANARY $(date -u +%FT%TZ)"
SECRET="REDACTED_POST_SCRUB_20261018"  # literal removed 2026-10-18, value dead since rotation

echo "=== [STAGE 0] preflight ==="
echo "HEAD: $(git rev-parse HEAD)"
echo "unpushed: $(git rev-list --count @{u}..HEAD 2>/dev/null || echo '?')"
command -v git-filter-repo >/dev/null && FILTER=git-filter-repo || FILTER=""
echo "filter tool: ${FILTER:-MISSING}"

# Enumerate affected blobs
BLOBS=$(git rev-list --objects --all \
  | git cat-file --batch-check='%(objectname) %(objecttype) %(rest)' \
  | awk '$2=="blob"' \
  | while read -r sha rest; do
      git cat-file blob "$sha" 2>/dev/null | grep -qF "$SECRET" && echo "$sha $rest"
    done)
echo "affected blobs:"
echo "$BLOBS" | sed '/^$/d'

COMMIT_HITS=$(git log --all --oneline -S"$SECRET")
echo "affected commits:"
echo "$COMMIT_HITS" | sed '/^$/d'
echo
echo "commit count: $(echo "$COMMIT_HITS" | grep -c . || echo 0)"

# Receipt-safe check: does v1.0/v1.1 receipt reference env.local?
if grep -rq "env.local" genesis/receipt_v1.json genesis/receipt_v1_1.json 2>/dev/null; then
  echo "[held] genesis receipt references env.local — ABORT, inspect manually"
  exit 1
fi
echo "[banked] genesis receipts do not reference env.local — rewrite is receipt-safe"

# Does the v1.0 commit (fce8eb0) or v1.1 commit (682fe7b) contain the secret?
if echo "$COMMIT_HITS" | grep -qE 'fce8eb0|682fe7b|f42699a|a236581'; then
  echo "[held] CRITICAL: recent genesis commits contain the secret — they will be rewritten"
  echo "  receipt_id values survive (content hashes), but commit SHAs will change"
else
  echo "[banked] recent genesis commits are clean — only ancient commits affected"
fi

if [ "${CONFIRM:-0}" != "1" ]; then
  echo
  echo "=== DRY RUN — re-run with CONFIRM=1 to purge ==="
  echo "ROTATION NOTE: the secret is PUBLIC permanently. Rotating/supplying ROTATED="
  echo "changes the live value on disk; purging history stops future exposure only."
  echo
  echo "If blast radius is acceptable, arm with:"
  echo "  CONFIRM=1 ROTATED=\$(openssl rand -hex 32) bash bin/secret_scrub_env_local_v1.sh"
  exit 0
fi

# --- ARMED PATH (only runs with CONFIRM=1) ---
echo "=== [STAGE 1] rotate ==="
if [ -n "${ROTATED:-}" ]; then
  printf 'JWT_SECRET=%s\n' "$ROTATED" > .env.local
  chmod 600 .env.local
  echo "[banked] .env.local rotated (mode 600)"
else
  echo "[held] ROTATED not set — removing secret value, leaving placeholder"
  printf 'JWT_SECRET=ROTATE_ME\n' > .env.local
  chmod 600 .env.local
fi

echo "=== [STAGE 2] untrack + gitignore ==="
git rm --cached .env.local 2>/dev/null && echo "[banked] .env.local untracked" \
  || echo "[held] .env.local not tracked (?)"
grep -qxF '.env.local' .gitignore || { echo '.env.local' >> .gitignore; \
  echo '*.env.local' >> .gitignore; echo ".env*" >> .gitignore; \
  echo "[banked] gitignore hardened"; }

echo "=== [STAGE 3] snapshot ==="
git branch "safety/pre-scrub-${STAMP}" && echo "[banked] safety branch created"
git bundle create "/home/jesse/openroot-backup-prescrub-${STAMP}.bundle" --all
echo "[banked] rescue bundle: openroot-backup-prescrub-${STAMP}.bundle (KEEP OFFREPO)"

echo "=== [STAGE 4] history rewrite ==="
if [ -z "$FILTER" ]; then
  command -v pip3 >/dev/null && pip3 install --user git-filter-repo
  export PATH="$HOME/.local/bin:$PATH"
  command -v git-filter-repo >/dev/null || { echo "[held] no filter-repo"; exit 1; }
fi
printf '%s==>REDACTED-JWT-SCRUBBED\n' "$SECRET" > "/tmp/replace-v1-${STAMP}.txt"
git filter-repo --force --replace-text "/tmp/replace-v1-${STAMP}.txt" \
  --path .env.local --invert-paths 2>/dev/null \
  || git filter-repo --force --replace-text "/tmp/replace-v1-${STAMP}.txt"
shred -u "/tmp/replace-v1-${STAMP}.txt" 2>/dev/null || rm -f "/tmp/replace-v1-${STAMP}.txt"
echo "[banked] history rewritten: .env.local excised + secret string replaced"

echo "=== [STAGE 5] verify ==="
echo "remaining refs to secret (must be 0):"
git grep -lF "$SECRET" $(git rev-list --all) 2>/dev/null | wc -l || true
if git log --all --oneline -S"$SECRET" | grep -q .; then
  echo "[held] SECRET STILL IN HISTORY — inspect"; exit 1
fi
echo "[banked] history clean"

echo "=== [STAGE 6] genesis manifest intact check ==="
if [ -f genesis/founding_docs/MANIFEST.sha256 ]; then
  ( cd genesis/founding_docs && sha256sum -c MANIFEST.sha256 ) \
    && echo "[banked] genesis docs untouched by rewrite (content-hash chain intact)"
fi

echo "=== [STAGE 7] mistake log scar ==="
python3 - <<'PY'
import hashlib, json, time
entry = {
  "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "event": "jwt-secret-leaked-env-local-public-repo",
  "canary": "CANARY:OPENROOT-JWT-SCRUB-V1",
  "remediation": "rotated placeholder, untracked, gitignored, filter-repo excised",
  "fingerprint": hashlib.sha256(b"jwt-env-local-scrub-2026").hexdigest()[:16],
}
with open("data/mistakes/mistake_log.jsonl", "a") as f: f.write(json.dumps(entry)+"\n")
print("[banked] scar logged:", entry["fingerprint"])
PY

echo "=== NEXT ==="
echo "1. Force-push required: git push --force origin main (history diverged post-rewrite)"
echo "2. ROTATE the real JWT_SECRET wherever it is consumed (docker/systemd/app env)"
echo "3. Delete safety branch + bundle once verified: git branch -D safety/pre-scrub-${STAMP}"
echo "$CANARY COMPLETE [exit=0]"
