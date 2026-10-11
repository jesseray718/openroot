#!/usr/bin/env python3
import os
import json
import sys
import sqlite3
import urllib.request
import urllib.error
import re
from pathlib import Path

SAFE_DB = "file_map_safe.sqlite"
CONTEXT_FILE = "coder_context.json"

def load_keys():
    """Sanitize and load API keys from environment and ~/.api_keys."""
    keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "").strip(),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", "").strip(),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", "").strip()
    }
    keys_file = os.path.expanduser("~/.api_keys")
    if os.path.exists(keys_file):
        with open(keys_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"').strip()
                    if k in keys and v:
                        keys[k] = v
    return keys

KEYS = load_keys()
GEMINI_KEY = KEYS["GEMINI_API_KEY"]
GROQ_KEY = KEYS["GROQ_API_KEY"]
OPENROUTER_KEY = KEYS["OPENROUTER_API_KEY"]

def get_live_openrouter_free_models():
    """Fetch live :free models directly from OpenRouter API."""
    try:
        url = "https://openrouter.ai/api/v1/models"
        req = urllib.request.Request(url, headers={"User-Agent": "AgapeCoder/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            models = [m["id"] for m in data.get("data", []) if str(m.get("id", "")).endswith(":free")]
            if models:
                return models
    except Exception as e:
        print(f"[!] Dynamic OpenRouter fetch warning: {e}")
    return [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen-2.5-coder-32b-instruct:free"
    ]

AGAPE_SYSTEM_PROMPT = """
You are an autonomous senior coding assistant governed by Agape Coordination and the 12 Computational Permaculture Principles.
You have access to a SQLite file map database (`file_map_safe.sqlite`). To query it, output a single SELECT query strictly inside ```sql ... ``` blocks.
"""

def query_sqlite(sql_query):
    if not os.path.exists(SAFE_DB):
        return f"Error: Database {SAFE_DB} does not exist on disk."
    clean_sql = sql_query.strip().strip("`").strip()
    clean_sql = re.sub(r"^<tool_call>\s*(?:sql)?", "", clean_sql, flags=re.IGNORECASE).strip()
    if not clean_sql.upper().startswith("SELECT"):
        return "Error: Only SELECT queries allowed."
    try:
        conn = sqlite3.connect(SAFE_DB)
        cursor = conn.cursor()
        cursor.execute(clean_sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        return json.dumps([dict(zip(cols, r)) for r in rows[:25]], indent=2) if rows else "No records found."
    except Exception as e:
        return f"SQL Error: {e}"

def extract_sql_query(response_text):
    m1 = re.search(r"```sql\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
    if m1:
        return m1.group(1).strip()
    m2 = re.search(r"<tool_call>(?:sql)?\s*(.*?)\s*(?:</tool_call>|```|$)", response_text, re.DOTALL | re.IGNORECASE)
    if m2 and "SELECT" in m2.group(1).upper():
        return m2.group(1).strip()
    return None

def call_groq(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for m in models:
        try:
            payload = {"model": m, "messages": messages, "temperature": 0.2}
            req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
                return data["choices"][0]["message"]["content"]
        except Exception:
            continue
    raise RuntimeError("Groq requests failed.")

def call_gemini(messages):
    models = ["gemini-1.5-flash", "gemini-2.0-flash"]
    for m in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={GEMINI_KEY}"
            prompt = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages])
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            continue
    raise RuntimeError("Gemini requests failed.")

def call_openrouter(messages, model_name):
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {"model": model_name, "messages": messages, "temperature": 0.2}
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/openroot",
        "X-Title": "Agape Permaculture Coder"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content")
            if content and content.strip():
                return content
    raise ValueError(f"Model {model_name} returned empty content.")

def call_cascading_llm(messages):
    if GROQ_KEY:
        try:
            print("[*] Tier 1: Dispatching to Groq...")
            return call_groq(messages)
        except Exception as e:
            print(f"[!] Groq bypass ({e}), falling back...")

    if GEMINI_KEY:
        try:
            print("[*] Tier 2: Dispatching to Google Gemini...")
            return call_gemini(messages)
        except Exception as e:
            print(f"[!] Gemini bypass ({e}), falling back...")

    if OPENROUTER_KEY:
        free_models = get_live_openrouter_free_models()
        print(f"[*] Querying {len(free_models)} live OpenRouter free models...")
        for model in free_models:
            try:
                print(f"[*] Tier 3 (OpenRouter Matrix): Trying {model}...")
                res = call_openrouter(messages, model)
                if res:
                    return res
            except Exception as e:
                print(f"[!] OpenRouter {model} failed ({e}), cascading...")

    return None

def local_fallback_scan():
    """Permaculture Principle #11/#12: Local direct execution fallback."""
    print("\n[*] Cloud APIs unreachable. Executing local filesystem inspection...")
    target_dir = Path("/sdcard/Documents/markor")
    if not target_dir.exists():
        # Fallback to alternate Termux mount paths
        target_dir = Path("/storage/emulated/0/Documents/markor")

    if not target_dir.exists():
        print(f"[!] Directory not found: {target_dir}")
        return

    md_files = list(target_dir.rglob("*.md"))
    print(f"\n=== LOCAL SUMMARY OF MARKDOWN FILES IN {target_dir} ===")
    print(f"Found {len(md_files)} markdown file(s):\n")

    for fpath in md_files[:20]:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                title = lines[0] if lines else "Empty File"
                preview = " ".join(lines[1:4])[:150] if len(lines) > 1 else "No additional context."
                print(f"• File: {fpath.name}")
                print(f"  Path: {fpath}")
                print(f"  Topic/Header: {title}")
                print(f"  Preview: {preview}...\n")
        except Exception as e:
            print(f"• File: {fpath.name} (Error reading: {e})\n")

def run_task(prompt):
    messages = [{"role": "system", "content": AGAPE_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
    
    response = call_cascading_llm(messages)
    
    if not response:
        # Local fallback execution
        local_fallback_scan()
        return

    sql_q = extract_sql_query(response)
    if sql_q:
        print(f"[*] Executing SQL Inspection: {sql_q}")
        db_res = query_sqlite(sql_q)
        print(f"[*] Database Result: {db_res[:200]}...")
    else:
        print("\n=== AGAPE AGENT OUTPUT ===")
        print(response)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_7b_coder.py \"Task description\"")
    else:
        run_task(" ".join(sys.argv[1:]))
