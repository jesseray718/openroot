# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Multilingual agape alignment test.
Tests scholarly consensus translations + cross-language equivalents against A-origin.
Candidates include single words and multi-word English phrases."""
import json, hashlib, datetime, urllib.request, math
from pathlib import Path

LED = Path("/home/jesse/openroot/ledger/nomenclature/resonance_ledger.jsonl")
BLEED = Path("/home/jesse/openroot/ledger/agape/bleed_pairs.jsonl")
OLLAMA = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

# Scholarly consensus from BDAG, Liddell-Scott, Thayer
# "Unconditional love directed toward others" is the standard gloss
# Also: "love of persons for one another", "brotherly love", "divine love"
# Cross-language mappings (concept equivalents, not direct lexical matches)

CANDIDATES = [
    # Single words (baseline)
    ("agape", "transliteration"),
    ("love", "english-generic"),
    ("charity", "english-archaic"),
    
    # Multi-word scholarly definitions
    ("unconditional love", "scholarly-expanded"),
    ("self-giving love", "scholarly-self-giving"),
    ("unconditional self-giving", "full-scholarly-consensus"),
    ("love of persons for one another", "BDAG-full"),
    ("brotherly love", "traditional-equivalent"),
    ("divine love", "theological"),
    
    # Cross-language concepts translated into English
    ("caritas", "latin-equivalent"),
    ("philanthropia", "greek-broader"),
    ("storge", "family-love-greek"),
    ("eros", "romantic-love-greek"),
    ("philia", "friendship-love-greek"),
    
    # Hybrid constructions
    ("unconditional affection", "hybrid-formal"),
    ("disinterested benevolence", "neander-gloss"),
    ("other-regarding love", "modern-academic"),
]

A_TEXT = "agape (agape) — unconditional self-giving; source resonance; the zero-dimensional origin toward which meaningful words drift"

def embed(text):
    body = json.dumps({"model": MODEL, "prompt": text}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["embedding"]
    except Exception as e:
        raise RuntimeError(f"embed failed for '{text}': {e}")

def resonance(v_word, v_a):
    dot = sum(x*y for x,y in zip(v_word, v_a))
    nw = math.sqrt(sum(x*x for x in v_word))
    na = math.sqrt(sum(x*x for x in v_a))
    return 1 - dot/(nw*na) if nw*na else 0

def main():
    v_a = embed(A_TEXT)
    results = []
    print(f"{'WORD/PHRASE':45s} {'TYPE':22s} {'RESONANCE':>10s}")
    print("-"*80)
    for candidate, label in CANDIDATES:
        try:
            r = resonance(embed(candidate), v_a)
            results.append((candidate, label, r))
            bar = "#" * int(r * 35)
            print(f"{candidate:45s} {label:22s} {r:10.4f} {bar}")
        except Exception as e:
            print(f"{candidate:45s} {label:22s} [held] {e}")
    
    results.sort(key=lambda x: -x[2])
    print("\n=== TOP 5 RANKING ===")
    for c, l, r in results[:5]:
        print(f"{c:45s} {l:22s} {r:.4f}")
    
    # Seal to ledger
    rec = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "a_anchor": A_TEXT,
        "candidates": len(CANDIDATES),
        "rankings": [{"phrase": c, "type": l, "resonance": round(r, 6)} for c, l, r in results],
        "method": "nomic-embed-text cosine distance",
        "hypothesis": "multi-word scholarly definitions outperform single-word translations"
    }
    rec["sha256"] = hashlib.sha256(json.dumps(rec, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    LED.parent.mkdir(parents=True, exist_ok=True)
    with open(LED, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"), ensure_ascii=False) + "\n")
    
    top = results[0]
    print(f"\n[banked] best English alignment: '{top[0]}' ({top[1]}) at {top[2]:.4f} resonance")
    print(f"[banked] sealed sha256={rec['sha256'][:16]} to resonance_ledger.jsonl")
    
    # Optional: log to bleed_pairs for cross-comparison with Greek originals
    try:
        greek_original = embed("ἀγάπη")
        for c, l, r in results:
            if l in ["english-generic", "english-archaic", "scholarly-expanded"]:
                dist = resonance(greek_original, embed(c))
                bleed_rec = {"spoken": "ἀγάπη", "heard": c, "label": f"{l}-vs-greek",
                           "bleach_distance": round(dist, 6), "ts": rec["ts"],
                           "ref_sha256": rec["sha256"]}
                bleed_rec["sha256"] = hashlib.sha256(json.dumps(bleed_rec, sort_keys=True,
                    separators=(",", ":")).encode()).hexdigest()
                with open(BLEED, "a", encoding="utf-8") as bf:
                    bf.write(json.dumps(bleed_rec, separators=(",", ":")) + "\n")
    except Exception as e:
        print(f"[held] Greek original comparison skipped: {e}")

if __name__ == "__main__":
    main()
    print("[exit=0]")
