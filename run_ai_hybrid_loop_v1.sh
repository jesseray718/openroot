#!/usr/bin/env bash
# run_ai_hybrid_loop_v1.sh — absolute-path, paste-safe hybrid loop
set -u
cd "$HOME/openroot" 2>/dev/null || { echo "FATAL: $HOME/openroot not found"; exit 2; }

TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN="outbox/ai_hybrid_loop/${TS}"
ABS_RUN="$(pwd)/$RUN"
mkdir -p "$RUN"
RECEIPT="$RUN/RUN_RECEIPT.md"
DB_LINK="universal_lattice_fts5.db"
MODELS_TRY="${MODELS_TRY:-qwen3.5:9b smollm2:1.7b qwen2.5-coder:0.5b}"
NQ="${NQ:-1}"
export MODELS_TRY NQ

declare -a STEP_NAMES=() STEP_STATES=() STEP_NOTES=()
mark() { local n="${3//|//}"; STEP_NAMES+=("$1"); STEP_STATES+=("$2"); STEP_NOTES+=("$n"); }

{
  echo "# AI HYBRID LOOP — RUN $TS"
  echo ""
  echo "- host: $(hostname 2>/dev/null)"
  echo "- repo: $(pwd) @ $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "- run_dir: $ABS_RUN"
  echo "- store: $(readlink "$DB_LINK" 2>/dev/null || echo MISSING)"
  echo "- questions: ${NQ}"
  echo "- models_try: ${MODELS_TRY}"
  echo ""
} > "$RECEIPT"
echo "[loop] run dir: $ABS_RUN"

# phase0
echo "[loop] phase0: interface discovery"
{ for f in bin/autodossier_compiler.py "$HOME/pods"/ask_pod_v1.py; do
    echo "===== $f ====="
    if [ -f "$f" ]; then echo "lines: $(wc -l < "$f")"; sed -n '1,20p' "$f"; else echo "MISSING"; fi
  done
} > "$RUN/DISCOVERY.txt" 2>&1
mark phase0-discovery "OK" "DISCOVERY.txt"

# step1 friction
echo "[loop] step1: friction scan"
S1="FAIL"
if timeout 300 python3 bin/friction_observer_v1.py --write-ledger data/friction_ledger.jsonl --json "$RUN/friction_report.json" > "$RUN/step1_friction.log" 2>&1; then
  S1="OK"
elif [ -f data/friction_report.json ]; then
  cp data/friction_report.json "$RUN/friction_report.json"
  S1="OK(reused)"
fi
mark step1-friction "$S1" "see step1_friction.log"

# step2 question travel
echo "[loop] step2: question travel"
cat > "$RUN/question_travel_v1.py" <<'PYTRAVEL'
#!/usr/bin/env python3
import json, os, re, sqlite3, sys, time, urllib.request, collections
RUN = sys.argv[1]
MODELS = os.environ.get("MODELS_TRY", "smollm2:1.7b").split()
NQ = int(os.environ.get("NQ", "1"))
STOP = set("the a an and or of to in on for with is are was were be been this that these those it its as at by from not but if then than so such can could will would should may might must have has had do does did about into over under between within without their there here what which who whom whose when where why how all any each few more most other some only own same too very just also".split())
def pick_db():
    for c in ("universal_lattice_fts5.db", os.path.expanduser("~/pods/clone_universal_20261016T083202Z/pod.db")):
        if os.path.exists(c): return os.path.realpath(c)
    return None
def fts_table(cur):
    names = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")]
    return "chunks_fts" if "chunks_fts" in names else (names[0] if names else None)
def text_col(cur, tab):
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({tab})")]
    best, best_len = None, -1
    for c in cols:
        try: L = cur.execute(f"SELECT sum(length({c})) FROM (SELECT {c} FROM {tab} LIMIT 200)").fetchone()[0] or 0
        except Exception: continue
        if L > best_len: best, best_len = c, L
    return best
def derive_q(text):
    words = [w for w in re.findall(r"[a-zA-Z]{4,}", text.lower()) if w not in STOP]
    top = [w for w,_ in collections.Counter(words).most_common(4)]
    if not top: return None, []
    return "What does the corpus say about " + ", ".join(top[:3]) + "?", top
def retrieve(cur, tab, tcol, query):
    try:
        rows = cur.execute(f"SELECT rowid, {tcol} FROM {tab} WHERE {tab} MATCH ? ORDER BY rank LIMIT 5", (query,)).fetchall()
        return rows, "fts5-match"
    except Exception:
        toks = re.findall(r'"([^"]+)"', query) or [query]
        where = " OR ".join([f"{tcol} LIKE ?" for _ in toks])
        rows = cur.execute(f"SELECT rowid, {tcol} FROM {tab} WHERE {where} LIMIT 5", [f"%{t}%" for t in toks]).fetchall()
        return rows, "like-fallback"
