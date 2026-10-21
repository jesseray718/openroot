#!/usr/bin/env bash
# cascade_release_v2 - v2.6 rescue + release + milestones + cleanup
# CONFIRM=1 gates all executions; banks regardless of verdict; negative = data
set -u
export GIT_PAGER=cat
ROOT=/data/data/com.termux/files/home/openroot
REPO=jesseray718/openroot
TS=$(date +%Y%m%d_%H%M%S)
TAG="v2026.09.21-agape-cascade-ledger-discipline"
MS_CLOSED="agape-cascade ledger discipline (v2.5-v2.8)"
MS_OPEN="agape-cascade v2.9 queue"
CONF="${CONFIRM:-0}"
cd "$ROOT"

echo "=== [STAGE:auth] ==="
gh auth status >/dev/null 2>&1 && echo "[PASS] gh authed" || { echo "[LEAK] gh not authed"; exit 1; }

echo "=== [STAGE:v26-rescue-optiplex] ==="
if git ls-files --error-unmatch bin/agape_cascade_v26.py >/dev/null 2>&1; then
    echo "[held] v2.6 tracked locally"
else
    if [ "$CONF" = "1" ]; then
        ssh jesse@100.122.169.43 'bash -s' <<'REMOTE'
set -u
export GIT_PAGER=cat
cd /home/jesse/openroot
git ls-files --error-unmatch bin/agape_cascade_v26.py >/dev/null 2>&1 && { echo "[held] tracked"; exit 0; }
[ -f bin/agape_cascade_v26.py ] || { echo "[LEAK] v2.6 ABSENT on optiplex"; exit 1; }
python3 -m py_compile bin/agape_cascade_v26.py && echo "[PASS] compiled"
grep -q AGCA2V26 bin/agape_cascade_v26.py && echo "[PASS] canary"
git add bin/agape_cascade_v26.py
git commit -m "[ADD][CASCADE] v2.6 conservation-law ledger - orphan rescue (final)

Ran 2026-09-21, verdict=1 (instrument WORKING: leak 91.63 = 100*ln(0.4),
destruction never wrote path_log; merit-top 64.75 from FLOOR_MIN clamps).
Then set -eu guillotined the bank - 4th control-flow strike. Recovered
verbatim from this worktree where it fled untracked. The
bank-proceeds-regardless law (v2.7+) exists because of this commit.

Provenance: lumo-assisted, human-gated (paste execution IS the gate)"
git push origin main && echo "[banked] v2.6 sealed from optiplex"
REMOTE
        git pull --rebase origin main && echo "[PASS] optiplex sync"
    else
        echo "[held] v2.6 rescue dry-held - CONFIRM=1"
    fi
fi

echo "=== [STAGE:audit] ==="
git fetch origin --tags
DIVERGE=$(git log origin/main..HEAD --oneline | wc -l)
[ "$DIVERGE" -eq 0 ] && echo "[PASS] HEAD = origin/main" || { echo "[LEAK] divergence=$DIVERGE"; exit 1; }
NEEDS_TAG=1
git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null && NEEDS_TAG=0
[ "$NEEDS_TAG" -eq 1 ] && echo "[gate] tag ${TAG} will be created at $(git rev-parse --short HEAD)" \
                     || echo "[held] tag ${TAG} exists"

echo "=== [STAGE:notes] ==="
NOTES="context_bridge/release-notes-${TAG}-${TS}.md"
mkdir -p context_bridge
cat > "$NOTES" <<'NOTES_EOF'
# Agape Cascade v2.5 - v2.8: Ledger Discipline Arc

Five versions, one day. Each version kills an accounting lie the previous exposed.

## The arc

- **v2.5 (1cfe00a)** - solidarity deploy + closed ledger. Shocked arms beat
  controls (-90.9 welf) - flagged as impossible by its own author.
- **v2.6 (orphan rescue)** - conservation-law telescope. Verdict=1 WORKING:
  leak 91.63 = 100*ln(0.4), destruction never wrote path_log. Bank was
  guillotined by set -eu (4th control-flow strike); recovered from worktree.
- **v2.7 (41b224a)** - both books written, sub-saturation regime
  (GENS=40, kappa=0.08), saturation gate, permaculture policy. Leaked
  exactly == welf (double-count) - caught by its own telescope.
- **v2.8 (81cb8f3)** - single-book path integral: ONE log per realized
  change. Telescope exact BY CONSTRUCTION, leak ~1e-9 across all 8 arms.

## Results (v2.8, telescope-verified)

