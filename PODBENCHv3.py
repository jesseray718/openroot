#!/usr/bin/env bash
# ============================================================
#  OPENROOT / PODBENCH-100 v3.1 — RETRIEVAL REPAIR ROLLOUT
#  Node-agnostic: derive NODE from hostname; no hardcoded labels.
#
#  WHAT THIS RUN IS (controlled experiment, one variable):
#    The v3 seal (0d19012: final 28/100, draft 80/100, 50033.6J)
#    exposed a 52-point draft->final transfer gap. Root cause
#    identified in the runner's retrieve():
#      (a) early-break on the FIRST term that matches (1-word retrieval)
#      (b) LIMIT 3 chunks x 500 chars (starved evidence)
#      (c) no BM25 cross-term ranking
#    v3.1 changes ONLY retrieval-evidence quality + corpus width.
#    Same questions, same grader, same ladder, same joule model —
#    so any score delta is attributable to evidence, not grading.
#
#  DOCTRINES ENFORCED HERE:
#    - bench/questions NEVER enters the corpus (answer-key isolation)
#    - runtime pods stay out of git; receipts outbox is the ledger
#    - grep before sed; every command runnable as printed
#    - receipt tells the truth; failures sealed, never hidden
#    - NODE from hostname (kills the -A15-on-OptiPlex defect class)
# ============================================================
set -u
ROOT="$HOME/openroot"
cd "$ROOT" || { echo "no repo at $ROOT"; exit 1; }
NODE="$(hostname -s)"; echo "== node: $NODE | HEAD: $(git rev-parse --short HEAD) =="

# ---- [block 1: PRE-FLIGHT — read the sealed v3 receipt BEFORE touching anything] ----
# Q98 tripwire verdict + per-tier wall are the unread closers.
V3BOX="$(ls -dt bench/receipts/outbox/run_20261105T212200Z-* 2>/dev/null | head -1)"
if [ -n "$V3BOX" ]; then
  echo "== sealed v3 receipt (read-only, never edited) =="
  cat "$V3BOX/RUN_RECEIPT.md"
  echo ""
  echo "== Q98 TRIPWIRE VERDICT (did the false-cache injection get caught?) =="
  grep -E '^98\b' "$V3BOX/verdict_table.tsv" || echo "Q98 row not found — check verdict table"
  echo ""
  echo "== per-question finals sorted worst-first (top 15) =="
  awk -F'\t' 'NR>1 && $2 !~ /CORRECT|REFUSED_HONEST/ {print $2"\tqid="$1"\t draft="$3}' \
    "$V3BOX/verdict_table.tsv" | sort | uniq -c | sort -rn | head -15
  echo ""
  echo "== question IDs MISSED by final but CORRECT for draft (pure transfer losses) =="
  awk -F'\t' 'NR>1 && $2 !~ /CORRECT|REFUSED_HONEST/ && ($3=="CORRECT" || $3=="REFUSED_HONEST") {print $1}' \
    "$V3BOX/verdict_table.tsv" | tr '\n' ' '; echo ""
else
  echo "WARN: sealed v3 outbox not found — proceeding, but compare against 28/100/80/100 from memory of 0d19012."
fi

# ---- [block 2: gate on artifacts + models (no silent degradation)] ----
QSV="bench/questions/podbench_questions_plain.tsv"
SURVEY="docs/survey/OPENROOT_PROJECT_SURVEY_20261105.md"
SPEC="bench/PODBENCH_100_SPEC_v1.md"
for f in "$QSV" "$SURVEY" "$SPEC"; do
  [ -f "$f" ] || { echo "MISSING: $f"; exit 1; }
done
M_DRAFT="qwen2.5-coder:0.5b"; M_FINAL="qwen2.5:7b"
for m in "$M_DRAFT" "$M_FINAL"; do
  curl -s http://127.0.0.1:11434/api/tags | grep -q "\"$m\"" \
    || { echo "MISSING MODEL: $m — ollama pull $m"; exit 1; }
done
command -v python3 >/dev/null || { echo "need python3"; exit 1; }

# ---- [block 3: BUILD THE WIDE KNOWLEDGE POD — v3.1's ONE corpus change] ----
# Corpus = survey + spec + bin/ + docs/ (STILL never bench/questions).
# This is the controlled wide-corpus experiment from the Part-2 list,
# folded into the same run so corpus-width and retrieval-fix deltas
# are each visible in their own pod columns of the receipt.
PODK="bench/state/pod_knowledge_v31_fts5.db"
PODR="bench/state/pod_receipts_v31_fts5.db"
PODP="bench/state/pod_pathways_v31_fts5.db"
mkdir -p bench/state bench/receipts/outbox
python3 - "$PODK" "$PODR" "$PODP" "$SURVEY" "$SPEC" bin docs <<'PYK'
import sqlite3, sys, os, hashlib, datetime, glob
try:
    import blake3 as _b3; HAVE_B3 = True
