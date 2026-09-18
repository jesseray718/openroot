#!/usr/bin/env python3
# asset_preclassify_v2.py — pass-2 rules (extensions, dirs, skips) + shelves
# then optional ASSIGN=1: chunked 7B propose-from-shelf -> 3B grade -> scribe gate
import json, glob, os, hashlib, sys, time, urllib.request

INV      = "/home/jesse/openroot/data/asset_inventory"
MODE     = "EXECUTE" if os.environ.get("ASSIGN") == "1" else "DRY-RUN"
OLLAMA   = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CODER    = os.environ.get("CODER_MODEL", "qwen2.5-coder:7b")
GRADER   = os.environ.get("GRADER_MODEL", "llama3.2:3b")
TS       = int(time.time())
CHUNK    = int(os.environ.get("CHUNK", "150"))

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def ollama(model, prompt, timeout=None):
    timeout = timeout or int(os.environ.get("TIMEOUT", "420"))
    req = urllib.request.Request(f"{OLLAMA}/api/chat",
        data=json.dumps({"model": model, "stream": False,
             "options": {"temperature": 0.1},
             "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["message"]["content"]

print("[canary] paste intact | mode:", MODE)
newest = max(glob.glob(f"{INV}/inventory_manifest_*.json"), key=os.path.getmtime)
inv = json.load(open(newest))

KW = [  # pass-1 buckets + widened dome/aerocement vocab (longest keyword wins)
    ("dome/cutlist-bom",  ["cutlist","cut_list","bill_of_material","cardboard_dome","cardboard","strut_bom","bom"]),
    ("dome/geometry",     ["dome_bom","geodesic","icosahedron","strut","chord_factor","dome_freq","dome","sphere_identity","v2_dome"]),
    ("aerocement/",       ["aerocement","aero_cement","opencell","open_cell","absorber","ferrocement","ferro","cement_mix","blackbody"]),
    ("thermal/",          ["thermal","cascade","rmh","rocket_mass","labyrinth","psychrometric","stirling","uplift","ach_","cooling","desiccant","solar"]),
    ("rag-agents/",       ["rag","embedding","nomic","ollama","aider","vector","retrieval","embed"]),
    ("logic-engine/",     ["axiom","theorem","postulate","chain_verify","proof","canon","merkle","definition"]),
    ("ledger-grants/",    ["ledger","grant","synthesis","acre","popw","attest","scribe","session_seed","cosmic"]),
    ("docs/",             ["readme","handbook","guide","playbook","template","contribut","thesis"]),
]
SKIP = ["__pycache__",".pyc",".egg-info","/build/",".bak",".sync-conflict",".git/","gguf"]
EXT = [(".py","scripts/"),(".sh","scripts/"),(".rs","scripts/"),
       (".md","docs/"),(".txt","docs/"),(".pdf","docs/"),
       (".json","data/"),(".jsonl","data/"),(".csv","data/"),(".tsv","data/"),
       (".log","logs/"),(".tar","archive/"),(".xz","archive/")]

def route(path):
    p = path.lower()
    if any(s in p for s in SKIP): return "archive/skip"
    hits = {}
    for b, kws in KW:
        for k in kws:
            if k in p: hits[b] = hits.get(b, 0) + len(k)  # weighted vote
    if hits: return max(hits, key=hits.get)
    for e, b in EXT:
        if p.endswith(e): return b
    return "shelves/"

for r in inv: r["bucket"] = route(r["path"])

from collections import Counter
c = Counter(r["bucket"] for r in inv)
print(f"[observe] total={len(inv)}")
for b, n in c.most_common(): print(f"  {b:<18} {n}")

json.dump(inv, open(f"{INV}/preclassified_v2.json","w"), indent=1)
print(f"[banked] preclassified_v2.json -> {INV}")

shelf = [r for r in inv if r["bucket"] == "shelves/"]
print(f"[observe] shelf (coder work queue) = {len(shelf)}")
if MODE == "DRY-RUN" or not shelf:
    print("[held] dry-run. Tighten rules & re-run (free), or ASSIGN=1 to let 7B work the shelf")
    sys.exit(0)

# ---- chunked coder stage: propose promotions OUT of shelves only ----
buckets = [b for b,_ in KW] + ["scripts/","data/","logs/"]
promotions, fails = [], 0
for i in range(0, len(shelf), CHUNK):
    chunk = shelf[i:i+CHUNK]
    listing = "\n".join(f"{j}: {r['path']}" for j, r in enumerate(chunk))
    prompt = f"""Sort these files. Use ONLY the numbers given. Each file gets ONE bucket.
BUCKETS: {buckets}
If a file truly fits none, use bucket "shelves/". Output STRICT JSON only:
{{"moves":[{{"id":<num>,"bucket":"<bucket>"}}]}}
FILES:
{listing}"""
    try:
        out = ollama(CODER, prompt)
        js = out[out.find("{"):out.rfind("}")+1]
        moves = json.loads(js)["moves"]
    except Exception as e:
        print(f"[held] chunk {i//CHUNK}: coder fail ({e}) — skipping, shelf stays"); fails += 1
        continue
    valid = [m for m in moves if 0 <= m.get("id", -1) < len(chunk)
             and m.get("bucket") in buckets + ["shelves/"]]
    print(f"[send] chunk {i//CHUNK}: {len(valid)}/{len(chunk)} valid proposals")
    for m in valid:
        if m["bucket"] != "shelves/":
            promotions.append({"path": chunk[m["id"]]["path"],
                               "from": "shelves/", "to": m["bucket"]})

# ---- 3B grade: sample-audit the aggregated proposal table ----
audit_prompt = """Audit this file->bucket mapping list. Reply STRICT JSON:
{"verdict":"PASS"} if mappings look plausible for the bucket names,
{"verdict":"FAIL","reason":"..."} otherwise. Sample a few lines and judge.
""" + "\n".join(f"{p['path']} -> {p['to']}" for p in promotions[:200])
try:
    g = ollama(GRADER, audit_prompt)
    verdict = "FAIL" if '"FAIL"' in g else "PASS"
except Exception:
    verdict = "NO-GRADE (grader down; proposals held, not applied)"

sug = f"{INV}/assignments.suggested.md"
with open(sug, "w") as f:
    f.write(f"# Shelf Promotion Proposal v2 (ts={TS})\n\n")
    f.write(f"- deterministic routed: {len(inv)-len(shelf)}\n- shelf: {len(shelf)}\n")
    f.write(f"- coder chunks failed: {fails}\n- promotions proposed: {len(promotions)}\n")
    f.write(f"- grader verdict: {verdict}\n\n## Proposed moves\n")
    for p in promotions: f.write(f"- `{p['path']}` -> **{p['to']}**\n")
print(f"[gate] grader verdict: {verdict} | promotions={len(promotions)} | failed_chunks={fails}")
print(f"[banked] {sug}")
print(f"[seal] sha256 {sha(sug)}")
print("[gate] YOU ARE THE GATE: `less` it, then scribe.py gate to apply")
