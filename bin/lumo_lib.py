#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""lumo_lib.py — shared primitives for the OpenRoot local stack.
ollama_generate / prove (cache-first, never recompute) / embed (nomic).
Import from any script: from lumo_lib import ollama_generate, prove, embed
"""
import datetime, hashlib, json, os, sqlite3, urllib.request

ROOT = "/home/jesse/openroot"
OLLAMA_HOST = "http://localhost:11434"
MODEL_BUILDER = "qwen2.5-coder:7b"
MODEL_GRADER = "qwen2.5:3b"
MODEL_EMBED = "nomic-embed-text"
CACHE_DB = os.path.join(ROOT, "data", "proof_cache.db")

def _post(endpoint, payload, timeout=600):
    req = urllib.request.Request(
        OLLAMA_HOST + endpoint, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def ollama_generate(prompt, model=MODEL_BUILDER, timeout=600):
    return _post("/api/generate",
                 {"model": model, "prompt": prompt, "stream": False},
                 timeout)["response"]

def embed(texts, model=MODEL_EMBED, timeout=300):
    """Embed str or list[str] -> list of float lists."""
    single = isinstance(texts, str)
    out = _post("/api/embed",
                {"model": model, "input": [texts] if single else texts},
                timeout)["embeddings"]
    return out[0] if single else out

def prove(statement):
    """Cache-first theorem prover: PROVED -> never recomputed.
    Promoted from knowledge_probe_v1.py v1.1 (identical semantics)."""
    tid = hashlib.sha256(statement.encode()).hexdigest()[:16]
    con = sqlite3.connect(CACHE_DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS proofs (
        theorem_id TEXT PRIMARY KEY, statement TEXT, status TEXT, proof TEXT,
        grader_verdict TEXT, model TEXT, sha256 TEXT, created_at TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_proofs_status ON proofs(status)")
    con.commit()
    row = con.execute("SELECT * FROM proofs WHERE theorem_id=?",
                      (tid,)).fetchone()
    if row and row["status"] == "PROVED":
        proof = row["proof"]; created = row["created_at"]
        con.close()
        print("[cache-hit] theorem %s already proved %s — no recompute"
              % (tid, created))
        return {"statement": statement, "status": "PROVED", "proof": proof}
    if row and row["status"] == "FAILED":
        con.close()
        print("[held] theorem %s previously graded FAIL — see cache" % tid)
        return {"statement": statement, "status": "FAILED"}
    try:
        draft = ollama_generate(
            "Prove this statement rigorously and concisely. "
            "State premises, steps, conclusion.\nSTATEMENT: " + statement)
        verdict = ollama_generate(
            "Grade the following proof against this statement. "
            "Reply first line VERDICT: PASS or VERDICT: FAIL, "
            "second line FIX: none or a correction.\nSTATEMENT: %s\nPROOF: %s"
            % (statement, draft), model=MODEL_GRADER)
        status = "PROVED" if "PASS" in verdict.upper() else "FAILED"
        con.execute("INSERT OR REPLACE INTO proofs VALUES (?,?,?,?,?,?,?,?)",
            (tid, statement, status, draft, verdict, MODEL_BUILDER,
             hashlib.sha256(draft.encode()).hexdigest(),
             datetime.datetime.now().isoformat(timespec="seconds")))
        con.commit()
        print("[%s] theorem %s graded %s" %
              ("banked" if status == "PROVED" else "held", tid, status))
        return {"statement": statement, "status": status, "proof": draft}
    except Exception as e:
        print("[held] ollama unreachable (%s) — theorem %s unbanked" % (e, tid))
        return {"statement": statement, "status": "UNBANKED"}
    finally:
        con.close()
# [exit=0]
