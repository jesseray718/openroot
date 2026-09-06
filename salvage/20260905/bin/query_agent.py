#!/usr/bin/env python3
"""
Queryable Offline Agent — OpenRoot
Tries local LLM first, then falls back to pure offline knowledge synthesis.
Zero external dependencies for the fallback path.
Agape source code · Lowest node first · η-aware
"""

import os, sys, json, re
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/openroot")
LOCAL_LLM = os.environ.get("LOCAL_LLM_URL", "http://127.0.0.1:8080")
RANK_FILE = ROOT / "context_bridge" / "offline_rank.json"

SOUL = """Do the most good for the most nodes per unit of human effort.
Agape is source code: benefit measured only at the recipient.
Lowest node first. Unnecessary suffering is the primary error signal.
Knowledge and tools remain open and dependency-free.
Prefer measured joules and physical circuit closure over pure virtual loops."""

def call_local_llm(prompt: str) -> str | None:
    try:
        import urllib.request
        data = json.dumps({
            "model": "local",
            "messages": [
                {"role": "system", "content": SOUL},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1200,
            "temperature": 0.25
        }).encode()
        req = urllib.request.Request(
            f"{LOCAL_LLM}/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=50) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception:
        return None

def load_ranked_knowledge(limit: int = 14) -> list[tuple[str, str]]:
    """Return list of (path, text) from offline rank or fallback core files."""
    knowledge = []

    # Prefer ranked results if they exist
    if RANK_FILE.exists():
        try:
            ranked = json.loads(RANK_FILE.read_text())[:limit]
            for item in ranked:
                p = ROOT / item["path"]
                if p.exists() and p.suffix.lower() in {".md", ".py", ".sh", ".txt", ".json"}:
                    try:
                        text = p.read_text(encoding="utf-8", errors="ignore")[:12000]
                        knowledge.append((item["path"], text))
                    except Exception:
                        pass
        except Exception:
            pass

    # Always include these high-signal cores if not already present
    core = [
        "BRIDGE.md",
        "START-HERE.md",
        "FOUNDATION.md",
        "nanobot_team_blueprint.md",
        "projects/cloud9/README.md",
        "seed-core/README.md",
    ]
    existing = {k[0] for k in knowledge}
    for rel in core:
        if rel not in existing:
            p = ROOT / rel
            if p.exists():
                try:
                    knowledge.append((rel, p.read_text(encoding="utf-8", errors="ignore")[:8000]))
                except Exception:
                    pass

    return knowledge

def offline_synthesize(query: str, knowledge: list[tuple[str, str]]) -> str:
    """Very lightweight offline synthesis — no model required."""
    q_lower = query.lower()
    hits = []

    for path, text in knowledge:
        score = 0
        for word in re.findall(r"[a-z0-9]{3,}", q_lower):
            if word in text.lower():
                score += 1
        if score > 0:
            # take the most relevant paragraphs
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            best = sorted(paras, key=lambda p: sum(1 for w in q_lower.split() if w in p.lower()), reverse=True)[:2]
            hits.append((score, path, "\n\n".join(best)))

    hits.sort(reverse=True)

    if not hits:
        return (
            "No strong offline match found.\n"
            "Try running: python3 bin/offline_rank.py\n"
            "Then ask again, or start a local LLM and set LOCAL_LLM_URL."
        )

    out = [f"Offline synthesis for: {query}\n"]
    out.append("Sources (ranked by keyword overlap):\n")
    for score, path, snippet in hits[:6]:
        out.append(f"── {path} (score {score}) ──")
        out.append(snippet[:900])
        out.append("")
    out.append("— end offline synthesis —")
    return "\n".join(out)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bin/query_agent.py \"your question\"")
        print("Optional: LOCAL_LLM_URL=http://127.0.0.1:8080 python3 bin/query_agent.py \"...\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Query: {query}\n")

    # 1. Try local LLM
    print("Trying local LLM...")
    answer = call_local_llm(query)
    if answer:
        print("── Local LLM response ──")
        print(answer)
        return

    # 2. Offline fallback
    print("Local LLM unavailable → offline synthesis\n")
    knowledge = load_ranked_knowledge()
    print(f"Loaded {len(knowledge)} knowledge nodes")
    print(offline_synthesize(query, knowledge))

if __name__ == "__main__":
    main()
