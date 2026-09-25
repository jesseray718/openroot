#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
query_ideas.py - Search parallel_ideas.jsonl with filters
"""

import json
import sys
from pathlib import Path

IDEAS_PATH = Path("/home/jesse/openroot/data/parallel_ideas.jsonl")

def load_ideas():
    if not IDEAS_PATH.exists():
        print(f"ERROR: {IDEAS_PATH} not found")
        return []
    
    ideas = []
    with open(IDEAS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    ideas.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return ideas

def search(query, ideas):
    """Simple text search across all string values"""
    q = query.lower()
    matches = []
    for i, idea in enumerate(ideas):
        # Flatten all string values
        txt = json.dumps(idea).lower()
        if q in txt:
            matches.append((i, idea))
    return matches

def main():
    if len(sys.argv) < 2:
        print("Usage: query_ideas.py <search_term>")
        print("       query_ideas.py --stats")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--stats":
        ideas = load_ideas()
        print(f"Total ideas: {len(ideas)}")
        print(f"File: {IDEAS_PATH}")
        if ideas:
            print(f"\nFirst entry:")
            print(json.dumps(ideas[0], indent=2)[:500])
        return
    
    ideas = load_ideas()
    matches = search(arg, ideas)
    
    print(f"Query: '{arg}'")
    print(f"Matches: {len(matches)} / {len(ideas)}")
    
    for idx, idea in matches[:20]:  # Limit to 20 results
        print(f"\n--- [{idx}] ---")
        print(json.dumps(idea, indent=2)[:1000])

if __name__ == "__main__":
    main()
