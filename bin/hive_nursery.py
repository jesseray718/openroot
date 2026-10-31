#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""hive_nursery v1 — warming staging area + certified tiniest-capable hive.
Warms installed models, runs falsifiable talent probes, elects per-class leaders,
emits data/hive_registry.json consumed by multi_router --registry.
"""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
REGISTRY = os.path.join(ROOT, "data", "hive_registry.json")

def api(path, body=None, timeout=180):
    req = urllib.request.Request(OLLAMA_BASE + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def gen(model, prompt, opts=None):
    b = {"model": model, "prompt": prompt, "stream": False}
    if opts: b.update(opts)
    t0 = time.time(); out = api("/api/generate", b)["response"]
    return out, (time.time()-t0)*1000

# talent probes — falsifiable: regex verdict, no vibes
PROBES = {
 "classify": ("Reply with the single word CODE and nothing else.",
              lambda o: bool(re.search(r"\bCODE\b", o.strip()[:20]))),
 "code-edit": ("Fix this code. Output ONLY the corrected code, nothing else:\nfor i in range(10)\n    print(i\n",
               lambda o: "range(10):" in o and "print(i)" in o and len(o.strip()) < 400),
 "draft":     ("Write one sentence containing the word lattice.",
               lambda o: "lattice" in o.lower() and 3 < len(o.split()) < 60),
 "outline":   ("Output exactly two lines each starting with SUBTASK:",
               lambda o: len([l for l in o.splitlines() if l.strip().startswith("SUBTASK:")]) >= 2),
 "scope-reject": ("You are a code editor. Someone asks: write a poem about cats. "
                  "Reply with exactly: [OUT-OF-SCOPE]",
                  lambda o: "OUT-OF-SCOPE" in o),
}

def size_of(tag):  # rough param estimate from tag name
    for suf in ("-instruct", ":free"): tag = tag.replace(suf, "")
    m = re.search(r"(\d+(?:\.\d+)?)b", tag.lower())
    if m: return float(m.group(1))
    if "embed" in tag.lower() or "nomic" in tag.lower(): return 0.1
    return 8.0  # unknown => treated as big

def main():
    print(f"[BOOT] hive nursery — ollama_base={OLLAMA_BASE}")
    try:
        installed = [m["name"] for m in api("/api/tags", timeout=10).get("models", [])]
    except Exception as e:
        print(f"[DEAD] ollama unreachable ({type(e).__name__}) — set OLLAMA_HOST from termux. Nothing certified."); return 1
    print(f"[INVENTORY] {len(installed)} installed: {', '.join(installed)}")
    print("[STAGE:warm] keeping every model hot (keep_alive 30m) before probing")
    for m in installed:
        try: gen(m, "", {"keep_alive": "30m"}); print(f"  [WARM] {m}")
        except Exception as e: print(f"  [HELD-WARM] {m}: {type(e).__name__}")
    registry = {"generated": datetime.now(timezone.utc).isoformat(),
                "ollama_base": OLLAMA_BASE, "classes": {}}
    print("[STAGE:certify] falsifiable talent probes — a file that survived != a product")
    for m in installed:
        if "embed" in m.lower():  # embeddings certified separately
            try:
                t0=time.time(); d=len(api("/api/embeddings",
                    {"model": m, "input": "probe"})["embedding"]); ms=(time.time()-t0)*1000
                registry["classes"].setdefault("embed", []).append(
                    {"model": m, "params_b": size_of(m), "ms": round(ms,1),
                     "verdict": "PASS" if d > 0 else "FAIL-zerodim"})
                print(f"  {m} [embed] PASS {ms:.0f}ms ({d}-dim)")
            except Exception as e: print(f"  {m} [embed] FAIL {type(e).__name__}")
            continue
        for cls, (prompt, check) in PROBES.items():
            try:
                out, ms = gen(m, prompt, {"keep_alive": "30m"})
                ok = check(out)
                registry["classes"].setdefault(cls, []).append(
                    {"model": m, "params_b": size_of(m), "ms": round(ms,1),
                     "verdict": "PASS" if ok else "FAIL"})
                print(f"  {m} [{cls}] {'PASS' if ok else 'FAIL'} {ms:.0f}ms :: {out.strip()[:40]!r}")
            except Exception as e:
                print(f"  {m} [{cls}] FAIL {type(e).__name__}")
    print("[STAGE:elect] tiniest-capable equivalent per class = min(params among PASS, tie->fastest)")
    for cls in list(registry["classes"]):
        rows = registry["classes"][cls]              # list of probe rows
        registry["classes"][cls] = {"rows": rows}    # wrap: multi_router reads [cls]["elected"]
        passing = [r for r in rows if r["verdict"] == "PASS"]
        if passing:
            lead = sorted(passing, key=lambda r: (r["params_b"], r["ms"]))[0]
            registry["classes"][cls]["elected"] = lead
            print(f"  [{cls}] -> {lead['model']} ({lead['params_b']}b, {lead['ms']}ms) "
                  f"[{len(passing)}/{len(rows)} certified]")
        else:
            print(f"  [{cls}] NO LEADER — zero certified, class stays on the big model or lumo lane")
    with open(REGISTRY, "w") as f: json.dump(registry, f, indent=2)
    print(f"[BANKED] registry {REGISTRY}")
    print("[CANARY] hive-nursery-certified")
    return 0

if __name__ == "__main__": sys.exit(main())
