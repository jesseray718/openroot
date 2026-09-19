#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""llm_rag_integration.py — Bridges local LLMs with the SQLite RAG index.
Usage: python3 llm_rag_integration.py "<your query>"
"""
import os
import sys
import sqlite3
import json
import math

sys.path.insert(0, "/home/jesse/openroot/bin")
import lumo_lib

ROOT = "/home/jesse/openroot"
DB = os.path.join(ROOT, "data", "embeddings.db")

def retrieve_context(query, k=3):
    """Retrieve the top-k most semantically similar chunks from the local index."""
    try:
        qv = lumo_lib.embed(query)
    except Exception as exc:
        print(f"[held] Embedding failed: {exc}")
        return "(No relevant local context found.)"

    con = None
    try:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        rows = con.execute("SELECT path, chunk, embedding FROM chunks").fetchall()
    except sqlite3.Error as exc:
        print(f"[held] Database access failed: {exc}")
        return "(No relevant local context found.)"
    finally:
        if con:
            con.close()

    if not rows:
        return "(No relevant local context found.)"

    scored = []
    for path, chunk, blob in rows:
        try:
            cv = json.loads(blob)
            dot = sum(a * b for a, b in zip(qv, cv))
            na = math.sqrt(sum(a * a for a in qv))
            nb = math.sqrt(sum(b * b for b in cv))
            if na and nb:
                scored.append((dot / (na * nb), path, chunk))
        except (ValueError, TypeError, json.JSONDecodeError):
            continue

    scored.sort(reverse=True)
    top_chunks = scored[:k]

    if not top_chunks:
        return "(No relevant local context found.)"

    context_str = "\n\n".join(f"--- {path} ---\n{chunk}" for _, path, chunk in top_chunks)
    return context_str

def generate_answer(query, context):
    """Generate an answer using the local builder model grounded in context."""
    prompt = (
        "You are an expert answering a question based on the provided OpenRoot repository context.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION:\n{query}\n\n"
        "ANSWER:"
    )
    try:
        response = lumo_lib.ollama_generate(prompt)
        return response
    except Exception as exc:
        return f"[held] Generation failed: {exc}"

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 llm_rag_integration.py "<your query>"')
        sys.exit(1)

    query = sys.argv[1]
    
    print(f"[search] Retrieving context for: '{query}'...")
    context = retrieve_context(query)
    
    if "(No relevant local context found.)" in context:
        print("[warn] No local context retrieved. Proceeding with base model knowledge.")
    else:
        num_blocks = context.count("--- ")
        print(f"[search] Found {num_blocks} relevant context blocks.")

    print("[generate] Generating response...")
    answer = generate_answer(query, context)
    
    print("\n=== ANSWER ===")
    print(answer)
    print("==============")
    
    print("[exit=0]")
    sys.exit(0)

if __name__ == "__main__":
    main()
