#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
echo "[STAGE:preflight] $(hostname) at $(pwd)"

echo "[STAGE:strays] sweep loose artifacts into archive (never delete evidence)"
ARCH="archive/cleanup-${TS}"
mkdir -p "$ARCH/logs" "$ARCH/scripts" "$ARCH/reports"
for f in bash_check.log compile.log ci_heal_v1.sh or_install_v1.sh; do
  [ -f "$f" ] && mv -- "$f" "$ARCH/scripts/" && echo "[ARCHIVED] $f" || echo "[SKIP] $f"
done
[ -d reports ] && find reports -maxdepth 1 -type d -name 'router_r*' -exec mv -- {} "$ARCH/reports/" \; && echo "[ARCHIVED] router reports" || true
echo "[STAGE:strays] done — working tree dirt reduced to intentional untracked (context_bridge, human_gate_bundle, data)"

echo "[STAGE:gitignore] codify junk policy"
grep -q '^\*.log$' .gitignore || printf '\n# session junk (2026-09-21 clean state policy)\n*.log\n/tmp_orphan_\n' >> .gitignore
echo "[gate] gitignore updated"

echo "[STAGE:goals] rebuild GOALS.md + MASTER_TODO.md from verified queue (remnant-guided, human-gated)"
[ -f GOALS.md ] && cp GOALS.md "$ARCH/GOALS.md.bak" && echo "[gate] prior GOALS backed up" || echo "[gate] no prior GOALS.md (expected — known loss)"
cat > GOALS.md <<GOALSEOF
# GOALS — OpenRoot

Regenerated ${TS} from verified session queue + context_bridge remnants (original lost in history rewrite; remnants in session-2026-09-16-* files). Lumo-assisted, human-gated — REVIEW BEFORE TRUSTING.

## Mission
Open-source hardware blockchain: local-first AI orchestration + passive energy systems, structured to lift the economic bottom floor. eta = J_useful/J_human. Falsifiable claims only.

## Active Goals
1. **Public-readiness hardening** — CI green (DONE 2026-09-21), docs refreshed (DONE), quarantine discipline established (DONE)
2. **Contributor pipeline** — support Reh1t on issue #53 (RAG ingestion); history was force-pushed, their clone is stale
3. **GOALS/TODO restoration** — this file (DONE pending human gate)
4. **Profile polish** — pin 4 repos on profile, [PHOTO] slot in README
5. **aerocement-panel-v0** — standalone repo with build evidence
6. **SARE grant framing** — COP-boundary language, no >100% thermo
7. **Weekly cadence** — onepass_v3.sh every week
GOALSEOF

cat > MASTER_TODO.md <<TODOEOF
# MASTER TODO — OpenRoot (${TS})

Provenance: rebuilt from session-closeout queue (context_bridge/session-cicd-closeout-20260921_160334.md). Regeneration used setup_restore_v1 strategy.

## Now (this week)
- [ ] Human-gate review of regenerated GOALS.md + this file, then commit
- [ ] Reh1t issue #53: welcome comment + explain force-push history (git fetch && git reset --hard origin/main)
- [ ] Pin 4 repos on profile (gh api /user/pins or manual) + [PHOTO] slot in README
- [ ] Ingest 3 lessons from 2026-09-21 into lesson chain (py_compile /dev/stdin false-fail; no-op sed false-pass; double-comma edit)

## Next (2 weeks)
- [ ] aerocement-panel-v0 standalone repo with build evidence + BOM
- [ ] Quarantine triage: fix or formally retire hive_live_convergence_v1.sh (quote line 76) and refinement_loop_v1.sh (EOF line 99); delete workflow_recover.sh (garbage)
- [ ] SARE grant framing doc — COP-boundary language only
- [ ] Fix agape_cascade floor-cap flaw before any v2 claims (cap 100x100 < SOL 300x100)

## Standing cadence
- [ ] Weekly: onepass_v3.sh (env_map, manifest regen, drift, next-move, seed, commit)
- [ ] Every session: handoff seal in context_bridge/ with sha256
TODOEOF
echo "[gate] GOALS.md ($(wc -l < GOALS.md) lines) + MASTER_TODO.md ($(wc -l < MASTER_TODO.md) lines) drafted — UNCOMMITTED for human gate"

echo "[STAGE:readme-freshness] update Verified State table in README to current HEAD"
HEAD_SHORT=$(git rev-parse --short HEAD)
git fetch origin -q
if grep -q "HEAD | " README.md; then
  sed -i "s#| HEAD | .* (ahead.*#| HEAD | ${HEAD_SHORT} (fresh snapshot ${TS}; see DOCS.md) |#" README.md && echo "[gate] README HEAD row updated"
else
  echo "[gate] README HEAD row not found by pattern — manual check (grep '| HEAD |' README.md)"
fi
sed -i "s#^#Deprecated placeholder marker — never rendered#" /dev/null 2>/dev/null || true

echo "[STAGE:docs] regenerate DOCS.md with current file counts"
{
  echo "# DOCS Index — OpenRoot (${TS})"
  echo ""
  echo "Entry points: README.md (mission/doctrine/state) · SCOPE.md (boundaries) · GOALS.md (goals) · MASTER_TODO.md (queue)"
  echo ""
  for d in */ ; do
    d="${d%/}"; [ "$d" = ".git" ] && continue
    N=$(find "$d" -type f 2>/dev/null | wc -l)
    echo "- **${d}/** — ${N} files"
  done
} > DOCS.md
echo "[gate] DOCS.md regenerated"

echo "[STAGE:proof] full gate suite — local mirror of CI plus doc gates"
FAIL=0
for f in bin/*.py; do [ -f "$f" ] || continue; python3 -m py_compile "$f" 2>/dev/null || { echo "[FAIL-PY] $f"; FAIL=1; }; done
for f in bin/*.sh; do [ -f "$f" ] || continue; bash -n "$f" 2>/dev/null || { echo "[FAIL-SH] $f"; FAIL=1; }; done
for doc in README.md SCOPE.md GOALS.md MASTER_TODO.md DOCS.md; do [ -s "$doc" ] || { echo "[FAIL-DOC] $doc empty"; FAIL=1; }; done
grep -q "Human-gate" GOALS.md || { echo "[FAIL] GOALS lacks human-gate notice"; FAIL=1; }
[ "$FAIL" -eq 0 ] && echo "[PASS] all gates green" || { echo "[HELD] gates failing — nothing committed"; exit 1; }

echo "[STAGE:seal] commit strays-archive + gitignore + docs (GOALS/TODO left staged for human gate per doctrine)"
git add .gitignore "$ARCH" GOALS.md MASTER_TODO.md README.md DOCS.md
git status --porcelain | grep "^[MA]" 
echo "--- HUMAN GATE REVIEW ABOVE — files staged, review GOALS.md + MASTER_TODO.md now ---"
echo "Type: git commit -m '[RESTORE] GOALS/MASTER_TODO rebuilt from remnant queue + cleanup archive ${TS} — lumo-assisted, human-gated' && git push origin main"
echo "Or abort: git restore --staged GOALS.md MASTER_TODO.md && git checkout GOALS.md MASTER_TODO.md 2>/dev/null; true"
echo "[CANARY] OPTCLEAN-V1-${TS}-STAGED-NOT-COMMITTED"
echo "[exit=0]"