Shock = gen 12, -60% floors, -40% seeds. GENS=40, kappa=0.08.

| policy       | min_fl | med_fl | recov  | path_gain | cost_path |
|--------------|--------|--------|--------|-----------|-----------|
| bottom-first | 0.2761 | 0.2778 | 24     | 56.67     | 108.14    |
| equal        | 0.1641 | 0.2371 | never  | 43.13     | 106.73    |
| merit-top    | 0.01   | 0.01   | never  | -87.51    | 48.13     |
| permaculture | 0.2029 | 0.2451 | never  | 49.06     | 113.51    |

- `equal` holds the cost crown (106.73) at this regime.
- `merit-top` negative welfare in BOTH arms - extraction collapses the commons.
- `permaculture` pays +6.8 path cost for softer allocation (higher min_fl).
- Transfer wedges (welf-path: ~62-67 controls) DECLARED store-moves, not phantom growth.

## Verification

- Telescope: max |path - final_gain| ~ 1e-9, all arms [PASS]
- Saturation: all rows sub-ceiling (frac_at_cap <= 0.2) [VALID]
- Gates: py_compile + canary + stack_gate.sh v2 [PASS]. Canary: AGCA2V28.
- Full data: workareas/cascade-v28-*/results.json

Provenance: lumo-assisted, human-gated (paste execution IS the gate).
NOTES_EOF
echo "[banked] notes: $NOTES"

echo "=== [STAGE:release] ==="
if [ "$CONF" = "1" ] && [ "$NEEDS_TAG" -eq 1 ]; then
    gh release create "$TAG" \
        --target "$(git rev-parse HEAD)" \
        --title "Agape Cascade v2.8 - telescope-exact ledger discipline" \
        --notes-file "$NOTES" \
        && echo "[banked] RELEASE PUBLISHED: $TAG" \
        || echo "[LEAK] release failed - see gh output"
else
    echo "[held] release dry-held (CONF=$CONF, needs_tag=$NEEDS_TAG)"
fi

echo "=== [STAGE:milestones] ==="
if [ "$CONF" = "1" ]; then
    if ! gh api "repos/${REPO}/milestones" --jq ".[].title" 2>/dev/null | grep -qxF "$MS_CLOSED"; then
        gh api -X POST "repos/${REPO}/milestones" \
            -f title="$MS_CLOSED" \
            -f state=closed \
            -f description="Solidarity deploy -> conservation telescope -> single-book path integral. Closed by release ${TAG}." \
            >/dev/null && echo "[banked] milestone CLOSED: $MS_CLOSED"
    else
        echo "[held] milestone exists: $MS_CLOSED"
    fi
    if ! gh api "repos/${REPO}/milestones" --jq ".[].title" 2>/dev/null | grep -qxF "$MS_OPEN"; then
        gh api -X POST "repos/${REPO}/milestones" \
            -f title="$MS_OPEN" \
            -f state=open \
            -f description="Gini-at-recovery ranking, wedge trajectory, SHOCK_LOSS x DEPLOY_FRAC grid sweep, floor-cap tier question from v1.x." \
            >/dev/null && echo "[banked] milestone OPEN: $MS_OPEN"
    else
        echo "[held] milestone exists: $MS_OPEN"
    fi
    gh issue edit 53 --milestone "$MS_OPEN" >/dev/null 2>&1 \
        && echo "[banked] #53 (Reh1t RAG) -> $MS_OPEN" \
        || echo "[held] #53 milestone edit skipped"
else
    echo "[held] milestones dry-held - CONFIRM=1"
fi

echo "=== [STAGE:cleanup] ==="
for f in .commitmsg.txt bot_loop.pid bot_loop_restart.log; do
    [ -f "$f" ] && rm -f "$f" && echo "[clean] $f"
done
if [ "$CONF" = "1" ] && git stash list | grep -q pre-pull-reconcile; then
    git stash drop && echo "[clean] stale stash dropped"
else
    echo "[held] stash ${CONF:+kept}/absent"
fi

echo "=== [STAGE:verify] ==="
git log --oneline -3
gh release view "$TAG" --json tagName,url --jq '.tagName + " " + .url' 2>/dev/null || echo "[held] no release yet"
gh api "repos/${REPO}/milestones" --jq ".[] | .state + \" | \" + .title" 2>/dev/null | head -4
echo "HEAD: $(git rev-parse --short HEAD) | divergence: $(git log origin/main..HEAD --oneline | wc -l)"
echo "[BANKED] [exit=0]"
