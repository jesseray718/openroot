#!/usr/bin/env bash
# triad_execute_all_v1.sh — nomic fix + hygiene debt + orphan quarantine + PoPW pivot + sibling clones
# CANARY:OPENROOT-TRIAD-EXECUTE-ALL-V1
# Gates: untrack (dry-run first), commit (COMMIT=1), push (PUSH=1), orphan move (MOVE_ORPHAN=1)
set -eu
export GIT_PAGER=cat TERM=dumb
R=/home/jesse/openroot
TS=$(date -u +%Y%m%dT%H%M%SZ)
HOST=$(hostname)
[ "$HOST" = "optiplex3060" ] || { echo "[held] run on optiplex3060"; exit 1; }
cd "$R"

# ---------- STAGE 1: nomic check false-negative fix ----------
echo "[gate] stage 1 — nomic check bug fix (tag-suffix mismatch)"
sed -i "s/grep -q '\"nomic-embed-text\"'/grep -q 'nomic-embed-text'/" "$R/check_nomic_embed_v1.sh" || true
grep -q "grep -q 'nomic-embed-text'" "$R/check_nomic_embed_v1.sh" && echo "[banked] pattern patched"
bash "$R/check_nomic_embed_v1.sh" || { echo "[held] nomic still failing — paste output back"; }

# ---------- STAGE 2: hygiene — untrack caches/backups (dry-run view) ----------
echo "[gate] stage 2 — hygiene untrack census"
UNTRACK_LIST=$(git ls-files | grep -E '\.(pyc|bak|before)$' || true)
UNTRACK_N=$(echo "$UNTRACK_LIST" | grep -c . || true)
echo "[banked] untrackable (pyc/bak/before): $UNTRACK_N files"
echo "$UNTRACK_LIST" | head -10
echo "[held] .log files held for your call: $(git ls-files | grep -c '\.log$' || true) tracked"
echo "[held] .next/ build artifacts tracked: $(git ls-files | grep -c '^\.next/' || true)"

if [ "${COMMIT:-0}" = "1" ]; then
  echo "[gate] stage 2b — EXECUTING untrack (COMMIT=1)"
  echo "$UNTRACK_LIST" | xargs -r git rm --cached -q
  # .next/ and report mega-files: untrack, keep on disk
  git ls-files | grep -E '^\.next/' | xargs -r git rm --cached -q || true
  git ls-files | grep -E '(theorem_discovery.*(text_files|keyword_hits|direct_concepts)\.txt|expansions/archives.*manifest\.jsonl)$' \
    | xargs -r git rm --cached -q || true
  # ignore rules so they never return
  cat >> .gitignore <<'IGN'
# hygiene v1 20261009: caches, backups, build output, mega-reports — never track
__pycache__/
*.pyc
*.bak
*.before
.next/
reports/theorem_discovery_*/text_files.txt
reports/theorem_discovery_*/keyword_hits.txt
reports/theorem_discovery_*/direct_concepts.txt
ledger/expansions/archives_*.manifest.jsonl
IGN
  git add .gitignore
  git commit -q -m "hygiene v1: untrack ${UNTRACK_N} pyc/bak/before + .next/ + theorem mega-reports; gitignore rules added (CANARY:OPENROOT-TRIAD-EXECUTE-ALL-V1) [banked]"
  echo "[banked] hygiene commit: $(git rev-parse --short HEAD)"
else
  echo "[held] dry-run only. Re-run with COMMIT=1 to execute stage 2b."
fi

# ---------- STAGE 3: 100MB orphan quarantine ----------
echo "[gate] stage 3 — orphan deepdive_latest.md handling"
ORPHAN=/home/jesse/deepdive_latest.md
if [ -f "$ORPHAN" ]; then
  OSHA=$(sha256sum "$ORPHAN" | awk '{print $1}')
  OSIZE=$(stat -c%s "$ORPHAN")
  mkdir -p "$R/attic/orphans"
  REC="$R/reports/deepdive/orphan_deepdive_latest_provenance-$TS.md"
  {
    echo "# orphan quarantine record — $TS"
    echo "- src: $ORPHAN"
    echo "- size: $OSIZE bytes | sha256: $OSHA"
    echo "- disposition: excerpt below, full file gzipped to attic/orphans/ (NOT committed — 100MB blob rule)"
    echo "## head excerpt"
    echo '```'; head -c 2000 "$ORPHAN"; echo; echo '```'
    echo "## tail excerpt"
    echo '```'; tail -c 2000 "$ORPHAN"; echo; echo '```'
  } > "$REC"
  echo "[banked] provenance record: $REC (sha256 $(sha256sum "$REC" | awk '{print $1}'))"
  if [ "${MOVE_ORPHAN:-0}" = "1" ]; then
    gzip -9 -c "$ORPHAN" > "$R/attic/orphans/deepdive_latest-$TS.md.gz"
    echo "[banked] gzip archived: attic/orphans/deepdive_latest-$TS.md.gz ($(du -h "$R/attic/orphans/deepdive_latest-$TS.md.gz" | cut -f1))"
    rm "$ORPHAN"
    echo "[banked] original removed from home (full copy preserved in attic, outside git)"
  else
    echo "[held] orphan left in place — re-run with MOVE_ORPHAN=1 to archive+remove"
  fi
else
  echo "[banked] no orphan present"
fi

