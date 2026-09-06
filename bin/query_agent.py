#!/usr/bin/env python3
"""
Queryable Offline Agent
Tries local LLM first, then falls back to offline knowledge synthesis.
Zero external dependencies for the fallback path.
Agape source code • Lowest node first
"""

import os, sys, json, re, urllib.request
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/openroot")
LOCAL_LLM = os.environ.get("LOCAL_LLM_URL", "http://127.0.0.1:8080")

SOUL = """Do the most good for the most nodes per unit of human effort.
Agape is source code: benefit measured only at the recipient.
Lowest node first. Unnecessary suffering is the primary error signal.
Knowledge and tools remain open and dependency-free."""

def call_local_llm(prompt: str) -> str | None:
    """Try local OpenAI-compatible endpoint. Return None on failure."""
    try:
        data = json.dumps({
            "model": "local",
            "messages": [
                {"role": "system", "content": SOUL},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.3
        }).encode()
        req = urllib.request.Request(
            f"{LOCAL_LLM}/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception:
        return None

def load_knowledge(limit=12):
    """Pull the highest-signal local files for offline synthesis."""
    candidates = [
        ROOT / "BRIDGE.md",
        ROOT / "case-study" / "docs" / "SYSTEM-WIRING.md",
        ROOT / "case-study" / "docs" / "AGAPE-CORRECTIVE.md",
        ROOT / "case-study" / "docs" / "REDIRECTION-OS.md",
        ROOT / "case-study" / "docs" / "FLOOR-RISING-SIMULATION.md",
        ROOT / "docs" / "axioms" / "COMPOUNDING-COOPERATION.md",
        ROOT / "THESIS.md",
        ROOT / "nanobot_team_blueprint.md",
    ]
    chunks = []
    for p in candidates:
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")[:3000]
                chunks.append(f"### {p.name}\n{text}")
            except Exception:
                pass
    return "\n\n".join(chunks[:limit])

def offline_synthesize(question: str) -> str:
    """Pure offline answer from local knowledge + Agape framing."""
    knowledge = load_knowledge()
    # Very simple keyword-guided extraction
    q = question.lower()
    relevant = []
    for block in knowledge.split("### "):
        if any(w in block.lower() for w in re.findall(r"\w+", q) if len(w) > 3):
            relevant.append(block[:800])
    body = "\n---\n".join(relevant[:4]) if relevant else knowledge[:2000]

    return f"""[OFFLINE SYNTHESIS — no local LLM detected]

Question: {question}

Agape framing: benefit is measured only at the recipient. Lowest node first.

Relevant local knowledge:
{body}

---
Next action suggestions:
- If this is about capital → check leveling-cooperative or business-leveling ledgers
- If this is about knowledge rank → run: python3 bin/offline_rank.py
- If this is about system state → cat BRIDGE.md
- For real generative depth, start a local model and set LOCAL_LLM_URL
"""

def answer(question: str) -> str:
    print("Trying local LLM...", file=sys.stderr)
    result = call_local_llm(question)
    if result:
        return f"[LOCAL LLM]\n{result}"
    print("Local LLM unavailable — using offline knowledge synthesis.", file=sys.stderr)
    return offline_synthesize(question)

def main():
    print("=" * 56)
    print("Queryable Offline Agent")
    print("Local LLM first → offline knowledge fallback")
    print("=" * 56)
    print(SOUL)
    print()

    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(answer(q))
        return

    print("Type a question and press Enter. Type 'quit' to exit.\n")
    while True:
        try:
            q = input("query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nYield obtained.")
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit", "q"):
            print("Yield obtained.")
            break
        print()
        print(answer(q))
        print()

if __name__ == "__main__":
    main()
