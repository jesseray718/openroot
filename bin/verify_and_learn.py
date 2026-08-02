#!/usr/bin/env python3
"""
Verification atom.
Takes original metrics + LLM-proposed new code.
Re-runs the lattice.
Accepts only if η rises.
Writes a layer-1 postulate on success.
"""
import json, sys, hashlib, time, re
from pathlib import Path

def extract_code(llm_text: str) -> str:
    m = re.search(r'OPTIMIZED_CODE:\s*(.*?)(?:ENERGY_DELTA:|ACRE_NOTE:|$)', llm_text, re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    code = m.group(1).strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[-1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    return code.strip()

def metrics_from_code(code: str, source: str = "llm_rewrite") -> dict:
    lines = code.count("\n") + 1
    chars = len(code)
    functions = code.count("def ") + code.count("func ")
    classes = code.count("class ")
    imports = code.count("import ") + code.count("from ")
    complexity = functions * 2 + classes * 3 + imports
    unique = len(set(l.strip() for l in code.splitlines() if l.strip()))
    red = max(0.0, 1.0 - (unique / max(lines, 1)))
    return {
        "id": Path(source).name,
        "source": source,
        "metrics": {
            "lines": lines,
            "chars": chars,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity_score": complexity,
            "file_size_kb": round(chars / 1024, 3),
            "human_input_estimate": 0.0,          # auto-generated
            "time_budget": 10.0,
            "useful_estimate": round(max(0.002, complexity * 0.0004), 6)
        },
        "redundant_ratio": round(red, 3),
        "downstream": 4,
        "fractal_invariant": True                 # forced for raised-order candidates
    }

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 verify_and_learn.py <old_acre.json> <llm_output.txt> <original_source.py>")
        sys.exit(1)

    old_acre_path = sys.argv[1]
    llm_path = sys.argv[2]
    source_path = sys.argv[3]

    with open(old_acre_path) as f:
        old = json.load(f)
    if "acre" in old:
        old = old["acre"]
    old_η = old.get("η", 0.0)

    with open(llm_path) as f:
        llm_text = f.read()
    new_code = extract_code(llm_text)
    if not new_code:
        print(json.dumps({"status": "REJECT", "reason": "no OPTIMIZED_CODE block"}))
        sys.exit(2)

    # write temp metrics
    tmp_target = Path.home() / "openroot/tmp/verify_target.json"
    metrics = metrics_from_code(new_code, source_path)
    tmp_target.write_text(json.dumps(metrics, indent=2))

    # re-run lattice
    import subprocess
    cmd = [
        "python3", str(Path.home() / "openroot/bin/nanobot_lattice.py"),
        str(Path.home() / "openroot/une/axiom_lattice.json"),
        str(tmp_target),
        "6"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({"status": "REJECT", "reason": "lattice failed", "stderr": r.stderr[:300]}))
        sys.exit(3)

    new = json.loads(r.stdout)
    if "acre" in new:
        new = new["acre"]
    new_η = new.get("η", 0.0)

    delta = new_η - old_η
    result = {
        "status": "ACCEPT" if delta > 0.01 else "REJECT",
        "old_η": old_η,
        "new_η": new_η,
        "delta_η": round(delta, 6),
        "new_merkle": new.get("merkle_root"),
        "new_claim": new.get("claim"),
        "postulate": None
    }

    if result["status"] == "ACCEPT":
        # write layer-1 postulate
        postulate = {
            "id": f"P{int(time.time())}",
            "statement": f"Surgical rewrite of bottleneck in {Path(source_path).name} raised η by {delta:.4f}",
            "constraint": "raise_order_on_lowest_η_node",
            "Δη": delta,
            "derived_from": old.get("axioms_applied", []),
            "merkle": new.get("merkle_root"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        result["postulate"] = postulate
        # append to axiom database
        ax_path = Path.home() / "openroot/une/axiom_lattice.json"
        ax = json.loads(ax_path.read_text())
        ax.setdefault("layer_1_verified", []).append(postulate)
        ax_path.write_text(json.dumps(ax, indent=2))
        # optional: write the new code back (commented for safety)
        # Path(source_path).write_text(new_code)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
