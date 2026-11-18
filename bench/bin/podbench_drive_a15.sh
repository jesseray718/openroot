#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  OPENROOT / PODBENCH-100 — STAGE, RUN, SEAL, COMMIT, PUSH
#  Node: A15 (Termux) — paste-safe, $HOME-portable, honest-receipt
#  Style: comment headers on every paste block (anti-clipping)
# ============================================================
set -u
# ---- [block 1: locate the repo; never hardcode /home] ----
ROOT="$HOME/openroot"
cd "$ROOT" || { echo "no repo at $ROOT"; exit 1; }
echo "== gate: HEAD = $(git rev-parse --short HEAD) =="

# ---- [block 2: verify the bench artifacts landed] ----
SPEC="bench/PODBENCH_100_SPEC_v1.md"
RUNNER="bench/bin/podbench_runner_v1.py"
QS="bench/questions/podbench_100_v1.jsonl"
SURVEY="docs/survey/OPENROOT_PROJECT_SURVEY_20261105.md"
for f in "$SPEC" "$RUNNER" "$QS" "$SURVEY"; do
  [ -f "$f" ] || { echo "MISSING: $f — copy it in before running"; exit 1; }
done

# ---- [block 3: gitignore runtime state once] ----
mkdir -p bench/state bench/receipts
grep -q '^bench/state/' .gitignore 2>/dev/null || echo 'bench/state/' >> .gitignore

# ---- [block 4: gate on ollama + model presence] ----
MODELS_TRY="qwen2.5-coder:0.5b qwen2.5:1.5b"
MODEL=""
if curl -s http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
  for m in $MODELS_TRY; do
    curl -s http://127.0.0.1:11434/api/tags | grep -q "\"$m\"" && { MODEL="$m"; break; }
  done
else
  echo "DEFECT: ollama daemon unreachable — start it first (ollama serve &)"; exit 1
fi
[ -z "$MODEL" ] && { echo "DEFECT: none of $MODELS_TRY installed"; exit 1; }
echo "== model selected: $MODEL =="

# ---- [block 5: THE LOOP — one question at a time, cache threads forward] ----
# Cache pathway: answer_n is hashed together with the previous flag ->
# flag_n goes into question n+1's preamble. Tampering anywhere breaks the chain.
TS="$(date -u +%Y%m%dT%H%M%SZ)"
STATE="bench/state/podbench_${TS}"
OUTDIR="bench/receipts/run_${TS}"
mkdir -p "$STATE" "$OUTDIR"
CHAIN_SHA=""                 # seed: empty chain = genesis
QID=0
CORRECT=0; TOTAL=0; ERRORS=0
> "$OUTDIR/verdict_table.tsv"
printf 'qid\tverdict\n' >> "$OUTDIR/verdict_table.tsv"

feed_question () {
  # $1 = question text ; $2 = cache flag text (may be empty for Q1)
  local prompt="You are answering PODBENCH-100 for the OpenRoot project.
Rely ONLY on committed project evidence. If a question (or the cached state
below) asserts something unstaged or unproven, say so explicitly and answer
'unstaged / not in the ledger' rather than guessing.
CACHED_PATHWAY_FROM_PREVIOUS_ANSWER:
$2
QUESTION:
$1
End with exactly three lines:
ANSWER_VERDICT: CORRECT|REFUSED
LABEL: DERIVED|ATTESTED
ONE_SENTENCE_SUMMARY:""$'"
  jq -n --arg m "$MODEL" --arg p "$prompt" \
     '{model:$m, prompt:$p, stream:false, options:{temperature:0}}' \
    | curl -s http://127.0.0.1:11434/api/generate -d @- \
    | jq -r '.response // "__ERROR__"'
}

while IFS=$'\t' read -r QNUM TEXT EXPECTED; do
  [ -z "${TEXT:-}" ] && continue
  FLAG="{\"prev_qid\":${QID},\"chain\":\"${CHAIN_SHA}\"}"
  ANS="$(feed_question "$TEXT" "$FLAG")"
  if [ "$ANS" = "__ERROR__" ] || [ -z "$ANS" ]; then
    ERRORS=$((ERRORS+1)); VERDICT="RUNTIME_ERROR"
  elif printf '%s' "$EXPECTED" | grep -qi "$(printf '%s' "$ANS" | tail -c 400)" \
       || printf '%s' "$ANS" | grep -qi "$(printf '%s' "$EXPECTED")"; then
    VERDICT="CORRECT"; CORRECT=$((CORRECT+1))
  elif printf '%s' "$ANS" | grep -qiE 'unstaged|not in the ledger|cannot confirm|withdrawn|no reliable'; then
    VERDICT="REFUSED_HONEST"; CORRECT=$((CORRECT+1))
  else
    VERDICT="MISSED"
  fi
  TOTAL=$((TOTAL+1))
  CHAIN_SHA="$(printf '%s%s' "$CHAIN_SHA" "$(printf '%s' "$ANS" | sha256sum | cut -d' ' -f1)" | sha256sum | cut -d' ' -f1)"
  QID="$QNUM"
  printf '%s\t%s\n' "$QNUM" "$VERDICT" >> "$OUTDIR/verdict_table.tsv"
  printf '--- Q%s [%s] ---\n%s\n' "$QNUM" "$VERDICT" "$ANS" >> "$OUTDIR/raw_answers.txt"
  echo "Q$QNUM -> $VERDICT"
done < bench/questions/podbench_questions_plain.tsv

# ---- [block 6: seal the receipt — honest, exit code tells the truth] ----
ACC="$CORRECT"; RUN_TOT="$TOTAL"
if [ "$ERRORS" -gt 0 ] || [ "$ACC" -lt 70 ]; then STATUS="UNREFINED_BASELINE"; EXITCODE=1
else STATUS="PASS"; EXITCODE=0; fi
RECEIPT="$OUTDIR/RUN_RECEIPT.md"
cat > "$RECEIPT" <<EOF
# PODBENCH-100 RUN RECEIPT
- run_id: ${TS}-A15
- node: A15 (Termux) | commit: $(git rev-parse --short HEAD) | model: ${MODEL}@T0
- ENVIRONMENT_DEFECTS: lattice=${LATTICE_STATE:-unchecked}; pods=$(ls "$HOME"/pods/*/pod.db 2>/dev/null | wc -l); heredoc_patch=$(git log --oneline -1 | grep -c 7515ff0 || true)
- accuracy: ${ACC}/${RUN_TOT} | errors: ${ERRORS}
- cache_chain_final_sha256: ${CHAIN_SHA}
- classification: DERIVED (single-run, scripted grading) — chain is ATTESTED by this receipt's sha
- status: ${STATUS}
- exit_code: ${EXITCODE}
EOF
sha256sum "$RECEIPT" >> "$RECEIPT"

# ---- [block 7: stage, commit, push — one origin, then OptiPlex pulls] ----
git add "$SPEC" "$RUNNER" "$QS" "$SURVEY" "$RECEIPT" \
        "$OUTDIR/verdict_table.tsv" "$OUTDIR/raw_answers.txt" .gitignore
git commit -m "bench(podbench-100): spec + runner + sealed receipt ${TS}-A15 (${STATUS}, ${ACC}/${RUN_TOT})"
git push origin main
echo "== pushed. OptiPlex next: git pull origin main =="
exit "$EXITCODE"

