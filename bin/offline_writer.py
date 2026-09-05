#!/usr/bin/env python3
"""
Offline Code Writer — OpenRoot
Uses ranked local knowledge + simple templates to propose code improvements
and small self-upgrade loops without any network.
"""

import os, sys, json, re
from pathlib import Path
from datetime import datetime

ROOT = Path("/data/data/com.termux/files/home/openroot")
RANK_FILE = ROOT / "context_bridge" / "offline_rank.json"
OUT_DIR = ROOT / "context_bridge" / "writer_proposals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_top_code_files(limit=20):
    files = []
    if RANK_FILE.exists():
        try:
            ranked = json.loads(RANK_FILE.read_text())
            for item in ranked:
                p = ROOT / item["path"]
                if p.suffix.lower() in {".py", ".sh"} and p.exists():
                    files.append(p)
                    if len(files) >= limit:
                        break
        except Exception:
            pass
    return files

def propose_improvement(task: str, files: list[Path]) -> str:
    """Generate a concrete proposal based on local patterns."""
    task_l = task.lower()
    related = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")[:6000]
            if any(w in text.lower() for w in task_l.split() if len(w) > 3):
                related.append((f.relative_to(ROOT), text[:1500]))
        except Exception:
            pass

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    proposal = []
    proposal.append(f"# Offline Writer Proposal — {stamp}")
    proposal.append(f"# Task: {task}")
    proposal.append("")
    proposal.append("## Intent")
    proposal.append("Produce a small, testable improvement that can run fully offline.")
    proposal.append("Respect η (useful joules / human joules) and lowest-node first.")
    proposal.append("")

    if related:
        proposal.append("## Related local files found")
        for path, _ in related[:6]:
            proposal.append(f"- {path}")
        proposal.append("")
        proposal.append("## Suggested next concrete step")
        proposal.append("1. Read the highest-ranked related file fully")
        proposal.append("2. Extract the core function or loop that matches the task")
        proposal.append("3. Write a minimal improved version into a new file under bin/ or computational_flow/")
        proposal.append("4. Add a one-line smoke test")
        proposal.append("5. Run offline_rank.py again so the new file enters the ranking")
    else:
        proposal.append("## No strong local match")
        proposal.append("Start with a minimal stub:")
        proposal.append("```python")
        proposal.append("#!/usr/bin/env python3")
        proposal.append(f'"""Offline task: {task}"""')
        proposal.append("def main():")
        proposal.append("    print('stub — implement offline')")
        proposal.append("if __name__ == '__main__':")
        proposal.append("    main()")
        proposal.append("```")

    proposal.append("")
    proposal.append("## Self-upgrade loop (offline)")
    proposal.append("```bash")
    proposal.append("python3 bin/offline_rank.py")
    proposal.append("python3 bin/query_agent.py \"improve the offline writer itself\"")
    proposal.append("python3 bin/offline_writer.py \"add better pattern matching to offline_writer\"")
    proposal.append("```")

    return "\n".join(proposal)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bin/offline_writer.py \"describe the code improvement you want\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    print(f"Offline writer task: {task}\n")

    files = load_top_code_files()
    print(f"Scanned {len(files)} ranked code files")

    text = propose_improvement(task, files)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = OUT_DIR / f"proposal_{stamp}.md"
    out.write_text(text)
    print(text)
    print(f"\nProposal saved → {out}")

if __name__ == "__main__":
    main()