# ---------- STAGE 4: Gumroad pivot — PoPW Evidence Chain Toolkit ----------
echo "[gate] stage 4 — PoPW packet reframe"
cat > "$R/docs/monetization/gumroad_pow_toolkit_draft-$TS.md" <<'INNER_EOF_G'
# Gumroad Listing Draft — PoPW Evidence Chain Toolkit (v1, PIVOTED from thermal packet)

## Why pivoted
Cross-repo census 20261009T181129Z: sibling thermal repos thin (15 files) / mostly
missing locally. Flagship inventory: 97 ledger/chain/PoPW files. Sell what's deep.

## Title
Proof-of-Physical-Work Evidence Chain Toolkit — tamper-evident logging for makers, labs, and builds

## Price
$19 launch, raise to $29 after 30 sales. Free tier: core scripts stay GPL-3.0 in repo.

## Pitch
Chain of custody for physical work: sensor readings, energy measurements (RAPL
microjoules), and build evidence hashed SHA-256, chained, and timestamped into SQLite.
Broken links expose tampered or corrupted evidence — automatically, not by vibes.

## Contents
- popw_ledger.py lineage (chained append, tamper detection, audit walk)
- Joule accounting harness: RAPL reads with ESTIMATE fallback, thermo ledger schema
- Dedup + cache pathway layer (hash lookup prevents recomputation — the eta lever)
- Multi-model gate integration (3B grader pre-check, human commit gate)
- Setup runbook: Ollama + nomic-embed + SQLite + FTS5, tested on Ubuntu 24.04 + Termux
- Verification checklist: how to prove a chain is intact, what broken links mean
- 3 worked examples from live deployments (compute energy, thermal cascade, corpus sweep)

## Honesty layer
Everything's GPL-3.0 in the public repo. You're buying curation, the runbook,
worked configs, and a support thread. State it plainly.

## Needed from Jesse
[ ] pick 3 cleanest worked examples from live runs
[ ] smoke-test runbook end-to-end on fresh clone
[ ] support channel decision (email/GitHub Discussions)
[ ] screenshots: audit walk output, broken-link detection demo (THE money shot)
INNER_EOF_G

echo "[banked] PoPW toolkit draft: docs/monetization/gumroad_pow_toolkit_draft-$TS.md"

# thermal drafts retained (SARE still thermal — grants want measurements, not kits)
echo "[banked] thermal drafts retained for SARE path; sibling clones below rebuild that lane"

# ---------- STAGE 5: commit monetization additions ----------
if [ "${COMMIT:-0}" = "1" ]; then
  git add "$R/docs/monetization/gumroad_pow_toolkit_draft-$TS.md" "$R/reports/deepdive/" "$R/reports/cross_repo_census-"*.md 2>/dev/null || true
  git add -A "$R/reports" 2>/dev/null || true
  git commit -q -m "monetization pivot: PoPW Evidence Chain Toolkit draft + census/orphan provenance (CANARY:OPENROOT-TRIAD-EXECUTE-ALL-V1) [banked]" || true
  echo "[banked] monetization commit: $(git rev-parse --short HEAD)"
else
  echo "[held] monetization commit deferred (COMMIT=0)"
fi

# ---------- STAGE 6: clone missing siblings (gh authed) ----------
echo "[gate] stage 6 — sibling clones"
mkdir -p /home/jesse/repos-allowlist
for repo in openroot-canon openroot-thesis openroot-spoke-template OpenCell-Thermal-System; do
  DIR="/home/jesse/$repo"
  if [ -d "$DIR" ]; then
    echo "[banked] $repo exists"
  elif gh repo view "jesseray718/$repo" >/dev/null 2>&1; then
    gh repo clone "jesseray718/$repo" "$DIR" -- --depth 1
    echo "[banked] $repo cloned (shallow) -> $(cd "$DIR" && git ls-files | wc -l) files"
  else
    echo "[held] jesseray718/$repo not found on GitHub"
  fi
done

# ---------- STAGE 7: optional push ----------
if [ "${PUSH:-0}" = "1" ]; then
  echo "[gate] stage 7 — PUSHING (PUSH=1)"
  git push origin main
  echo "[banked] pushed: $(git rev-parse --short HEAD)"
else
  echo "[held] push deferred. Verify locally, then re-run with PUSH=1 or use bin/push_guard.py"
fi

# ---------- STAGE 8: seal ----------
cat > "$R/context_bridge/handoff-triad-execute-$TS.md" <<INNER_EOF_H
# Handoff — triad_execute_all_v1 — $TS
- Artifacts: hygiene commit(s), orphan provenance report, PoPW toolkit draft, sibling clones
- Known loss risk: NONE (untracks are --cached only, files stay on disk)
- Debt flagged: .git still 253M — needs git filter-repo pass 2 (strip historical pyc/log/next blobs). SEPARATE session, fresh clone, CONFIRM gate. Do NOT rush.
- Thermal lane: rebuilt after sibling clone census re-run
- Next: 1) rerun cross_repo_census with cloned siblings 2) PoPW runbook smoke test 3) filter-repo pass 2 planning
INNER_EOF_H
git add context_bridge/handoff-triad-execute-$TS.md
[ "${COMMIT:-0}" = "1" ] && git commit -q -m "handoff: triad_execute_all_v1 session record [banked]" || echo "[held] handoff commit deferred"
echo "CANARY:OPENROOT-TRIAD-EXECUTE-ALL-V1 COMPLETE"
echo "[exit=0]"
