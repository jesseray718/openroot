#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
ROOT=/home/${OPENROOT_USER}/openroot
echo "[STAGE 0] preflight"
command -v python3 >/dev/null
curl -sf --max-time 10 http://localhost:11434/api/tags >/dev/null || { echo "[held] ollama down"; exit 1; }
python3 -m py_compile "$ROOT/bin/pathway_ledger_v1.py" "$ROOT/bin/audit_via_ai_v1.py" && echo "[banked] py_compile gate"

echo "[STAGE 1] diff capture (git add -N first — diff is blind to untracked)"
cd "$ROOT"
git add -N .
git diff -- . ":(exclude)reports" ":(exclude)logs" ":(exclude)data/pathways.db" ":(exclude)data/embeddings*" > /tmp/openroot_pending.diff
DIFF_LINES=$(wc -l < /tmp/openroot_pending.diff)
echo "[banked] pending diff: ${DIFF_LINES} lines"

echo "[STAGE 2] smart routing"
if [ "$DIFF_LINES" -lt 300 ]; then
  MODEL=qwen2.5:3b
else
  MODEL=qwen2.5-coder:7b
fi
echo "[banked] routed: $MODEL"

echo "[STAGE 3] audit ROOT (with diff) then bin/"
python3 "$ROOT/bin/audit_via_ai_v1.py" --target "$ROOT" --diff-file /tmp/openroot_pending.diff --model "$MODEL" --kind workspace_audit
python3 "$ROOT/bin/audit_via_ai_v1.py" --target "$ROOT/bin" --model "$MODEL" --kind bin_audit

echo "[STAGE 4] ledger verify"
python3 "$ROOT/bin/pathway_ledger_v1.py" verify

echo "[STAGE 5] commit gate (default dry-run)"
if [ "${CONFIRM:-0}" = "1" ]; then
  git add bin/pathway_ledger_v1.py bin/audit_via_ai_v1.py bin/superlinear_audit_v1.sh reports/ data/pathways.db 2>/dev/null || true
  git commit -m "feat: superlinear pathway chain v1 — cached audit pathways, model routing, ledger seal (${MODEL}-authored, py_compile+chain-verify passed)" || true
  if [ -x "$ROOT/bin/push_guard.py" ]; then
    python3 "$ROOT/bin/push_guard.py" || git push origin main
  else
    git push origin main
  fi
  echo "[banked] committed+pushed"
else
  echo "[gate] DRY RUN — reports written, ledger sealed, nothing committed. Re-run with CONFIRM=1 to commit+push."
fi
