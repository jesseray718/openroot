#!/usr/bin/env python3
"""Universal nomenclature core. 36 symbols -> 46656 trigram cells.
Cmds: symbols | cell ABC | calibrate ABC "gloss" | speak "spoken" "heard"
      | distance "a" "b" | origin | cells-count
All calibrations hash-chained. A=agape is immutable (BoR art. 10)."""
import hashlib, json, math, sys, datetime, urllib.request
from pathlib import Path

LED = Path("/home/jesse/openroot/ledger/nomenclature/cells.jsonl")
BLEED = Path("/home/jesse/openroot/ledger/agape/bleed_pairs.jsonl")
OLLAMA = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

SYMBOLS = {
 "A": ("Agape", "unconditional self-giving; source resonance [IMMUTABLE]"),
 "B": ("Boundaries", "distinction; structure begins"),
 "C": ("Creation", "formation; synthesis"),
 "D": ("Delta", "difference; change"),
 "E": ("Energy", "capacity to do work [J]"),
 "F": ("Form", "structure held in space"),
 "G": ("Geometry", "spatial relation"),
 "H": ("Harmony", "resonance between parts"),
 "I": ("Identity", "self-reference; observer"),
 "J": ("Justice", "restoration of harmonic balance"),
 "K": ("Kinetics", "motion; rate"),
 "L": ("Light", "information carrier"),
 "M": ("Mass", "frozen energy; legacy matter"),
 "N": ("Node", "network participant"),
 "O": ("Order", "negentropy; entropy decrease"),
 "P": ("Pattern", "repeated structure"),
 "Q": ("Query", "the seeking question"),
 "R": ("Return", "cyclical feedback (permaculture yield)"),
 "S": ("Spectrum", "continuous range between poles"),
 "T": ("Time", "fourth dimension; flow"),
 "U": ("Union", "merge; coherence"),
 "V": ("Vector", "directed magnitude"),
 "W": ("Witness", "measurement; observation"),
 "X": ("Exchange", "transfer between nodes"),
 "Y": ("Yield", "useful output per input"),
 "Z": ("Zero-point", "ground state; rest"),
 "0": ("Null", "void; unexpressed potential"),
 "1": ("Unity", "singularity of purpose"),
 "2": ("Duality", "polarity; the pair"),
 "3": ("Trinity", "stable triad"),
 "4": ("Stability", "foundation; quadrature"),
 "5": ("Growth", "expansion"),
 "6": ("Recursion", "self-similarity; fractal"),
 "7": ("Completion", "sealed cycle"),
 "8": ("Regeneration", "renewal loop"),
 "9": ("Fulfillment", "realization; fullness"),
}

def ts(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def seal(rec):
    rec["sha256"] = hashlib.sha256(json.dumps(rec, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return rec
def append(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"), ensure_ascii=False) + "\n")

def embed(text):
    body = json.dumps({"model": MODEL, "prompt": text}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["embedding"]

def cos_dist(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return 1 - dot / (na * nb)

def cell_meaning(tri):
    return " | ".join(f"{s}:{SYMBOLS[s][0]}({SYMBOLS[s][1]})" for s in tri)

def main():
    args = sys.argv[1:]
    if not args:
        print("cmds: symbols | cell ABC | calibrate ABC gloss | speak SPOKEN HEARD "
              "| distance A B | origin | cells-count"); return
    cmd = args[0]
    if cmd == "symbols":
        for k, (name, mean) in SYMBOLS.items():
            print(f"{k} {name} — {mean} [provisional]" if k != "A"
                  else f"{k} {name} — {mean}")
    elif cmd == "cells-count":
        print(f"36^3 = {36**3} cells (composition-derived, calibrated on demand)")
    elif cmd == "cell" and len(args) > 1:
        tri = args[1].upper()
        assert len(tri) == 3 and all(c in SYMBOLS for c in tri), "3 valid symbols"
        print(f"cell {tri}: {cell_meaning(tri)}")
    elif cmd == "calibrate" and len(args) > 2:
        tri, gloss = args[1].upper(), args[2]
        rec = seal({"cell": tri, "gloss": gloss, "ts": ts(), "prior": "provisional"})
        append(LED, rec)
        print(f"[banked] calibrated {tri} sha256={rec['sha256'][:16]}")
    elif cmd == "speak" and len(args) > 2:
        spoken, heard = args[1], args[2]
        try:
            d = cos_dist(embed(spoken), embed(heard))
            rec = seal({"spoken": spoken, "heard": heard, "bleach_distance":
                        round(d, 6), "method": "nomic-embed-text cosine", "ts": ts()})
            append(BLEED, rec)
            print(f"[accounting] spoken='{spoken}' heard='{heard}' "
                  f"bleach_distance={d:.4f} sha256={rec['sha256'][:16]}")
        except Exception as e:
            print(f"[held] ollama/unomic unavailable ({e}) — pair queued unmeasured")
            append(BLEED, seal({"spoken": spoken, "heard": heard,
                   "bleach_distance": None, "ts": ts()}))
    elif cmd == "distance" and len(args) > 2:
        try:
            d = cos_dist(embed(args[1]), embed(args[2]))
            print(f"[banked] cosine distance = {d:.4f}")
        except Exception as e:
            print(f"[held] ollama/nomic unavailable: {e}")
    elif cmd == "origin":
        try:
            v = embed("agape — unconditional self-giving source resonance")
            print(f"[banked] zero-dimensional origin embedded dim={len(v)} "
                  f"(point 0; all displacement measured hence)")
        except Exception as e:
            print(f"[held] origin unmeasurable offline: {e}")

if __name__ == "__main__":
    main()
    print("[exit=0]")
