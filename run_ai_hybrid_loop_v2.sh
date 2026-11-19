#!/usr/bin/env bash
# OpenRoot Hybrid Tiny Loop v2 — Newton Chain + PoPW thermal + pods-aware
set -u
ROOT="$HOME/openroot"
cd "$ROOT" || exit 2
export OPENROOT_ROOT="$ROOT"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN="data/outbox/ai_hybrid_loop/${TS}"
mkdir -p "$RUN" ledger data
RECEIPT="$RUN/RUN_RECEIPT.md"
MODELS_TRY="${MODELS_TRY:-qwen2.5-coder:0.5b smollm2:1.7b qwen2.5:1.5b}"
NQ="${NQ:-1}"
export MODELS_TRY NQ TS RUN

python3 bin/popw_thermal_ledger.py init >/dev/null

{
  echo "# AI HYBRID LOOP v2 — $TS (Newton+PoPW fused)"
  echo "- host: $(hostname)"
  echo "- root: $ROOT"
  echo "- models: $MODELS_TRY"
  echo "- pods dir: $(ls -d /home/jesse/pods 2>/dev/null || echo absent)"
  echo "- fulltext state: $(ls -d $HOME/.local/state/openroot-fulltext-v2 2>/dev/null || echo absent)"
} > "$RECEIPT"

echo "[v2] discovery against live pods + fulltext indexes"
python3 - << 'PY'
import json, os, time, urllib.request, sqlite3, re, collections, pathlib
ROOT = pathlib.Path("/home/jesse/openroot")
PODS = pathlib.Path("/home/jesse/pods")
FTS_STATE = pathlib.Path.home() / ".local/state/openroot-fulltext-v2"
MODELS = os.environ.get("MODELS_TRY", "qwen2.5-coder:0.5b").split()
NQ = int(os.environ.get("NQ", "1"))
RUN = pathlib.Path(os.environ["RUN"])
TS = os.environ["TS"]

candidates = []
# 1. fulltext ordinary pods (preferred)
if FTS_STATE.exists():
    for name in ("knowledge.pod.sqlite3", "system.pod.sqlite3", "manual.pod.sqlite3"):
        p = FTS_STATE / name
        if p.is_file():
            candidates.append(str(p))
# 2. any pod.db under /home/jesse/pods
if PODS.exists():
    for p in sorted(PODS.rglob("pod.db")):
        candidates.append(str(p))
# 3. openroot data FTS fallbacks
for name in ("universal_lattice_fts5.db", "data/fts_index.db", "data/mesh_index.db", "data/canonical_index.db"):
    p = ROOT / name
    if p.exists():
        candidates.append(str(p))

db = candidates[0] if candidates else None
doc = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "db": db,
    "candidates": candidates[:12],
    "questions": [],
    "models_tried": MODELS,
    "pod_root": str(PODS) if PODS.exists() else None,
    "fulltext_state": str(FTS_STATE) if FTS_STATE.exists() else None,
}
if not db:
    doc["error"] = "no fts/pod db found"
    json.dump(doc, open(RUN / "travel.json", "w"), indent=2)
    print(json.dumps({"error": "no db", "candidates": candidates}))
    raise SystemExit(0)

conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
conn.execute("PRAGMA query_only=1")
cur = conn.cursor()

# Prefer FTS5 virtual tables that look like the fulltext schema
tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%' OR name='words'")]
tab = None
for candidate in ("words", "chunks_fts", "chunks"):
    if candidate in tabs:
        tab = candidate
        break
if not tab and tabs:
    tab = tabs[0]
if not tab:
    tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    tab = tabs[0] if tabs else None
if not tab:
    doc["error"] = "no usable table"
    json.dump(doc, open(RUN / "travel.json", "w"), indent=2)
    raise SystemExit(0)

# Locate a text column
cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{tab}")')]
tcol = None
best = -1
for c in cols:
    try:
        L = cur.execute(f'SELECT sum(length("{c}")) FROM (SELECT "{c}" FROM "{tab}" LIMIT 80)').fetchone()[0] or 0
        if L > best:
            best, tcol = L, c
    except Exception:
        pass
if not tcol:
    tcol = "body" if "body" in cols else (cols[0] if cols else "text")

n = cur.execute(f'SELECT count(*) FROM "{tab}"').fetchone()[0]
doc.update({"fts_table": tab, "text_col": tcol, "rows": n})

avail = set()
try:
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
        avail = {m["name"] for m in json.load(r).get("models", [])}
except Exception:
    pass
doc["ollama_available"] = sorted(avail)