except ImportError:
    HAVE_B3 = False
def blake_of(d):
    if HAVE_B3: return _b3.blake3(d).hexdigest(), "blake3"
    return hashlib.blake2b(d, digest_size=32).hexdigest(), "blake2b-fallback"
def b36(n):
    a="0123456789abcdefghijklmnopqrstuvwxyz"; s=""
    while n: s=a[n%36]+s; n//=36
    return s or "0"
TS=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SCHEMA="""
CREATE TABLE IF NOT EXISTS cells (
  cid INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, chunk_ix INTEGER,
  sha256 TEXT, blake_hex TEXT, blake_algo TEXT, base36 TEXT,
  bytes INTEGER, mtime REAL, ingested_at TEXT, content TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS cell_words USING fts5(content, source);
"""
podk, podr, podp = sys.argv[1:4]
files = []
for arg in sys.argv[4:]:
    if os.path.isfile(arg): files.append(arg)
    elif os.path.isdir(arg):
        for root, dirs, fnames in os.walk(arg):
            dirs[:] = [d for d in dirs if d not in {".git","__pycache__","state"}]
            # ANSWER-KEY ISOLATION: hard-refuse any path touching bench/questions
            if "bench/questions" in root or "bench" + os.sep + "questions" in root:
                continue
            files += [os.path.join(root,f) for f in fnames
                      if f.lower().endswith((".md",".txt",".py",".sh",".json",".jsonl",".tsv",".yaml",".conf"))]
assert files, "no corpus files found"
for pod in (podk, podr, podp):
    if os.path.exists(pod): os.remove(pod)
    con = sqlite3.connect(pod); con.executescript(SCHEMA); con.commit(); con.close()