def ollama_tags():
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            return {m["name"] for m in json.load(r).get("models", [])}
    except Exception: return set()
def ground(prompt, avail):
    last = "no model"
    for m in MODELS:
        if m not in avail: continue
        body = json.dumps({"model": m, "prompt": prompt, "stream": False, "options": {"num_predict": 200, "temperature": 0.2}}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as r: out = json.load(r)
            return {"model": m, "elapsed_s": round(time.time()-t0,1), "text": (out.get("response") or "").strip(), "status": "OK"}
        except Exception as e: last = f"{type(e).__name__} on {m}"
    return {"model": None, "elapsed_s": None, "text": "", "status": f"UNAVAILABLE ({last})"}
def dump(doc):
    json.dump(doc, open(os.path.join(RUN, "QUESTION_TRAVEL.json"), "w"), indent=2)
def main():
    db = pick_db()
    doc = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "db": db, "questions": []}
    if not db:
        doc["error"] = "no pod db"; dump(doc); sys.exit(1)
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only=1"); cur = conn.cursor()
    tab = fts_table(cur); tcol = text_col(cur, tab)
    n = cur.execute(f"SELECT count(*) FROM {tab}").fetchone()[0]
    doc.update({"fts_table": tab, "text_col": tcol, "rows": n})
    avail = ollama_tags(); doc["ollama_models_available"] = sorted(avail)
    hits = 0
    for i in range(NQ):
        off = (n // (NQ + 1)) * (i + 1)
        row = cur.execute(f"SELECT rowid, {tcol} FROM {tab} ORDER BY rowid LIMIT 1 OFFSET ?", (off,)).fetchone()
        src_rid, src_txt = row[0], row[1] or ""
        q, top = derive_q(src_txt)
        if not q:
            print(f"  q{i}: empty terms, skip"); continue
        query = " OR ".join(f'"{t}"' for t in top[:4])
        res, engine = retrieve(cur, tab, tcol, query)
        rids = [r[0] for r in res]; hit = src_rid in rids; hits += int(hit)
        ctx = "\n\n---\n\n".join(f"[chunk {r[0]}] {(r[1] or '')[:700]}" for r in res[:3])
        prompt = ("Answer strictly from the context. If the context does not contain the answer, reply exactly: NOT_IN_CONTEXT.\n\nQuestion: " + q + "\n\nContext:\n" + ctx + "\n\nAnswer (max 4 sentences):")
        ans = ground(prompt, avail)
        doc["questions"].append({"idx": i, "source_rowid": src_rid, "question": q, "query_terms": top[:4],
            "retrieval": {"engine": engine, "top5_rowids": rids, "source_in_top5": hit}, "answer": ans})
        dump(doc)
        print(f"  q{i}: rowid={src_rid} recall@5={'HIT' if hit else 'MISS'} answer={ans['status']} model={ans['model']}")
    doc["summary"] = {"questions": NQ, "recall_hits": hits, "answered": sum(1 for x in doc["questions"] if x["answer"]["status"]=="OK")}
    dump(doc)
    print(f"  recall@5 = {hits}/{NQ}  answered_ok = {doc['summary']['answered']}/{NQ}")
main()
PYTRAVEL
S2="FAIL"
if timeout 600 python3 "$RUN/question_travel_v1.py" "$RUN" > "$RUN/step2_travel.log" 2>&1; then S2="OK"; fi
sed 's/^/  /' "$RUN/step2_travel.log" 2>/dev/null || true
mark step2-question-travel "$S2" "QUESTION_TRAVEL.json"

# step3 fractal — ABSOLUTE PATH, no tilde, no $HOME
echo "[loop] step3: fractal pod verification"
cat > "$RUN/pods_fractal_v1.py" <<'PYFRACTAL'
#!/usr/bin/env python3
import json, os, sqlite3, time
ROOT = os.path.expanduser("~/pods")
HERE = os.path.dirname(os.path.abspath(__file__))
pods = []
for name in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, name)
    pdb = os.path.join(d, "pod.db")
    if not (os.path.isdir(d) and os.path.isfile(pdb)): continue
    entry = {"pod": name, "bytes": os.path.getsize(pdb), "tables": {}}
    try:
        conn = sqlite3.connect(f"file:{pdb}?mode=ro", uri=True)
        conn.execute("PRAGMA query_only=1")
        tabs = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for t in tabs[:12]:
            try: entry["tables"][t] = conn.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
            except Exception as e: entry["tables"][t] = f"err:{type(e).__name__}"
        entry["core_sig"] = ",".join(sorted(tabs)); conn.close(); entry["status"] = "OK"
    except Exception as e:
        entry["status"] = f"ERR {type(e).__name__}: {e}"
    pods.append(entry)
