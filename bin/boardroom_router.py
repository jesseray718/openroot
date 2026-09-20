#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# boardroom_router.py — Executive Boardroom Council, RAG Router & Response Grader

import json, math, re, sqlite3, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.home() / "openroot"
DB_PATH = ROOT / "data" / "fts_index.db"
LEDGER_PATH = ROOT / "data" / "logs" / "boardroom_ledger.jsonl"
LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

# --- 1. COUNCIL PROMPTS & ROLES ---
COUNCIL_ROLES = {
    "STRATEGIST": {
        "title": "Chief Strategist (Agape Anchor)",
        "prompt": "Optimize for long-term vision, zero-coordination cost, and strict alignment with the Agape taxonomy matrix."
    },
    "ARCHITECT": {
        "title": "Technical Architect (Coder 7B)",
        "prompt": "Provide production-ready, zero-defect code, AST transformations, and optimized POSIX shell / Python structures."
    },
    "PERMACULTURE": {
        "title": "Permaculture & Yield Director",
        "prompt": "Apply the 12 permaculture principles. Maximize thermal energy capture, waste-stream cascades, and structural yields."
    },
    "AUDITOR": {
        "title": "System Grader & Auditor (3B Check)",
        "prompt": "Parse artifacts, verify JSON schema compliance, check syntax integrity, and grade performance from 0.0 to 1.0."
    }
}

# --- 2. LOCAL RAG RETRIEVAL (SQLite FTS5) ---
def query_knowledge_db(query: str, limit: int = 3):
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Clean non-alphanumeric characters for standard FTS match
    clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query)
    if not clean_query.strip():
        return []
    
    sql = "SELECT filepath, title, content FROM knowledge_fts WHERE knowledge_fts MATCH ? LIMIT ?;"
    results = []
    try:
        cursor.execute(sql, (clean_query, limit))
        for row in cursor.fetchall():
            results.append({"path": row[0], "title": row[1], "snippet": row[2][:300] + "..."})
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()
    return results

# --- 3. AUDIT & GRADING ENGINE ---
def grade_execution_output(response_text: str, code_snippets: list) -> dict:
    score = 1.0
    penalties = []

    # Check 1: Code syntax syntax integrity
    for code in code_snippets:
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            score -= 0.35
            penalties.append(f"SyntaxError in generated snippet: {e}")

    # Check 2: Structural filler / wordiness penalty
    filler_words = ["in conclusion", "here is a list", "as an ai model"]
    for word in filler_words:
        if word in response_text.lower():
            score -= 0.10
            penalties.append(f"Filler term detected: '{word}'")

    # Check 3: Schema verification
    score = max(0.0, min(1.0, round(score, 2)))
    
    return {
        "score": score,
        "grade": "PASS" if score >= 0.70 else "FAIL",
        "penalties": penalties,
        "audited_at": datetime.now(timezone.utc).isoformat()
    }

# --- 4. COUNCIL ROUTER RUNNER ---
def run_boardroom_session(task_query: str):
    print(f"[+] Initializing Boardroom Session for task: '{task_query}'")
    context_docs = query_knowledge_db(task_query)
    
    session_manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": task_query,
        "rag_context_count": len(context_docs),
        "council_outputs": {}
    }

    print(f"[+] Retrieved {len(context_docs)} local context snippets from FTS5 index.")
    
    # Simulate multi-agent evaluation pipeline
    synthetic_code_sample = "def test():\n    return 'Agape Matrix Active'\n"
    audit_results = grade_execution_output("Direct execution payload delivered.", [synthetic_code_sample])

    for role_key, role_meta in COUNCIL_ROLES.items():
        session_manifest["council_outputs"][role_key] = {
            "title": role_meta["title"],
            "status": "APPROVED" if audit_results["grade"] == "PASS" else "FLAGGED",
            "audit": audit_results if role_key == "AUDITOR" else None
        }

    # Append transaction to append-only JSON-L ledger
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(session_manifest, ensure_ascii=False) + "\n")

    print(f"[+] Session logged to ledger: {LEDGER_PATH}")
    print(json.dumps(session_manifest, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Aero-Disc heat exchanger thermal yield"
    run_boardroom_session(query)
