#!/usr/bin/env python3
"""Atomic metrics extractor. Output is valid target.json for the lattice."""
import sys, json
from pathlib import Path

def extract(path: str) -> dict:
    p = Path(path)
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return {"error": str(e)}
    lines = content.count("\n") + 1
    chars = len(content)
    functions = content.count("def ") + content.count("func ") + content.count("function ")
    classes = content.count("class ")
    imports = content.count("import ") + content.count("from ")
    complexity = functions * 2 + classes * 3 + imports
    unique_lines = len(set(l.strip() for l in content.splitlines() if l.strip()))
    redundant_ratio = max(0.0, 1.0 - (unique_lines / max(lines, 1)))
    return {
        "id": p.name,
        "source": str(p.resolve()),
        "metrics": {
            "lines": lines,
            "chars": chars,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity_score": complexity,
            "file_size_kb": round(chars / 1024, 3),
            "human_input_estimate": round(complexity * 0.5, 2),
            "time_budget": 30.0,
            "useful_estimate": round(max(0.001, complexity * 0.00025), 6)
        },
        "redundant_ratio": round(redundant_ratio, 3),
        "downstream": 3,
        "fractal_invariant": False
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_metrics.py <file>")
        sys.exit(1)
    print(json.dumps(extract(sys.argv[1]), indent=2))
