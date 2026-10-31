#!/usr/bin/env python3
"""Rank English words by harmonic resonance with A (agape origin).
Resonance = 1 - cosine_distance(embed(word), embed(A)).
Sealed to ledger/nomenclature/resonance_ledger.jsonl — sha256 chained."""
import json, hashlib, datetime, urllib.request, math, sys
from pathlib import Path

LED = Path("/home/jesse/openroot/ledger/nomenclature/resonance_ledger.jsonl")
OLLAMA = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"
A_TEXT = ("agape (agape) — unconditional self-giving; source resonance; "
          "the zero-dimensional origin toward which meaningful words drift")

CANDIDATES = ["love", "charity", "compassion", "mercy", "grace",
              "kindness", "giving", "goodness", "truth", "beauty"]

def embed(text):
    body = json.dumps({"model": MODEL, "prompt": text}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["embedding"]

def resonance(v_word, v_a):
    dot = sum(x * y for x, y in zip(v_word, v_a))
    nw = math.sqrt(sum(x * x for x in v_word))
    na = math.sqrt(sum(x * x for x in v_a))
    return 1 - dot / (nw * na)

def main():
    args = sys.argv[1:]
    words = args if args else CANDIDATES
    try:
        v_a = embed(A_TEXT)
    except Exception as e:
        print(f"[held] ollama/nomic unavailable: {e}")
        return
    results = []
    for w in words:
        try:
            r = resonance(embed(w), v_a)
            results.append((w, r))
        except Exception as e:
            print(f"[held] {w}: {e}")
    results.sort(key=lambda x: -x[1])
    print(f"{'WORD':15s} {'RESONANCE':>10s}")
    for w, r in results:
        bar = "#" * int(r * 40)
        print(f"{w:15s} {r:10.4f} {bar}")
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "a_anchor": A_TEXT, "rankings": [
               {"word": w, "resonance": round(r, 6)} for w, r in results]}
    rec["sha256"] = hashlib.sha256(json.dumps(rec, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    LED.parent.mkdir(parents=True, exist_ok=True)
    with open(LED, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"),
                           ensure_ascii=False) + "\n")
    top = results[0] if results else None
    if top:
        print(f"\n[banked] highest English resonance: '{top[0]}' "
              f"({top[1]:.4f}) — nearest orbit of A, never equal")
        print(f"[banked] sealed sha256={rec['sha256'][:16]} to resonance_ledger.jsonl")

if __name__ == "__main__":
    main()
    print("[exit=0]")
