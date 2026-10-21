#!/usr/bin/env bash
# frp5_deep_audit.sh — full repo pass v5: GitHub deep audit + local gate + consolidate + guarded push
# Author: frp5 script, jesse-supervised. Dry-run unless CONFIRM=1.
set -euo pipefail
export GIT_PAGER=cat

REPO=/home/jesse/openroot
CANARY="[canary] frp5 paste intact"

cd "$REPO"
TS=$(date +%Y%m%d_%H%M%S)
RPT="$REPO/analysis/frp5_${TS}"
mkdir -p "$RPT" "$RPT/github"

echo "[frp5] ${TS} — mode: $([ "${CONFIRM:-0}" = "1" ] && echo EXECUTE || echo DRY-RUN)"

# ---------- [stage:fetch] ----------
echo "[stage:fetch] syncing refs..."
git fetch origin --prune 2>&1 | tee "$RPT/fetch.log" || true
git remote -v > "$RPT/remotes.txt"

# ---------- [stage:audit-local] ----------
echo "[stage:audit-local]"
{
  echo "== HEAD ==";            git rev-parse HEAD
  echo "== origin/main ==";     git rev-parse origin/main
  echo "== ahead/behind ==";    git rev-list --left-right --count main...origin/main
  echo "== status porcelain =="; git status --porcelain
  echo "== bin tracked files =="; COUNT=$(git ls-files bin/ | wc -l); echo "count=$COUNT"
  echo "== GOALS.md ==";       [ -f GOALS.md ] && echo present || echo MISSING
  echo "== MASTER_TODO.md =="; [ -f MASTER_TODO.md ] && echo present || echo MISSING
} > "$RPT/local_state.txt" 2>&1

BIN_COUNT=$(git ls-files bin/ | wc -l || echo 0)
if [ "$BIN_COUNT" -eq 0 ]; then
  echo "[held] bin/ UNTRACKED (seed flagged this as possible) — staged for bank, not committed unless CONFIRM=1"
fi

# stack_gate every runnable script in bin/ (dry-run safe — gate only)
if [ -f "$REPO/bin/stack_gate.sh" ]; then
  [ -x "$REPO/bin/stack_gate.sh" ] || chmod +x "$REPO/bin/stack_gate.sh"
  for f in "$REPO"/bin/*.sh; do
    bash "$REPO/bin/stack_gate.sh" "$f" >> "$RPT/stack_gate.log" 2>&1 || echo "GATE-FAIL: $f" >> "$RPT/stack_gate.log"
  done
  echo "[stage:gate] stack_gate complete -> $RPT/stack_gate.log"
else
  echo "[held] stack_gate.sh not executable/present — skipping gate" | tee -a "$RPT/stack_gate.log"
fi

# ---------- [stage:audit-github] ----------
echo "[stage:audit-github] gh API sweep"
gh auth status > "$RPT/github/auth.txt" 2>&1 || { echo "[gate] gh not authed — aborting github stage"; exit 1; }

gh repo view jesseray718/openroot --json name,pushedAt,defaultBranchRef,stargazerCount,isPrivate \
  > "$RPT/github/openroot.json" 2>&1 || true
gh pr list --repo jesseray718/openroot --state open --json number,title,author,headRefName,updatedAt \
  > "$RPT/github/open_prs.json" 2>&1 || true
gh repo list jesseray718 --limit 100 --json name,updatedAt,isPrivate,visibility,stargazerCount \
  > "$RPT/github/all_repos.json" 2>&1 || true
git ls-remote --heads origin > "$RPT/github/remote_branches.txt" 2>&1 || true

# quarantine branch + stale-branch detection (origin-only branches not in local)
grep -q "quarantine-pulse-20260918" "$RPT/github/remote_branches.txt" \
  && echo "QUARANTINE BRANCH STILL ON ORIGIN (candidate for delete under CONFIRM=1)" >> "$RPT/local_state.txt" \
  || echo "quarantine branch absent from origin" >> "$RPT/local_state.txt"

# PR #53 (Reh1t) special handling — force-push rewrote history, their clone is stale
gh pr view 53 --repo jesseray718/openroot --json number,title,state,author,mergeable \
  > "$RPT/github/pr53.json" 2>&1 || echo "PR 53 not accessible" > "$RPT/github/pr53.json"

# ---------- [stage:digest] ----------
python3 - "$RPT" <<'PYEOF'
import json, sys, pathlib
rpt = pathlib.Path(sys.argv[1])
def load(p):
    try: return json.loads((rpt/"github"/p).read_text())
    except Exception: return None
prs = load("open_prs.json") or []
repos = load("all_repos.json") or []
branches = [l.split("\t")[1].replace("refs/heads/","")
            for l in (rpt/"github/remote_branches.txt").read_text().splitlines() if l.strip()]
local_txt = (rpt/"local_state.txt").read_text()
import re as _re
_bm = _re.search(r"count=([0-9]+)", local_txt or "")
bin_count = int(_bm.group(1)) if _bm else 0
goals_present = bool(_re.search(r"GOALS\.md\npresent", local_txt or ""))
digest = {
  "ts": rpt.name,
  "open_prs": len(prs),
  "pr_numbers": [p.get("number") for p in prs],
  "public_repo_count": sum(1 for r in repos if not r.get("isPrivate")),
  "remote_branches": sorted(branches),
  "bin_tracked": bin_count,
  "goals_present": goals_present,
  "flags": [l for l in local_txt.splitlines() if "UNTRACKED" in l or "QUARANTINE" in l],
}
(rpt/"digest.json").write_text(json.dumps(digest, indent=2))
print("[stage:digest] " + json.dumps(digest["flags"]) + " | open_prs=%d | branches=%d"
      % (digest["open_prs"], len(branches)))
PYEOF

# ---------- [stage:consolidate] ----------
echo "[stage:consolidate] banking drift report"
cp "$RPT/digest.json" "$RPT/../frp5_latest_digest.json" 2>/dev/null || true
if command -v sqlite3 >/dev/null && [ -f "$REPO/data/repo_drift.db" ]; then
  sqlite3 "$REPO/data/repo_drift.db" \
    "INSERT INTO IF NOT EXISTS drift_log DEFAULT VALUES;" >/dev/null 2>&1 || true
fi

# ---------- [stage:push] ----------
if [ "${CONFIRM:-0}" = "1" ]; then
  git add -A
  if ! git diff --cached --quiet; then
    py_compile_fail=0
    find bin -name '*.py' -exec python3 -m py_compile {} \; 2>>"$RPT/py_compile.log" || py_compile_fail=1
    if [ "$py_compile_fail" = "0" ]; then
      git commit -m "frp5 audit: bank audit report + drift digest ($TS). frp5-authored, py_compile passed. [banked]"
      git push origin main
      echo "[banked] pushed $(git rev-parse --short HEAD)"
    else
      echo "[gate] py_compile FAILED — push held, see $RPT/py_compile.log"; exit 1
    fi
  else
    echo "[banked] worktree clean — nothing to commit"
  fi
  # quarantine cleanup — only after digest reviewed by human
  echo "[held] quarantine branch deletion intentionally EXCLUDED from auto-push. Run manually when confident:"
  echo "       git push origin --delete quarantine-pulse-20260918"
else
  echo "[held] dry-run complete. Review $RPT/local_state.txt + $RPT/digest.json"
  echo "[held] re-run with CONFIRM=1 to commit+push report artifacts"
fi

echo "$CANARY"
# --- verify paste integrity ---
tail -1 "$0" | grep -q "\[canary\] frp5 paste intact" || { echo "CANARY FAIL — tail truncated"; exit 1; }
echo "[exit=0]"
