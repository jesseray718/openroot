#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# model_symposium.py — model-to-model Q&A rounds over the RAG index to surface
# leverageable synergies. 3B probes, 7B grounds in retrieved context, 3B grades.
# Output: leverage_report.md ranked by "eta gain" estimate.
# Jesse Ray / OpenRoot v1.0 | runs against agape_rag.db, degrades gracefully if empty
import os, sys, json, re, time, sqlite3, struct, math, glob, urllib.request
from datetime import datetime

OLLAMA    = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
BIG_MDL   = os.environ.get("BIG_MODEL",  "qwen2.5-coder:7b")
SMALL_MDL = os.environ.get("SMALL_MODEL", "qwen2.5:3b")
ROUNDS    = int(os.environ.get("ROUNDS", "5"))
OUT_DIR   = "/home/jesse/openroot/data/symposium"
RAG_DB    = "/home/jesse/openroot/data/universal_index/agape_rag.db"
REPORT    = os.path.join(OUT_DIR, "leverage_report_" +
                         datetime.now().strftime("%Y%m%d_%H%M%S") + ".md")

def http(path, payload, timeout=600):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def gen(model, prompt, temp=0.4):
    return http("/api/generate", {"model": model, "prompt": prompt, "stream": False,
                                  "keep_alive": "30m",
                                  "options": {"temperature": temp, "num_ctx": 8192}}
                ).get("response", "").strip()

def embed(text):
    try:
        return http("/api/embeddings",
                    {"model": "nomic-embed-text", "prompt": text[:8000],
                     "keep_alive": "30m"}, timeout=60).get("embedding") or []
    except Exception:
        return []

def cos(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
    return d/(na*nb) if na and nb else 0.0

def retrieve(question, k=4):
    """Grounding for the 7B: top chunks from the RAG DB (semantic + path list)."""
    if not os.path.exists(RAG_DB):
        return "(no RAG index yet — reason from your own knowledge of the corpus)"
    con = sqlite3.connect(RAG_DB)
    rows = con.execute("SELECT path, text, embedding FROM chunks "
                       "ORDER BY id DESC LIMIT 4000").fetchall()
    con.close()
    if not rows:
        return "(RAG index empty — reason from your own knowledge)"
    qv = embed(question)
    if qv:
        scored = sorted(((cos(qv, struct.unpack("<%df" % (len(r[2])//4), r[2])), r)
                         for r in rows), key=lambda x: -x[0])[:k]
    else:
        terms = [w for w in re.findall(r"[A-Za-z_]{3,}", question)][:4]
        scored = [(0, r) for r in rows if any(t in r[1].lower() for t in terms)][:k]
    ctx = [f"- {r[1]} :: {r[0][:600]}" for _, r in scored]
    return "\n".join(ctx) if ctx else "(no relevant chunks)"

os.makedirs(OUT_DIR, exist_ok=True)
print(f"[canary] paste intact | symposium: {SMALL_MDL} <-> {BIG_MDL} | {ROUNDS} rounds")
report = ["# Model Symposium — Leverage Report",
          f"_Generated {datetime.now().isoformat()} | probe={SMALL_MDL} | ground={BIG_MDL}_\n"]

context_summary = ("The OpenRoot ecosystem: local-first computation stack on OptiPlex 3060 "
                   "+ Termux mesh. Assets: 6,766 inventoried files across scripts (4,855), "
                   "rag-agents (382), shelves (217), docs (123), thermal (110), "
                   "logic-engine (109), ledger-grants (96), aerocement (69), dome/geometry (9). "
                   "Available models: qwen2.5-coder:7b, qwen2.5:3b, nomic-embed-text, others.")

synergies = []
transcript = []

for rnd in range(1, ROUNDS + 1):
    print(f"\n===== ROUND {rnd}/{ROUNDS} =====")
    prior = ("\nFindings so far:\n" + "\n".join(f"- {s}" for s in synergies[-4:]) +
             "\n") if synergies else ""

    # --- 3B probes: what's leverageable that hasn't been said yet ---
    probe_q = (prior + "Given the OpenRoot asset classes above and the model stack "
                "(coder, grader, embedder), name ONE specific under-exploited pairing "
                "between two existing capabilities that would multiply output per joule "
                "of Jesse's human input. Be concrete: name the two components and the "
                "compound effect. Output format:\n"
                "PAIRING: <component A> + <component B>\n"
                "EFFECT: <one sentence>\n"
                "ETA_GAIN: <low|medium|high> — why briefly")
    probe = gen(SMALL_MDL, probe_q)
    print("[probe]", SMALL_MDL, "->"); print(probe[:600])
    transcript.append(("probe", probe))

    m = re.search(r"PAIRING:\s*(.+?)\nEFFECT:\s*(.+?)\n", probe, re.S)
    if not m:
        print("[hold] probe malformed — reskipping round")
        continue
    pairing, effect = m.group(1).strip(), m.group(2).strip()

    # --- 7B grounds it: retrieves evidence, refines into an actionable synergy ---
    ground_q = (f"A smaller model proposed this synergy:\nPAIRING: {pairing}\n"
                f"EFFECT: {effect}\n\nRetrieved local context:\n{retrieve(pairing)}\n\n"
                "Using ONLY credible context (say when context is missing), refine this "
                "into a concrete next action Jesse can execute this week. Format:\n"
                "SYNERGY: <refined pairing>\n"
                "EVIDENCE: <paths/facts grounding it, or 'weak: no direct evidence'>\n"
                "ACTION: <single concrete step with exact paths/commands where known>\n"
                "ETA: <your independent low|medium|high estimate>")
    grounded = gen(BIG_MDL, ground_q, temp=0.2)
    print("\n[ground]", BIG_MDL, "->"); print(grounded[:800])
    transcript.append(("ground", grounded))

    gm = re.search(r"SYNERGY:\s*(.+?)\nEVIDENCE:\s*(.+?)\nACTION:\s*(.+?)\nETA:\s*(\w+)",
                   grounded, re.S)
    if gm:
        syn, ev, act, eta = (x.strip() for x in gm.groups())
        synergies.append({"pairing": syn, "evidence": ev, "action": act, "eta": eta,
                          "raw_probe": pairing})
        report.append(f"## Synergy {len(synergies)}: {syn}\n"
                      f"- **Effect:** {effect}\n- **Evidence:** {ev}\n"
                      f"- **Action:** {act}\n- **ETA:** {eta}\n")
    else:
        print("[hold] grounding malformed — recorded raw")
        report.append(f"## Unparsed round {rnd}\n```\n{grounded[:500]}\n```\n")

# --- final grade: 3B ranks the synergies by leverage ---
if synergies:
    rank_q = ("Rank these OpenRoot synergies by (usefulness x feasibility) divided by "
              "human effort, most leverageable first. One line each, top line is #1:\n" +
              "\n".join(f"{i+1}. {s['pairing']} :: {s['action'][:120]}"
                        for i, s in enumerate(synergies)) +
              "\n\nThen pick the single BEST first move and say why in one sentence.")
    verdict = gen(SMALL_MDL, rank_q)
    print("\n===== GRADER VERDICT ====="); print(verdict)
    report.append("## Ranked by leverage\n```\n" + verdict + "\n```\n")

with open(REPORT, "w") as f:
    f.write("\n".join(report))
# append transcript for audit
with open(REPORT.replace(".md", "_transcript.json"), "w") as f:
    json.dump(transcript, f, indent=1)

print(f"\n[banked] {REPORT}")
print(f"[banked] transcript alongside")
print(f"[gate] next: less {REPORT} | eta-high items go to GOALS.md")
