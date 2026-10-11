#!/usr/bin/env bash
# check_nomic_embed_v1.sh — nomic-embed-text pre-flight: service + model + live embed
# CANARY:OPENROOT-CHECK-NOMIC-V1
# Read-only diagnostics. No state changes.
set -eu
export GIT_PAGER=cat TERM=dumb
OLLAMA="http://localhost:11434"

echo "[gate] stage 0 — Ollama service reachable"
if ! curl -sf --max-time 5 "$OLLAMA/api/version" > /tmp/ollama_ver.json 2>&1; then
  echo "[held] Ollama not reachable at $OLLAMA — check: systemctl --user status ollama / pgrep -af ollama"
  exit 1
fi
echo "[banked] Ollama version: $(cat /tmp/ollama_ver.json)"

echo "[gate] stage 1 — model presence"
MODELS=$(curl -sf --max-time 5 "$OLLAMA/api/tags")
if echo "$MODELS" | grep -q '"nomic-embed-text:latest"'; then
  SIZE=$(echo "$MODELS" | python3 -c "import json,sys; d=json.load(sys.stdin); m=[x for x in d['models'] if 'nomic-embed' in x['name']]; print(m[0]['size']//1024//1024,'MiB') if m else print('?')")
  echo "[banked] nomic-embed-text present ($SIZE)"
else
  echo "[held] nomic-embed-text NOT installed. Available:"
  echo "$MODELS" | python3 -c "import json,sys; [print('  -', m['name']) for m in json.load(sys.stdin)['models']]"
  echo "install: ollama pull nomic-embed-text"
  exit 1
fi

echo "[gate] stage 2 — model detail (params/context)"
curl -sf --max-time 10 "$OLLAMA/api/show" -d '{"model":"nomic-embed-text:latest"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); det=d.get('details',{}); print('[banked] family:',det.get('family','?'),'| param:',det.get('parameter_size','?'),'| ctx:',''.join(p.get('context_length','?') for p in [d.get('model_info',{}).get('nomic.embed.text.context_length')] ) if d.get('model_info') else '?')"
echo

echo "[gate] stage 3 — live embed smoke test (cold/warm timing)"
python3 - <<'PYEOF'
import json, time, urllib.request

def embed(text):
    req = urllib.request.Request(
        "http://localhost:11434/api/embed",
        data=json.dumps({"model": "nomic-embed-text:latest", "input": text}).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    dt = time.time() - t0
    emb = d.get("embeddings", [[]])[0]
    return dt, emb

t1, e1 = embed("OpenCell aerocement thermal absorber panel")
t2, e2 = embed("proof of physical work sha256 ledger")

print(f"[banked] embed #1 (cold-ish): {t1:.2f}s | dim={len(e1)}")
print(f"[banked] embed #2 (warm):      {t2:.2f}s | dim={len(e2)}")

# sanity: nonzero vector, correct dimensionality (nomic-embed-text = 768)
assert len(e1) == 768, f"unexpected dimension: {len(e1)}"
assert any(abs(v) > 1e-6 for v in e1), "zero vector returned"

# cosine similarity between unrelated texts (sanity: should be low-mid, not ~1)
dot = sum(a*b for a,b in zip(e1,e2))
n1 = sum(a*a for a in e1) ** 0.5
n2 = sum(a*a for a in e2) ** 0.5
sim = dot/(n1*n2)
print(f"[banked] cosine(unrelated pair) = {sim:.3f} (expect < ~0.5 for sanity)")

print("[gate] ALL CHECKS PASSED — nomic-embed-text operational")
PYEOF

echo "[gate] stage 4 — memory footprint"
ps aux | grep -i '[o]llama' | awk '{printf "[banked] ollama pid=%s rss=%.0fMiB cpu=%s%%\n", $2, $6/1024, $3}'

echo "[exit=0]"