sigs = {}
for p in pods: sigs.setdefault(p.get("core_sig", "?"), []).append(p["pod"])
groups = sorted(sigs.items(), key=lambda kv: -len(kv[1]))
doc = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "root": ROOT,
       "pod_count": len(pods),
       "signature_groups": [{"sig": s, "pods": ps} for s, ps in groups],
       "self_similar": {"max_group_size": len(groups[0][1]) if groups else 0,
                        "max_group_sig": (groups[0][0][:200] if groups else None),
                        "distinct_signatures": len(groups)}}
out = os.path.join(HERE, "PODS_FRACTAL.json")
with open(out, "w") as f: json.dump(doc, f, indent=2)
print(f"wrote {out}")
for s, ps in groups[:5]:
    print(f"  sig[{len(ps)} pods]: {s[:90]}  e.g. {ps[:3]}")
big = len(groups[0][1]) if groups else 0
print(f"  verdict: {len(pods)} pods, {len(groups)} distinct signatures, largest self-similar group {big}")
PYFRACTAL
S3="FAIL"
if timeout 300 python3 "$RUN/pods_fractal_v1.py" > "$RUN/step3_fractal.log" 2>&1; then S3="OK"; fi
sed 's/^/  /' "$RUN/step3_fractal.log" 2>/dev/null || true
mark step3-fractal-pods "$S3" "PODS_FRACTAL.json"

# step4 pathway
echo "[loop] step4: pathway record"
S4="SKIP(no-evidence)"
if [ -f "$RUN/QUESTION_TRAVEL.json" ] && [ -f "$RUN/PODS_FRACTAL.json" ] && [ -f "$RUN/friction_report.json" ]; then
  S4="FAIL"
  if python3 bin/pathway_cache_v1.py --root "$PWD" --ledger data/pathway_cache.jsonl record \
      --name "ai-hybrid-${TS}" --actor jesse \
      --step "friction_observer" --step "question_travel" --step "pods_fractal" \
      --evidence "${ABS_RUN}/friction_report.json" \
      --evidence "${ABS_RUN}/QUESTION_TRAVEL.json" \
      --evidence "${ABS_RUN}/PODS_FRACTAL.json" \
      --parent 1 --notes "absolute-path fractal fix; NQ=${NQ}" \
      > "$RUN/step4_pathway.log" 2>&1; then S4="OK"; fi
fi
mark step4-pathway-record "$S4" "see step4_pathway.log"

# step5 PATHWAYS.md
echo "[loop] step5: PATHWAYS.md"
S5="FAIL"
cp PATHWAYS.md "$RUN/PATHWAYS.md.bak" 2>/dev/null || true
if timeout 60 python3 bin/pathway_cache_v1.py --root "$PWD" --ledger data/pathway_cache.jsonl export-md PATHWAYS.md > "$RUN/step5_export.log" 2>&1; then S5="OK"; fi
mark step5-pathways-md "$S5" "see step5_export.log"

# step6 dossier
echo "[loop] step6: auto dossier"
S6="FAIL"
mkdir -p data/sdcard-sync/markor 2>/dev/null || true
[ -f data/sdcard-sync/markor/dossier.md ] && cp data/sdcard-sync/markor/dossier.md "$RUN/dossier.md.bak"
if timeout 120 python3 bin/autodossier_compiler.py > "$RUN/step6_dossier.log" 2>&1 < /dev/null; then S6="OK"; fi
mark step6-auto-dossier "$S6" "see step6_dossier.log"

# finalize
sha256sum "$RUN/friction_report.json" "$RUN/QUESTION_TRAVEL.json" "$RUN/PODS_FRACTAL.json" > "$RUN/EVIDENCE.sha256" 2>/dev/null || true
{
  echo ""; echo "## steps"; echo ""; echo "| step | state | note |"; echo "|---|---|---|"
  i=0; while [ $i -lt ${#STEP_NAMES[@]} ]; do
    echo "| ${STEP_NAMES[$i]} | ${STEP_STATES[$i]} | ${STEP_NOTES[$i]} |"
    i=$((i+1))
  done
  echo ""; echo "## fractal verdict"; echo ""
  grep -E 'verdict|sig\[|wrote ' "$RUN/step3_fractal.log" 2>/dev/null | sed 's/^/  /' || true
  echo ""; echo "_absolute-path hybrid loop — replay by hand._"
} >> "$RECEIPT"

CORE_FAIL=0
for st in "${STEP_STATES[@]}"; do case "$st" in FAIL*) CORE_FAIL=1 ;; esac; done
case "$S4" in SKIP*) CORE_FAIL=1 ;; esac
echo "[loop] receipt: $ABS_RUN/RUN_RECEIPT.md"
echo "[loop] exit_code=$CORE_FAIL"
exit "$CORE_FAIL"
