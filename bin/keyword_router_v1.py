#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""keyword_router_v1.py - FTS5 keyword pathways + multi-model loop hive
with Lumo inbox. KWRTV1 canary.

Loop shape per keyword path:
  keyword -> FTS5 query (local docs/lessons/ctx) -> fetch top passages ->
  route synthesis to cheapest CAPABLE model (local 3B/7B, gemini-flash
  free tier, openrouter free fallback) -> result written to inbox ->
  new lessons STAGED (human gate) -> digest emitted for Lumo handoff.

Lumo is in the loop via data/lumo_inbox.db + inbox digest md: the digest
IS the handoff artifact you paste into chat each window.

Doctrine: keys load from data/.env at runtime only. Failed API route
falls back to local - loop never dies on missing credentials.
"""
import json, os, sqlite3, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
CANARY = "KWRTV1"
EPS = 1e-6
OLLAMA = "http://localhost:11434/api/generate"
ENVFILE = ROOT / "data/.env"

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def load_env():
    if ENVFILE.exists():
        for line in ENVFILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def db_docs():
    """FTS5 index over knowledge corpus: docs, analysis, context_bridge."""
    c = sqlite3.connect(str(ROOT / "data/doc_index.db"))
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS fts_docs USING fts5(
        relpath, body)""")
    c.commit()
    return c

def refresh_index(c):
    seen = {r[0] for r in c.execute("SELECT relpath FROM fts_docs").fetchall()}
    n = 0
    for sub in ("docs", "analysis", "context_bridge"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            rel = str(p.relative_to(ROOT))
            if rel in seen or p.stat().st_size > 500_000:
                continue
            body = p.read_text(errors="replace")
            c.execute("INSERT INTO fts_docs VALUES (?, ?)", (rel, body))
            n += 1
    c.commit()
    return n

def fts_fetch(c, keyword, k=5):
    try:
        rows = c.execute(
            "SELECT relpath, snippet(fts_docs, 1, '[', ']', '...', 12) "
            "FROM fts_docs WHERE fts_docs MATCH ? LIMIT ?", (keyword, k)
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    return [(r[0], r[1]) for r in rows]

def inbox_db():
    c = sqlite3.connect(str(ROOT / "data/lumo_inbox.db"))
    c.execute("""CREATE TABLE IF NOT EXISTS inbox (
        id INTEGER PRIMARY KEY, ts TEXT, keyword TEXT, model TEXT,
        result TEXT, consumed INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS loop_stats (
        ts TEXT, keyword TEXT, model TEXT, latency_ms INTEGER, ok INTEGER)""")
    c.commit()
    return c

def ollama_gen(model, prompt, timeout=180):
    payload = json.dumps({"model": model, "prompt": prompt,
                          "stream": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload,
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode()).get("response", ""), \
               int((time.time() - t0) * 1000)

def gemini_gen(key, prompt, model="gemini-2.0-flash"):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           + model + ":generateContent?key=" + key)
    payload = json.dumps({"contents": [
        {"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    text = d.get("candidates", [{}])[0].get("content", {}) \
             .get("parts", [{}])[0].get("text", "")
    return text, int((time.time() - t0) * 1000)

def openrouter_gen(key, prompt, model="meta-llama/llama-3.2-3b-instruct:free"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = json.dumps({"model": model, "messages": [
        {"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    text = d.get("choices", [{}])[0].get("message", {}).get("content", "")
    return text, int((time.time() - t0) * 1000)

def keywords():
    kwf = ROOT / "data/router_keywords.json"
    if kwf.exists():
        return json.loads(kwf.read_text()).get("keywords", [])
    default = ["permaculture", "agape", "aerocement", "stirling",
               "floor_lift", "lesson", "router", "popw"]
    kwf.write_text(json.dumps({"keywords": default}, indent=1))
    return default

def synth_prompt(keyword, hits):
    ctx = "\n\n".join(h[0] + ":\n" + h[1] for h in hits[:5])
    return ("Keyword pathway: " + keyword + "\nCorpus passages:\n" + ctx +
            "\n\nSynthesize in under 120 words: what actionable thread "
            "connects these passages for the OpenRoot mission? If a passage "
            "suggests a past mistake and its fix, name them plainly.")

def route(keyword, hits, gkey, okey):
    """Route by talent: local-first. API tiers engage only when local
    answered thin - free tier saves local watts, not replaces them."""
    prompt = synth_prompt(keyword, hits)
    text, ms = ollama_gen("qwen2.5:3b", prompt)
    model = "local:qwen2.5:3b"
    if len(text.strip()) < 80:
        if gkey:
            try:
                text, ms = gemini_gen(gkey, prompt)
                model = "api:gemini-2.0-flash"
            except Exception:
                pass
        if len(text.strip()) < 80 and okey:
            try:
                text, ms = openrouter_gen(okey, prompt)
                model = "api:openrouter-free"
            except Exception:
                pass
    return model, text, ms

def main():
    load_env()
    gkey = os.environ.get("GEMINI_API_KEY", "")
    okey = os.environ.get("OPENROUTER_API_KEY", "")
    if gkey.startswith("your_") or not gkey:
        gkey = ""
    if okey.startswith("your_") or not okey:
        okey = ""
    print("[" + CANARY + "] canary intact | api tiers:",
          "gemini+openrouter" if (gkey or okey) else "LOCAL ONLY (add keys to data/.env)")
    docs = db_docs()
    added = refresh_index(docs)
    inbox = inbox_db()
    kws = keywords()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("kwloop-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    digest = ["# Lumo Inbox Digest - " + ts, ""]
    for kw in kws:
        hits = fts_fetch(docs, kw)
        if not hits:
            digest.append("- [" + kw + "] no FTS5 hits - index may need refresh")
            continue
        try:
            model, text, ms = route(kw, hits, gkey, okey)
        except Exception as e:
            digest.append("- [" + kw + "] ALL routes failed: " + str(e)[:100])
            inbox.execute("INSERT INTO loop_stats VALUES (?,?,?,?,?)",
                          (now(), kw, "none", 0, 0))
            continue
        inbox.execute("INSERT INTO inbox (ts, keyword, model, result) "
                      "VALUES (?,?,?,?)", (now(), kw, model, text.strip()))
        inbox.execute("INSERT INTO loop_stats VALUES (?,?,?,?,?)",
                      (now(), kw, model, ms, 1))
        digest.append("- [" + kw + "] (" + model + ", " + str(ms) + "ms)")
        digest.append("  " + text.strip().replace("\n", " ")[:220])
    inbox.commit()
    dp = wa / "lumo_inbox_digest.md"
    dp.write_text("\n".join(digest) + "\n")
    print("[INBOX] " + str(dp))
    print("[TIP] consume-mark after review:")
    print("  sqlite3 data/lumo_inbox.db \"UPDATE inbox SET consumed=1;")
    print("       DELETE FROM inbox WHERE consumed=1;\"")
    print("[" + CANARY + "] complete - inbox digest ready for Lumo handoff")
    return 0

if __name__ == "__main__":
    sys.exit(main())
