#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# seal_session_v1.sh — triage MASTER_TODO post-promotion, add README [PHOTO] slot,
# write context_bridge handoff, single gated commit+push. Dry-run default.
# [canary] seal_session_v1_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
HANDOFF="$REPO/context_bridge/session-20260919-1349-issue53-goals-sealed.md"
say gate "seal_session_v1 start $TS CONFIRM=$CONFIRM"

# [1] TRIAGED MASTER_TODO — replaces untriaged promoted draft (deduped: 4 Reh1t lines -> 1 done-item,
#     goals-rebuild dupes folded; kept: bench-test, opencell rubric, research.db, embed, kill_tmp, email)
cat > MASTER_TODO.md <<'TODO_EOF'
# MASTER TODO — OpenRoot
<!-- Rebuilt from context_bridge remnants 2026-09-19 (commit 1ec3e352), triaged same day.
     Supersedes lost todo-automation-v2.0. 18-task target. Provenance: goals_rebuild_v1 + human triage. -->

## Queue (ordered)
1. [x] GOALS.md + MASTER_TODO rebuild from context_bridge remnants — sealed 1ec3e352, triaged
2. [x] Reh1t #53 welcome comment — posted 2026-09-19T13:40Z, comment 5742340723 (rebase path given)
3. [ ] Pin 4 repos on profile (pin_repos_v1.sh staged) + [PHOTO] slot in openroot README
4. [ ] aerocement-panel-v0 standalone repo with build evidence
5. [ ] SARE grant framing (COP-boundary language, never >100% thermo)
6. [ ] Weekly onepass_v3.sh cadence

## Kept from mined carried-over items (kept)
7. [ ] Bench test hardware ordering — highest-leverage physical item
8. [ ] opencell-absorber.md abstract rubric: purpose, method+instrument, measurements-pending with uncertainty, implication
9. [ ] research.db identification
10. [ ] Confirm embed build [exit=0] + warm query latency, retire grep sweep in probe
11. [ ] kill_tmp junk cleanup in repo root if any remain
12. [ ] README [PHOTO] slot + contact email decision
13. [ ] Wire embeddings task for Reh1t issue #53 support (substrate exists)
14. [ ] Delete quarantine-pulse-20260918 branch on GitHub when confident
15. [ ] stack_gate.sh v2 recovery — open risk
16. [ ] task_rank/task_freq divergence documented; grader shape-vs-substance defect logged (7B/3B loop)
17. [ ] MASTER_TODO drift check at next onepass (target: <=18 tasks)
18. [ ] Agape cascade v2: fix floor cap 100x100 < SOL 300x100 before further runs
TODO_EOF
say banked "MASTER_TODO.md triaged: 18 tasks, items 1-2 done, dupes folded, artifacts pruned"

# [2] README [PHOTO] slot — only if absent
if grep -q '\[PHOTO\]' README.md 2>/dev/null; then
  say held "README already has [PHOTO] slot — skipping"
else
  python3 - <<'PY_PHOTO'
import re
p = "/home/jesse/openroot/README.md"
try: lines = open(p, encoding="utf-8").read().split("\n")
except FileNotFoundError:
    print("[held] no README.md — skip PHOTO slot"); raise SystemExit
insert_at = None
for i, l in enumerate(lines):
    if l.startswith("# "):
        insert_at = i + 1; break
if insert_at is None: insert_at = 0
slot = ["", "<!-- [PHOTO] slot: replace with maintainer photo, ~400px, alt=\"Jesse Ray, OpenRoot\" -->", "![Maintainer](TODO-photo-path)", ""]
lines[insert_at:insert_at] = slot
open(p, "w", encoding="utf-8").write("\n".join(lines))
print("[banked] [PHOTO] slot inserted under first README heading")
PY_PHOTO
fi

# [3] Handoff seal
cat > "$HANDOFF" <<'HO_EOF'
# Session 2026-09-19 13:49 — issue #53 sealed + GOALS/MASTER_TODO promoted

