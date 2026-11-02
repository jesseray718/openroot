#!/usr/bin/env python3
"""
OPENROOT FTS5 POD SEARCH CLI
Performs millisecond full-text searches across historical database pods and conversation blocks.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/thermodynamics/openroot_interactive_pods.db")

def search_pods(keyword: str):
    if not DB_PATH.exists():
        print(f"[!] Database pod not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query FTS5 virtual table for matching keywords
    query = "SELECT block_height, timestamp, prompt_text, response_text, dossier_tags FROM pod_fts WHERE pod_fts MATCH ? ORDER BY block_height ASC;"
    try:
        cursor.execute(query, (keyword,))
        results = cursor.fetchall()
        
        print(f"[*] Search results for keyword: '{keyword}' (Found: {len(results)} matches)")
        print("-" * 60)
        
        for row in results:
            height, timestamp, prompt, response, tags = row
            print(f"Block #{height} | Timestamp: {timestamp}")
            print(f"  Tags: {tags}")
            print(f"  Prompt: {prompt}")
            print(f"  Response: {response}")
            print("-" * 60)
            
    except sqlite3.OperationalError as e:
        print(f"[!] FTS5 Query Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    search_term = sys.argv[1] if len(sys.argv) > 1 else "progressive-loop"
    search_pods(search_term)