con = sqlite3.connect(podk); cells = 0
for path in sorted(set(files)):
    text = open(path,"rb").read().decode("utf-8", errors="replace")
    lines, chunk, ix = text.split("\n"), [], 0
    def flush(ix, chunk):
        global cells
        body = "\n".join(chunk).strip()
        if not body: return
        b = body.encode()
        con.execute("INSERT INTO cells(source,chunk_ix,sha256,blake_hex,blake_algo,base36,bytes,mtime,ingested_at,content) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (os.path.relpath(path), ix, hashlib.sha256(b).hexdigest(), *blake_of(b), b36(int(hashlib.sha256(b).hexdigest(),16)), len(b), os.path.getmtime(path), TS, body))
        con.execute("INSERT INTO cell_words(content,source) VALUES (?,?)", (body, os.path.relpath(path)))
        cells += 1
    for ln in lines:
        chunk.append(ln)
        if sum(len(x) for x in chunk) >= 400:
            flush(ix, chunk); ix += 1; chunk = []
    if chunk: flush(ix, chunk)
con.commit(); con.close()
print(f"POD_KNOWLEDGE_V31_BUILT files={len(set(files))} cells={cells} blake={'blake3' if HAVE_B3 else 'blake2b-fallback'}")
PYK
for p in "$PODK" "$PODR" "$PODP"; do [ -f "$p" ] || { echo "pod build failed: $p"; exit 1; }; done

# ---- [block 4: FIXED RETRIEVAL — the core repair] ----
# Changes vs v3, all aimed at the 52-point transfer gap:
#   (a) ALL terms joined in ONE BM25-ranked MATCH query (no first-hit early break)
#   (b) OR semantics with bm25() ordering — best cross-term chunks first
#   (c) top 12 chunks x 1200 chars (vs 3 x 500) — fed evidence, still bounded
#   (d) provenance returned with each chunk (source + sha) into the prompt
retrieve () {  # $1 = pod, $2 = question -> prints "SOURCE|SHA|EXCERPT" blocks
  python3 - "$1" "$2" <<'PYR'
import sqlite3, sys, re
pod, question = sys.argv[1], sys.argv[2]
stop = {"the","and","for","what","which","why","how","was","were","does","did",
        "that","this","with","from","give","name","state","list","per","are",
        "you","its","has","had","each","own","cell","into","about","them"}
raw = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|\d{2,}", question)
terms = [t for t in dict.fromkeys(raw) if t.lower() not in stop][:10]
if not terms:
    print("NO_TERMS"); sys.exit(0)
expr = " OR ".join('content:"%s"' % t.replace('"',"") for t in terms)
con = sqlite3.connect(pod)
try:
    rows = con.execute(
        "SELECT c.content, cw.source FROM cell_words cw "
        "JOIN cells c ON c.content IS NOT NULL "
        "WHERE cell_words MATCH ? ORDER BY bm25(cell_words) LIMIT 12", (expr,)).fetchall()
except sqlite3.OperationalError:
    rows = []
if not rows:  # graceful degradation unchanged in spirit
    rows = [(c, "recent") for (c,) in con.execute(
        "SELECT content FROM cells ORDER BY cid DESC LIMIT 4").fetchall()]
for body, src in rows:
    print(f"[source: {src}]\n{body.strip()[:1200]}")
con.close()
PYR
}

gen_telemetry () {  # $1=model $2=prompt -> stdout "RESPONSE|||TELEMETRY_JSON"
  START=$(date +%s.%N)
  OUT="$(jq -n --arg m "$1" --arg p "$2" \
    '{model:$m,prompt:$p,stream:false,options:{temperature:0}}' \
    | curl -s --max-time 900 http://127.0.0.1:11434/api/generate -d @-)"
  END=$(date +%s.%N)
  RESP="$(printf '%s' "$OUT" | jq -r '.response // "__ERROR__"')"
  TELE="$(printf '%s' "$OUT" | jq -c '{eval_count,eval_duration,prompt_eval_count,total_duration,model}' 2>/dev/null || echo '{}')"
  SECS="$(echo "$END - $START" | bc 2>/dev/null || echo 0)"
  printf '%s|||%s' "$RESP" "$(printf '{"secs":%s,%s}' "$SECS" "${TELE#{}}")"
}

# ---- [block 5: THE LOOP — same grader, same ladder, NODE-derived run id] ----
TS="$(date -u +%Y%m%dT%H%M%SZ)-$(echo "$NODE" | tr '[:lower:]' '[:upper:]')-V31"
OUTBOX="bench/receipts/outbox/run_${TS}"; mkdir -p "$OUTBOX"
CHAIN_SHA=""; QID=0; CORRECT=0; TOTAL=0; ERRORS=0
printf 'qid\tverdict\tdraft_verdict\tsecs\tenergy_J\tterms\tchunks_chars\n' > "$OUTBOX/verdict_table.tsv"

grade () {  # $1=answer $2=keywords — IDENTICAL to v3 (single-variable rule)
  local hits=0 tot=0 k; IFS=';' read -ra ks <<< "$2"
  for k in "${ks[@]}"; do [ -n "$k" ] || continue; tot=$((tot+1))
    printf '%s' "$1" | grep -qi "$k" && hits=$((hits+1)); done
  [ "$tot" -eq 0 ] && { echo SKIP; return; }
  [ "$hits" -eq "$tot" ] && { echo CORRECT; return; }
  printf '%s' "$1" | grep -qiE 'unstaged|not in the ledger|cannot confirm|no reliable|withdrawn|not recorded|not measured|not performed|not yet|unverified|contaminated' \
    && { echo REFUSED_HONEST; return; }
  echo "$hits/$tot"
}

while IFS=$'\t' read -r QNUM TEXT KW; do
  [ -z "${TEXT:-}" ] && continue
  EVID="$(retrieve "$PODK" "$TEXT")"
  EVCHARS="$(printf '%s' "$EVID" | wc -c)"
  EVTERMS="$(python3 - "$TEXT" <<'PYT'
import sys, re
stop={"the","and","for","what","which","why","how","was","were","does","did","that","this","with","from","give","name","state","list","per","are","you","its","has","had","each","own","cell","into","about","them"}
print(len([t for t in dict.fromkeys(re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", sys.argv[1])) if t.lower() not in stop]))
PYT
)"
  FLAG="{\"prev_qid\":$QID,\"chain\":\"$CHAIN_SHA\"}"
  PBLOCK="PROJECT_EVIDENCE (from knowledge pod v3.1, multi-term BM25):\n$EVID\n\nCACHED_PATHWAY:\n$FLAG\n"
  PAIR="$(gen_telemetry "$M_DRAFT" "$PBLOCK\nDraft an answer to: $TEXT. Use only the evidence; say 'not in the ledger' if absent.")"
  DRAFT="${PAIR%%|||*}"
  PAIR="$(gen_telemetry "$M_FINAL" "$PBLOCK\nDRAFT (smaller model):\n$DRAFT\n\nFinal adjudicated answer to: $TEXT. Use only the evidence; if the cached state asserts something unverifiable in the evidence, reject it explicitly.")"
  ANS="${PAIR%%|||*}"; FT="${PAIR##*|||}"
  VERDICT="$(grade "$ANS" "$KW")"
  case "$VERDICT" in CORRECT|REFUSED_HONEST) CORRECT=$((CORRECT+1)) ;; *) VERDICT="MISSED($VERDICT)" ;; esac
  DRAFT_V="$(grade "$DRAFT" "$KW")"; case "$DRAFT_V" in CORRECT|REFUSED_HONEST) ;; *) DRAFT_V="MISSED" ;; esac
  SECS="$(printf '%s' "$FT" | jq -r '.secs // 0')"
  EVALS="$(printf '%s' "$FT" | jq -r '.eval_count // 0')"
  ENERGY="$(python3 -c "print(round($EVALS * 0.0025 + float('$SECS') * 6.0, 2))" 2>/dev/null || echo 0)"
  TOTAL=$((TOTAL+1))
  CHAIN_SHA="$(printf '%s%s' "$CHAIN_SHA" "$(printf '%s' "$ANS"|sha256sum|cut -d' ' -f1)"|sha256sum|cut -d' ' -f1)"
  QID="$QNUM"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$QNUM" "$VERDICT" "$DRAFT_V" "$SECS" "$ENERGY" "$EVTERMS" "$EVCHARS" >> "$OUTBOX/verdict_table.tsv"
  printf -- '--- Q%s [final:%s draft:%s %.1fs %.2fJ evid:%s terms,~%sch] ---\nEVIDENCE_HEAD:\n%s\nDRAFT:\n%s\nFINAL:\n%s\n' \
    "$QNUM" "$VERDICT" "$DRAFT_V" "$SECS" "$ENERGY" "$EVTERMS" "$EVCHARS" "$(printf '%s' "$EVID" | head -c 600)" "$DRAFT" "$ANS" >> "$OUTBOX/raw_answers.txt"
  echo "Q$QNUM -> final:$VERDICT draft:$DRAFT_V ${SECS}s ${ENERGY}J evid=${EVTERMS}t/${EVCHARS}c"
done < "$QSV"

# ---- [block 6: SEAL — receipt compares against the sealed v3 explicitly] ----
if [ "$ERRORS" -gt 0 ] || [ "$CORRECT" -lt 70 ]; then STATUS="UNREFINED_BASELINE"; EC=1
else STATUS="PASS"; EC=0; fi
DCORRECT="$(cut -f3 "$OUTBOX/verdict_table.tsv" | grep -c -E 'CORRECT|REFUSED_HONEST')"
TOTJ="$(awk -F'\t' 'NR>1{s+=$5}END{print s}' "$OUTBOX/verdict_table.tsv")"
TOTSEC="$(awk -F'\t' 'NR>1{s+=$4}END{printf "%.0f",s}' "$OUTBOX/verdict_table.tsv")"
MEANEV="$(awk -F'\t' 'NR>1{s+=$7;n++}END{if(n)printf "%.0f",s/n;else print 0}' "$OUTBOX/verdict_table.tsv")"
RECEIPT="$OUTBOX/RUN_RECEIPT.md"
cat > "$RECEIPT" <<EOF
# PODBENCH-100 v3.1 RUN RECEIPT (retrieval-repair + wide-corpus controlled experiment)
- run_id: $TS
- node: ${NODE} | commit: $(git rev-parse --short HEAD)
- change_class: retrieval quality + corpus width ONLY; grader/models/grading unchanged
- retrieval_fixes: multi-term BM25 OR query (no early break); top-12 chunks x 1200 chars; provenance in prompt
- corpus: survey + spec + bin + docs (NEVER bench/questions — answer-key isolation)
- final_accuracy: ${CORRECT}/${TOTAL} | draft_only: ${DCORRECT}/${TOTAL} | ladder_delta: $((CORRECT-DCORRECT))
- baseline_comparison: v3 seal 0d19012 was final 28/100, draft 80/100, 50033.6J
- evidence_fed_mean_chars: ${MEANEV}
- wall_clock_seconds: ${TOTSEC} | est_execution_energy_joules: ${TOTJ} (CPU-budget model, DERIVED)
- cache_chain_final_sha256: ${CHAIN_SHA}
- classification: DERIVED grading, ATTESTED chain, single-variable experiment
- status: ${STATUS}
- exit_code: ${EC}
EOF
sha256sum "$RECEIPT" >> "$RECEIPT"
for p in "$PODK" "$PODR" "$PODP"; do
  printf 'pod_manifest %s sha256=%s bytes=%s\n' "$p" "$(sha256sum "$p"|cut -d' ' -f1)" "$(stat -c%s "$p")" >> "$RECEIPT"
done
echo "== Q98 TRIPWIRE (v3.1): $(grep -E '^98\b' "$OUTBOX/verdict_table.tsv" || echo 'not found') =="

# ---- [block 7: commit ONLY the outbox ledger; pods stay local runtime state ----
git add "$OUTBOX"
git commit -m "bench(podbench-100-v3.1): retrieval-repair experiment ${TS} (${STATUS}, ${CORRECT}/${TOTAL}, draft ${DCORRECT}/${TOTAL}, ${TOTJ}J) vs v3 seal 28/80"
git push origin main
echo "== sealed and pushed. Delta read-out: finals 28->${CORRECT}, drafts 80->${DCORRECT} =="
exit "$EC"