## Artifacts built (this session)
- bin/queue_advance_v1.py — mines context_bridge (recency*frequency), 7B-forge/3B-grade loop
  for #53 comment. GRADED DEFECTIVE (see below); kept as instrument-audit evidence.
- bin/goals_rebuild_v1.sh — remnant miner, drafts->CONFIRM promote. Executed clean twice.
- reports/goals_draft/ — task_rank.tsv (16 tasks, recency-weighted), task_freq.tsv (12, raw),
  pr53_comment_draft.md (REJECTED 7B draft, factual errors survived 3B gate at 6/10),
  issue53_comment_draft.md (hand-fixed, POSTED).
- bin/seal_session_v1.sh — this triage+handoff seal.
- bin/pin_repos_v1.sh — profile pin tool, staged separately.

## Verified state
- main @ 1ec3e352 = origin/main (rebuilt GOALS.md + triaged MASTER_TODO.md, pushed)
- Issue #53 comment posted: 2026-09-19T13:40:10Z, id IC_kwDOTGdzqc8AAAABVkUqcw / 5742340723,
  OWNER-authored, body verified via gh --json.
- Issue #53 = "Dev Contributors — Local LLM Agents + RAG Tooling", assignee Reh1t (Rehan Tariq), OPEN.
- 16 branches preserved (eyes-only rule; unique-commit overlap verified, not deleted).

## Instrument audit findings (doctrine additions)
1. OPERATOR INPUTS UNGATED: "#53" was misread as PR (it is an ISSUE). Both 7B and 3B
   amplified the wrong premise faithfully. Cheap falsifiable check (gh pr view, 5 sec)
   caught it. Lesson: verify target type before forging communications.
2. GRADER SHAPE-OVER-SUBSTANCE: 3B scored a draft containing a factual inversion
   (filter-repo "doesn't alter content"), a role inversion (asked PR AUTHOR to review),
   an invented branch name, and 173 words vs 80-130 spec — as 6/10 ACCEPT. Tone/structure
   grading passed factual defects. Artifact banked. Lesson: graders need factual
   spot-check fields, not just tone/rubric fields.
3. PASTE FAILURE MODES: fenced markdown wrappers break heredoc pastes (terminator never
   matches); SSH broken-pipe mid-paste corrupts first attempt; rm-f-before-write makes
   re-paste idempotent. Lesson: paste surfaces are raw bash only, py_compile gate before exec.

## Broken items
- stack_gate.sh v2 recovery — unresolved (carried)
- quarantine-pulse-20260918 branch on GitHub — deletion deferred (carried)
- agape_cascade v1.x floor-cap degeneracy — fix before v2 (carried, todo #18)

## Next actions
1. Run pin_repos_v1.sh -> CONFIRM=1 (pins: openroot, wisdom-scaffold, openroot-ecosystem,
   jesseray718.github.io by default, override via PIN_REPOS)
2. Replace README TODO-photo-path with real photo
3. aerocement-panel-v0 standalone repo with build evidence
4. Watch #53 for Reh1t reply; review their PR promptly when it lands
5. Next onepass: verify MASTER_TODO <= 18 tasks, re-triage drift

[exit=0]
HO_EOF
say banked "handoff sealed -> $HANDOFF ($(wc -l < "$HANDOFF") lines)"

# [4] gated commit
if [ "$CONFIRM" = "1" ]; then
  git add MASTER_TODO.md README.md "$HANDOFF"
  git commit -m "triage MASTER_TODO post-promotion (18-task target, dupes folded); README [PHOTO] slot; session handoff 2026-09-19 — issue53 sealed, instrument-audit findings; provenance: seal_session_v1" \
    && say banked "committed $(git rev-parse --short HEAD)"
  git push origin main && say banked "pushed"
else
  say held "DRY RUN — review MASTER_TODO.md + $HANDOFF, then CONFIRM=1 bash bin/seal_session_v1.sh"
fi
printf '[exit=0]\n'
