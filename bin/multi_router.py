#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""multi_router v1 — many cheap loops, comfort-zone enforcement, per-round self-memory.
Usage: python3 bin/multi_router.py [--rounds N] [--smoke]
Env: GEMINI_API_KEY, OPENROUTER_API_KEY (never embedded in files).
"""
import argparse, hashlib, json, os, sqlite3, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "router_ledger.db")
OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# ---- provider registry: talents DECLARED, router refuses anything else ----
PROVIDERS = {
    "qwen3b_local":   {"api": "ollama", "model": "qwen2.5:3b",
        "allows": {"classify": "classify task into a task-class from the fixed list"},
        "strength": "fast classification and rubric grading. NEVER write code or long documents."},
    "qwen7b_coder":  {"api": "ollama", "model": "qwen2.5-coder:7b",
        "allows": {"code-edit": "apply one atomic spec as a minimal diff"},
        "strength": "minimal code edits from precise specs. NEVER design architecture."},
    "nomic_embed":   {"api": "ollama", "model": "nomic-embed-text",
        "allows": {"embed": "embed text into vector"},
        "strength": "embedding/retrieval only. NO generation."},
    "gemini":        {"api": "gemini", "model": "gemini-2.0-flash",
        "allows": {"synth": "synthesize multi-document context into one doc",
                   "summarize": "compress a long doc"},
        "strength": "long-context reading and synthesis. NO executable code authorship."},
    "openrouter":    {"api": "openrouter", "model": None,  # resolved at runtime
        "allows": {"draft": "bulk low-stakes drafting",
                   "translate": "translation", "outline": "structure an outline"},
        "strength": "cheap bulk text. NO math proofs, NO code."},
    "lumo_manual":   {"api": "manual", "model": "human-paste-bridge",
        "allows": {"plan": "author plan/spec", "reason": "cross-model reasoning audit"},
        "strength": "spec authoring + routing judgment via chat handoff. NOT an API."},
}
CLASS_TO_PROVIDER = {}          # built from PROVIDERS allows
for name, p in PROVIDERS.items():
    for k in p["allows"]:
        CLASS_TO_PROVIDER[k] = name

def now(): return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:16]

def db():
    c = sqlite3.connect(DB); c.execute("""CREATE TABLE IF NOT EXISTS hops(
        ts TEXT, round INTEGER, task_id TEXT, task_class TEXT, provider TEXT,
        model TEXT, latency_ms REAL, status TEXT, out_path TEXT)""")
    return c

def ollama(model, prompt, timeout=180):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_BASE.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read())["response"]
    return out, (time.time()-t0)*1000

def rest(url, headers, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.loads(r.read())
    return out, (time.time()-t0)*1000

def call_gemini(prompt):
    k = os.environ.get("GEMINI_API_KEY"); 
    if not k: return None, 0, "[HELD] GEMINI_API_KEY unset"
    m = PROVIDERS["gemini"]["model"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
    out, ms = rest(url, {"Content-Type": "application/json"},
                   {"contents": [{"parts": [{"text": prompt}]}]})
    return out["candidates"][0]["content"]["parts"][0]["text"], ms, "ok"

def resolve_openrouter_model():
    """Runtime pick: env override > cheapest live :free slug. Never trust hardcoded slugs."""
    if os.environ.get("OPENROUTER_MODEL"):
        return os.environ["OPENROUTER_MODEL"], "env-override"
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k: return None, "[HELD] OPENROUTER_API_KEY unset"
    try:
        hdr = {"Authorization": f"Bearer {k}"}
        out, _ = rest("https://openrouter.ai/api/v1/models", hdr, {})
        frees = [m["id"] for m in out["data"]
                 if str(m.get("pricing", {}).get("prompt", "1")) == "0"]
        frees.sort()   # deterministic
        return (frees[0], f"auto-picked of {len(frees)} free") if frees else (None, "no free models")
    except Exception as e:
        return None, f"[HELD] model-list {type(e).__name__}: {e}"

def call_openrouter(prompt):
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k: return None, 0, "[HELD] OPENROUTER_API_KEY unset"
    model, how = resolve_openrouter_model()
    if not model: return None, 0, f"[HELD] {how}"
    out, ms = rest("https://openrouter.ai/api/v1/chat/completions",
        {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        {"model": model,
         "messages": [{"role": "user", "content": prompt}]})
    return out["choices"][0]["message"]["content"] + f" [via {model}]", ms, "ok"

def dispatch(provider, task_class, task_text, rnd, task_id, con):
    p = PROVIDERS[provider]
    if task_class not in p["allows"]:                       # COMFORT-ZONE ENFORCEMENT
        con.execute("INSERT INTO hops VALUES(?,?,?,?,?,?,?,?,?)",
            (now(), rnd, task_id, task_class, provider, p["model"], 0, "DENIED-comfort-zone", ""))
        con.commit(); return "[DENIED] outside declared talent — routed elsewhere"
    instr = (f"SYSTEM: You are the '{provider}' node. Your ONLY talent: {p['strength']}\n"
             f"Task class: {task_class} ({p['allows'][task_class]}).\n"
             f"Refuse anything outside your talent by replying [OUT-OF-SCOPE].\n\nTASK:\n{task_text}")
    try:
        if p["api"] == "ollama":
            if task_class == "embed":
                body = json.dumps({"model": p["model"], "input": task_text}).encode()
                req = urllib.request.Request(OLLAMA_BASE.rstrip("/") + "/api/embeddings",
                        data=body, headers={"Content-Type": "application/json"})
                t0 = time.time()
                with urllib.request.urlopen(req, timeout=60) as r:
                    j = json.loads(r.read())
                ms = (time.time()-t0)*1000; out = f"[{len(j['embedding'])}-dim vector]"
            else:
                out, ms = ollama(p["model"], instr)
            status = "ok"
        elif p["api"] == "gemini":
            out, ms, status = call_gemini(instr)
        elif p["api"] == "openrouter":
            out, ms, status = call_openrouter(instr)
        elif p["api"] == "manual":                          # LUMO LANE — paste bridge
            pkt = os.path.join(ROOT, "lumo_lane", "inbox",
                    f"round{rnd:03d}_{task_id}_{now()}.md")
            with open(pkt, "w") as f: f.write(
                f"# Lumo Handoff — round {rnd}\n```\ntask_class: {task_class}\ntask_id: {task_id}\n"
                f"instructions: {instr}\n```\nPaste your reply in lumo_lane/outbox/ "
                f"as `reply-{os.path.basename(pkt)}`; next round ingests it.")
            out, ms, status = f"[QUEUED] {pkt}", 0.0, "lumo-queued"
    except Exception as e:
        out, ms, status = f"[HELD] {type(e).__name__}: {e}", 0.0, "error"
    outdir = os.path.join(ROOT, "reports", f"router_r{rnd:03d}"); os.makedirs(outdir, exist_ok=True)
    outp = os.path.join(outdir, f"{task_id}_{task_class}.md")
    with open(outp, "w") as f: f.write(str(out))
    con.execute("INSERT INTO hops VALUES(?,?,?,?,?,?,?,?,?)",
        (now(), rnd, task_id, task_class, provider, p["model"], round(ms,1), status, outp))
    con.commit()
    return str(out)[:200]

def classify_3b(text):
    cls_list = ", ".join(sorted(CLASS_TO_PROVIDER))
    out, _ = ollama(PROVIDERS["qwen3b_local"]["model"],
        f"Classify this task into EXACTLY one class from [{cls_list}]. "
        f"Reply with the single class word only.\nTASK: {text[:500]}")
    for k in CLASS_TO_PROVIDER:
        if k in out.lower(): return k
    return None

def self_memory(rnd, con, denied):
    """fresh memory every round — self-customized instructions + pathways"""
    rows = con.execute("""SELECT provider, COUNT(*), AVG(latency_ms),
        SUM(status='ok')+SUM(status='lumo-queued') FROM hops GROUP BY provider""").fetchall()
    speed = "\n".join(f"- {p}: {n} hops, avg {lat:.0f}ms, {ok} ok" for p,n,lat,ok in rows)
    tips = {"qwen7b_coder": "specs ever finer-grained — keep diffs atomic",
            "gemini": "feed multi-doc contexts, it earns its cost in synthesis",
            "openrouter": "route ALL bulk drafts here first (free tier)",
            "qwen3b_local": "classification only; its rubric grading stays in team_gate"}
    mem = os.path.join(ROOT, "data", "router_memory")
    os.makedirs(mem, exist_ok=True)
    body = (f"# Router Round-{rnd} Self-Memory\n## living register\n{speed}\n"
            f"## comfort-zone denials this round\n{denied or '(none — everyone inside talent)'}\n"
            f"## self-customized instructions next round\n"
            + "\n".join(f"- {t}" for t in tips.values()) +
            "\n## pathways\n- 3B classifies -> routed provider executes -> ledger -> "
            "next round memory\n- lumo lane packets await human paste-back (outbox)")
    pid = f"routermem-r{rnd:03d}-{now()}"; h = sha(body)
    path = os.path.join(mem, f"r{rnd:03d}.md")
    with open(path, "w") as f: f.write(
        f"---\nid: {pid}\ntimestamp: {now()}\ntype: router-memory\nparent: multi_router.py\n"
        f"hash: {h}\nstatus: active\n---\n\n{body}\n\n## Agape Analysis\n"
        "- Resonance: work flows to the node whose talent matches the load\n"
        f"- Entropy check: denials this round = {len(denied)}\n- Next move: ingest lumo outbox, expand lanes\n")
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=int(os.environ.get("ROUTER_ROUNDS", "3")))
    ap.add_argument("--tasks", default=os.path.join(ROOT, "data", "router_tasks.json"))
    args = ap.parse_args()
    con = db()
    tasks = json.load(open(args.tasks)) if os.path.exists(args.tasks) else [
        {"id": "t1", "class": "draft",     "text": "Draft a 5-line README blurb for OpenRoot lb_loop."},
        {"id": "t2", "class": "classify",  "text": "Is this task a code edit or a summary?"},
        {"id": "t3", "class": "plan",      "text": "Plan mistake-to-solution binding patch for lb_loop_v2."},
        {"id": "t4", "class": "outline",   "text": "Outline a SARE grant framing doc for OpenCell."}]
    print(f"[BOOT] {len(tasks)} tasks, {args.rounds} rounds, {len(PROVIDERS)} providers")
    print(f"[PREFLIGHT] ollama_base={OLLAMA_BASE}")
    # cheap liveness probes — dead lanes degrade gracefully, never burn a round mid-task
    try:
        import urllib.request as _u
        with _u.urlopen(OLLAMA_BASE.rstrip("/") + "/api/tags", timeout=5) as r:
            alive = len(json.loads(r.read()).get("models", []))
        print(f"[PREFLIGHT] ollama ALIVE — {alive} models loaded")
    except Exception as e:
        print(f"[PREFLIGHT] ollama DEAD ({type(e).__name__}) — set OLLAMA_HOST=http://100.122.169.43:11434 from termux")
    m, how = resolve_openrouter_model()
    print(f"[PREFLIGHT] openrouter model: {m or 'NONE'} ({how})")
    print(f"[PREFLIGHT] gemini: {'armed' if os.environ.get('GEMINI_API_KEY') else 'HELD — no key'}")
    print(f"[PREFLIGHT] lumo_manual: armed (paste bridge)")
    for rnd in range(1, args.rounds+1):
        print(f"\n===== ROUTER ROUND {rnd}/{args.rounds} =====")
        denied = []
        # ingest lumo outbox replies from prior round as context
        ob = os.path.join(ROOT, "lumo_lane", "outbox")
        lumo_context = ""
        for f in sorted(os.listdir(ob))[-3:]:
            lumo_context += open(os.path.join(ob, f)).read()[:1500]
        for t in tasks:
            tc = t["class"]
            if tc == "auto":
                tc = classify_3b(t["text"]) or "draft"
            prov = CLASS_TO_PROVIDER.get(tc, "lumo_manual")
            ctx = t["text"] + (f"\n\nPRIOR LUMO GUIDANCE:\n{lumo_context}" if lumo_context and prov=="lumo_manual" else "")
            print(f"  {t['id']} [{tc}] -> {prov}: ", end="")
            res = dispatch(prov, tc, ctx, rnd, t["id"], con)
            if "DENIED" in res or "HELD" in res: denied.append((t["id"], tc, prov))
            print(res[:120])
        mp = self_memory(rnd, con, denied)
        print(f"  [MEMORY] fresh self-instructions banked: {mp}")
    print("\n[LEDGER] capability/speed totals")
    for p, n, lat, ok in con.execute(
        """SELECT provider, COUNT(*), AVG(latency_ms),
           SUM(status IN ('ok','lumo-queued')) FROM hops GROUP BY provider ORDER BY 2 DESC"""):
        print(f"  {p:14s} hops={n}  avg={lat or 0:6.0f}ms  ok={ok}")
    print("[CANARY] multi-router-smoke-complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
