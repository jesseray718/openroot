# Lessons Draft — session 2026-09-20 (UNCOMMITTED, human gate)
# Extracted from verified terminal events today; every claim cites its source event.

## Instrument failures (audit-instruments doctrine)
1. **Canary regex bug**: `grep -q "$CANARY"` treats `[...]` as char-class; literal canary
   can never self-match. Fix: `grep -qF`. Source: 2 aborted runs, canary gate working
   as intended on a bug OF the gate. Lesson: pattern-escape test strings before trusting gates.
2. **Structural-pass / provenance-fail**: 3B graded hallucinated MASTER_TODO as PASS because
   rubric checked format (actionable/dedupe/grouped) but never GROUNDING (traceable to source
   chunks). 2 real statements in, 12 fabricated items out, stamped "nothing invented".
   Lesson: every rubric needs a grounding criterion; graders verify citation, not vibe.
3. **Stale-boot-seed near-miss**: mesh was about to overwrite a 152-line curated MASTER_TODO
   because the queue said "rebuild from remnants" — but 3 commits (1ec3e352, 9f0ae0fa,
   52082cfe) had ALREADY completed that rebuild. Lesson: before executing queued work,
   verify the queue isn't stale; `git log -- <target-file>` is the cheapest staleness probe.
4. **Diff-stat as oracle**: the `150 deletions` line was the ONLY signal a real file existed
   underneath the dry-run. Lesson: always read --stat on dry-runs; deletions of unknown
   content = STOP and investigate before CONFIRM.

## Compounding wins
5. Dry-run-default doctrine saved real work (item 3 above would have shipped at CONFIRM=1).
6. lb.sh v2 parachute bridge operational: autonomous local mutations, human remote gate.

## η (efficiency) observations
- 4 dead canary runs → 1-char fix (grep -qF); instrument audits remain highest-leverage work.
- Session recovered truth the boot seed lost: stale queues compound into dangerous autonomy.
