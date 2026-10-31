# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
import hashlib, json, os, re, time

ROOT = "/home/jesse/openroot"
DOCS = os.path.join(ROOT, "genesis/founding_docs")
OUT  = os.path.join(ROOT, "genesis/theorem_registry.jsonl")
CANARY = "CANARY:OPENROOT-THEOREM-REGISTRY-V1"

def sha(b): return hashlib.sha256(b).hexdigest()

print(f"[gate] {CANARY} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

MARKERS = [
    r"(?i)proof[- ]pending",
    r"(?i)theorem\s*:.*?\((?:proof[- ]pending|unproven)\)",
    r"(?i)^\s*(?:theorem|proposition|lemma)\s+[A-Z]+-\d+.*$",
]

registry, doc_stats = [], {}
for name in sorted(os.listdir(DOCS)):
    if not name.endswith(".md"):
        continue
    path = os.path.join(DOCS, name)
    text = open(path, "rb").read()
    h = sha(text)
    lines = text.decode("utf-8", "replace").splitlines()
    pending = []
    for i, line in enumerate(lines, 1):
        if re.search(MARKERS[0], line):
            pending.append((i, line.strip()))
        elif re.search(MARKERS[2], line):
            ctx = "\n".join(lines[i:i+6])
            if not re.search(r"(?i)proof:?\s*(?:complete|done|proved|sealed|\u2713)", ctx):
                if "theorem" in line.lower():
                    pending.append((i, line.strip()))
    doc_stats[name] = pending
    for ln, stmt in pending:
        tid = f"TH-{name[:2].upper()}-{len(registry)+1:03d}"
        registry.append({
            "id": tid, "doc": name, "line": ln,
            "statement": stmt[:400],
            "statement_sha256": sha(stmt.encode()),
            "doc_sha256": h,
            "status": "proof-pending",
            "proof_method": None,
            "layer": "tier-B-human-attested",
        })

with open(OUT, "w") as f:
    for r in registry:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

merkle = sha("\n".join(sorted(r["statement_sha256"] for r in registry)).encode())
print("=== registry summary ===")
for name, pend in doc_stats.items():
    if pend:
        print(f"  {name}: {len(pend)} pending")
print(f"total proof-pending: {len(registry)}")
print(f"registry: {OUT}")
print(f"merkle_root(statements): {merkle}")
print(f"REGISTRY_MERKLE={merkle}")
print(f"REGISTRY_COUNT={len(registry)}")
print(f"{CANARY} COMPLETE [exit=0]")
