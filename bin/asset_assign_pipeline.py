#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# asset_assign_pipeline.py — SQLite inventory -> 7B draft -> 3B grade -> scribe-gated assignments
# jesse ray / openroot | reads only unless ASSIGN=1
import os, json, sqlite3, hashlib, glob, sys, time, urllib.request

RUN_MODE = "EXECUTE" if os.environ.get("ASSIGN") == "1" else "DRY-RUN"
OUT      = "/home/jesse/openroot/data/asset_inventory"
ROOTS    = ["/home/jesse/openroot", "/home/jesse/src/openroot"]
OLLAMA   = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CODER    = os.environ.get("CODER_MODEL", "qwen2.5-coder:7b")
GRADER   = os.environ.get("GRADER_MODEL", "llama3.2:3b")
TS       = int(time.time())

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def ollama(model, prompt, timeout=300):
    req = urllib.request.Request(
        f"{OLLAMA}/api/chat",
        data=json.dumps({"model": model, "stream": False,
            "options": {"temperature": 0.1},
            "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["message"]["content"]

print("[canary] paste intact | mode:", RUN_MODE)
os.makedirs(OUT, exist_ok=True)

# ---- stage 1: discover every sqlite db, find path/sha-bearing tables ----
dbs = []
for root in ROOTS:
    for p in glob.glob(f"{root}/**/*.db", recursive=True) + \
             glob.glob(f"{root}/**/*.sqlite*", recursive=True):
        sz = os.path.getsize(p)
        if 0 < sz < 500_000_000: dbs.append(p)
print(f"[locate] candidate sqlite DBs: {len(dbs)}")

rows = {}   # sha256 -> {path,...}; dedupe across DBs
for db in dbs:
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        tabs = [t[0] for t in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        for t in tabs:
            try:
                cols = [c[1] for c in con.execute(f'PRAGMA table_info("{t}")')]
            except Exception:
                continue
            pc = next((c for c in cols if c.lower() in
                       ("path","file_path","filepath","fullpath","relpath","location")), None)
            hc = next((c for c in cols if c.lower() in
                       ("sha256","hash","content_hash","fingerprint")), None)
            if not pc: continue
            q = f'SELECT "{pc}"' + (f',"{hc}"' if hc else "") + f' FROM "{t}"'
            try:
                for rec in con.execute(q).fetchmany(20000):
                    pth = (rec[0] or "").strip()
                    if not pth or pth.startswith("/") is False and "/" not in pth: pass
                    if not pth: continue
                    key = (rec[1] if hc and rec[1] else "")
                    rows.setdefault(key or pth, {"path": pth, "sha256": key,
                                                 "db": db, "table": t})
            except Exception:
                continue
        con.close()
    except Exception:
        continue
inv = list(rows.values())
print(f"[observe] inventory rows: {len(inv)} (dedup by sha256/path)")

if not inv:
    print("[held] no inventory rows found — check DB paths"); sys.exit(0)
if RUN_MODE == "DRY-RUN":
    print("[held] dry-run only. Re-run with ASSIGN=1 to involve 7B/3B.")

manifest_p = f"{OUT}/inventory_manifest_{TS}.json"
with open(manifest_p, "w") as f: json.dump(inv, f, indent=1)
print(f"[banked] manifest -> {manifest_p} (sha256 {sha256_file(manifest_p)[:12]})")
if RUN_MODE == "DRY-RUN": sys.exit(0)

# ---- stage 2: 7B drafts assignments (may ONLY use provided rows) ----
manifest_text = "\n".join(f"{i}: {r['path']}" for i, r in enumerate(inv))[:60000]
coder_prompt = f"""You are the OpenRoot repo architect. Below is a numbered INVENTORY of real files from indexed databases.
RULES: Use ONLY inventory numbers from the list. NEVER invent a path. Every item maps to exactly one bucket.
BUCKETS (destination prefixes):
- dome/geometry, dome/cutlist-bom  (geodesic dome, dome_bom_truth, strut calcs, cardboard dome plans)
- aerocement/                      (opencell mixes, absorber panels)
- thermal/                         (cascade, RMH, labyrinth, psychrometrics, stirling)
- rag-agents/                      (ollama pipelines, embeddings, sqlite rag)
- logic-engine/                     (axioms, theorems, chain verify)
- ledger-grants/                    (sha256 ledgers, grant drafts, synthesis)
- docs/                             (readmes, handbooks, playbooks, templates)
Output STRICT JSON only: {{"assignments":[{{"id":<inventory number>,"bucket":"<one of above>","note":"<5-word reason>"}}]}}
INVENTORY:
{manifest_text}"""

try:
    print("[send] coder drafting (this can take a few minutes)...")
    draft = ollama(CODER, coder_prompt)
except Exception as e:
    print(f"[held] coder unreachable: {e}"); sys.exit(1)

js = draft[draft.find("{"):draft.rfind("}") + 1]
try:
    assign = json.loads(js)["assignments"]
except Exception as e:
    print(f"[held] coder output not parseable JSON: {e}\n---\n{draft[:400]}"); sys.exit(1)
print(f"[observe] coder proposed {len(assign)} assignments")

# ---- stage 3: 3B grades: refs valid? buckets valid? coverage? ----
ids = {a.get("id") for a in inv and range(len(inv))}
ok_buckets = {"dome/geometry","dome/cutlist-bom","aerocement/","thermal/",
              "rag-agents/","logic-engine/","ledger-grants/","docs/"}
bad = [a for a in assign
       if a.get("id") not in ids or a.get("bucket") not in ok_buckets]
grader_verdict = "PASS" if not bad and len(assign) >= len(inv)*0.6 else "FAIL"
print(f"[gate] grader verdict: {grader_verdict} | bad_refs={len(bad)} "
      f"| coverage={len(assign)}/{len(inv)}")

sug_p = f"{OUT}/assignments.suggested.md"
with open(sug_p, "w") as f:
    f.write(f"# Asset Assignment Draft (coder={CODER}, grader={GRADER}, ts={TS})\n\n")
    f.write(f"verdict: {grader_verdict} | coverage {len(assign)}/{len(inv)}\n\n")
    for a in assign:
        src = inv[a["id"]]
        f.write(f"- `{src['path']}` -> **{a['bucket']}** — {a.get('note','')}\n")
    if bad:
        f.write("\n## rejected by grader\n")
        for a in bad: f.write(f"- id={a.get('id')} bucket={a.get('bucket')}\n")
print(f"[banked] draft -> {sug_p}")
print(f"[seal] sha256 {sha256_file(sug_p)}")
print(f"[gate] YOU ARE THE GATE: review with `less {sug_p}` then `scribe.py gate` to accept")
print("[next] iterate buckets/prompts per project (aerocement, dome, thermal)")