hits = 0
for i in range(NQ):
    off = max(0, (n // (NQ + 1)) * (i + 1)) if n else 0
    try:
        row = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" ORDER BY rowid LIMIT 1 OFFSET ?', (off,)).fetchone()
    except Exception:
        row = None
    if not row:
        continue
    src_rid, src_txt = row
    stop = set("the a an and or of to in on for with is are was were be been this that these those it its as at by from not but if then than so such can could will would should may might must have has had do does did about into over under between within without their there here what which who whom whose when where why how all any each few more most other some only own same too very just also".split())
    prefer = {"openroot","newton","aerocement","aero","popw","ledger","eta","joule","postulate","chain","thermal","resonance","agape","pod","fts","pathway","receipt","attest","derived","stirling","labyrinth","blacklocust","permaculture","merkle","genesis","constitution","bounty"}
    words = [w for w in re.findall(r"[a-zA-Z]{4,}", (src_txt or "").lower()) if w not in stop]
    counts = collections.Counter(words)
    # boost preferred terms heavily when they appear
    boosted = []
    for w, c in counts.most_common(40):
        score = c * (8 if w in prefer else 1)
        boosted.append((score, w))
    boosted.sort(reverse=True)
    top = [w for _, w in boosted[:4]]
    if not top:
        continue
    q = "What does the corpus say about " + ", ".join(top[:3]) + "?"
    query = " OR ".join(f'"{t}"' for t in top[:4])
    try:
        if tab in ("words",) or "fts" in tab.lower():
            res = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" WHERE "{tab}" MATCH ? ORDER BY rank LIMIT 5', (query,)).fetchall()
        else:
            res = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" WHERE "{tcol}" LIKE ? LIMIT 5', (f"%{top[0]}%",)).fetchall()
    except Exception:
        res = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" WHERE "{tcol}" LIKE ? LIMIT 5', (f"%{top[0]}%",)).fetchall()
    rids = [r[0] for r in res]
    hit = src_rid in rids
    hits += int(hit)
    ctx = "\n\n---\n\n".join(f"[chunk {r[0]}] {(r[1] or '')[:500]}" for r in res[:3])
    prompt = f"Answer strictly from the context. If missing reply exactly: NOT_IN_CONTEXT.\n\nQuestion: {q}\n\nContext:\n{ctx}\n\nAnswer (max 3 sentences):"
    ans = {"status": "UNAVAILABLE", "model": None, "text": "", "elapsed_s": None}
    for m in MODELS:
        if m not in avail:
            continue
        body = json.dumps({"model": m, "prompt": prompt, "stream": False, "options": {"num_predict": 120, "temperature": 0.15}}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                out = json.load(r)
            ans = {"status": "OK", "model": m, "text": (out.get("response") or "").strip()[:400], "elapsed_s": round(time.time() - t0, 1)}
            break
        except Exception as e:
            ans = {"status": f"ERR {type(e).__name__}", "model": m, "text": "", "elapsed_s": None}
    doc["questions"].append({"idx": i, "source_rowid": src_rid, "question": q, "recall_hit": hit, "answer": ans})

doc["summary"] = {"questions": NQ, "recall_hits": hits, "answered_ok": sum(1 for x in doc["questions"] if x["answer"]["status"] == "OK")}
json.dump(doc, open(RUN / "travel.json", "w"), indent=2)
print(json.dumps(doc["summary"]))
print("db_used:", db)
print("candidates:", len(candidates))
print("pods_seen:", len(list(PODS.iterdir())) if PODS.exists() else 0)
print("fulltext_pods:", sum(1 for n in ("knowledge","system","manual") if (FTS_STATE / f"{n}.pod.sqlite3").exists()) if FTS_STATE.exists() else 0)
PY

# Write PoPW record from the travel result
python3 - << PY
import json, pathlib, subprocess, os
ROOT = pathlib.Path("/home/jesse/openroot")
run = pathlib.Path(os.environ["RUN"])
travel_path = run / "travel.json"
if not travel_path.exists():
    print("no travel.json — skip PoPW")
    raise SystemExit(0)
travel = json.load(open(travel_path))
summary = travel.get("summary", {})
hits = summary.get("recall_hits", 0)
ok = summary.get("answered_ok", 0)
useful = 1.0 if (hits > 0 or ok > 0) else 0.0
human = 0.9
payload = {
    "cycle_id": os.environ["TS"],
    "models": travel.get("models_tried", []),
    "recall_hits": hits,
    "questions": summary.get("questions"),
    "evidence": [str(travel_path)],
    "pod_root": travel.get("pod_root"),
    "db_used": travel.get("db"),
}
subprocess.check_call(["python3", str(ROOT / "bin" / "popw_thermal_ledger.py"), "add",
                       json.dumps(payload), str(human), str(useful)])
print(f"PoPW sealed: hits={hits} ok={ok} useful={useful} db={travel.get('db')}")
PY

echo "" >> "$RECEIPT"
python3 bin/popw_thermal_ledger.py tip >> "$RECEIPT"
echo "[v2] receipt: $RECEIPT"
python3 bin/popw_thermal_ledger.py verify
echo "[v2] cycle sealed next to pods"
ls -la /home/jesse/pods 2>/dev/null | head -8 || echo "no /home/jesse/pods yet"
ls -la "$HOME/.local/state/openroot-fulltext-v2"/*.pod.sqlite3 2>/dev/null | head -5 || echo "no fulltext pods yet"
exit 0
