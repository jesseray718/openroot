#!/usr/bin/env python3
"""OpenRoot Audit Scanner v3.1 - Fixed Regex"""
import os, json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/sdcard/openroot")
OUT = ROOT / "dossier.json"
LOG = ROOT / "logs" / "audit.log"
EXCLUDE = {".git", "__pycache__", "node_modules", ".cargo", "target", "build", ".venv", "dist"}

def safe_read(p):
    try: return p.read_text(errors="ignore")[:20000]
    except: return ""

def sha256_safe(p):
    h = hashlib.sha256()
    try:
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
        return h.hexdigest()
    except: return "HASH_ERROR"

def detect_type(p):
    ext = p.suffix.lower()
    if ext == ".py": return "script-python"
    if ext in (".ts", ".tsx"): return "script-typescript"
    if ext in (".js", ".jsx"): return "script-javascript"
    if ext == ".svelte": return "component-svelte"
    if ext == ".rs": return "script-rust"
    if ext in (".cpp", ".cc"): return "code-cpp"
    if ext in (".h", ".hpp"): return "header-cpp"
    if ext == ".sh": return "script-shell"
    if ext == ".md": return "document-markdown"
    if ext == ".json": return "data-json"
    if ext in (".yaml", ".yml"): return "data-yaml"
    if ext == ".toml": return "config-toml"
    if ext in (".txt", ".log"): return "text-log"
    if ext == ".jsonl": return "data-jsonl"
    if ext in (".jpg", ".png", ".webp", ".svg"): return "asset-image"
    if ext in (".zip", ".tar", ".gz"): return "archive"
    return "other"

print("Indexing files...")
all_files = []
all_basenames = {}
all_dirs = set()
for f in sorted(ROOT.rglob("*")):
    if any(ex in f.parts for ex in EXCLUDE): continue
    if f.is_dir():
        all_dirs.add(str(f.relative_to(ROOT)))
        continue
    if f.name == "dossier.json": continue
    rel = str(f.relative_to(ROOT))
    all_files.append(f)
    all_basenames.setdefault(f.name, []).append(rel)
    all_basenames.setdefault(f.stem, []).append(rel)
    parts = rel.split("/")
    for i in range(len(parts) - 1):
        all_dirs.add("/".join(parts[:i+1]))
print(f"Indexed {len(all_files)} files in {len(all_dirs)} directories")

def find_links(path, content):
    links = []
    # Strategy 1: Import statements
    for m in re.finditer(r'(?:from|import)\s+([\w.]+)', content):
        raw = m.group(1).replace(".", "/")
        candidates = [
            path.parent / (raw + ".py"),
            path.parent / (raw.split("/")[-1] + ".py"),
            path.parent.parent / (raw.split("/")[-1] + ".py"),
            ROOT / (raw + ".py"),
            ROOT / (raw.split("/")[-1] + ".py"),
            path.parent / raw / "__init__.py",
            ROOT / raw / "__init__.py",
        ]
        for c in candidates:
            try:
                resolved = c.resolve()
                if resolved.exists() and resolved.is_file():
                    rel = str(resolved.relative_to(ROOT))
                    if rel != str(path.relative_to(ROOT)):
                        links.append(rel)
            except: pass
    
    # Strategy 2: Quoted strings (filenames)
    # Matches "something.ext" or 'something.ext'
    pattern_quoted = r'''["']([^"']{3,80})["']'''
    for m in re.finditer(pattern_quoted, content):
        raw = m.group(1).strip()
        if raw.startswith("http") or raw.startswith("#"): continue
        
        # Check exact basename match
        if raw in all_basenames:
            for t in all_basenames[raw]:
                if t != str(path.relative_to(ROOT)):
                    links.append(t)
        
        # Check stem match (name without extension)
        raw_stem = Path(raw).stem
        if raw_stem in all_basenames:
            for t in all_basenames[raw_stem]:
                if t != str(path.relative_to(ROOT)):
                    links.append(t)
    
    # Strategy 3: Paths with extensions
    pattern_path = r'''["']([^"']+\.\w{2,5})["']'''
    for m in re.finditer(pattern_path, content):
        raw = m.group(1).strip()
        if raw.startswith("http"): continue
        candidates = [path.parent / raw, ROOT / raw, path.parent / raw.lstrip("./")]
        for c in candidates:
            try:
                resolved = c.resolve()
                if resolved.exists() and resolved.is_file():
                    rel = str(resolved.relative_to(ROOT))
                    if rel != str(path.relative_to(ROOT)):
                        links.append(rel)
            except: pass
    
    return sorted(set(links))

print("Building directory tree...")
tree = {}
for f in all_files:
    rel = str(f.relative_to(ROOT))
    parts = rel.split("/")
    node = tree
    for part in parts[:-1]:
        if part not in node:
            node[part] = {"_type": "dir", "_children": {}}
        node = node[part]["_children"]
    node[parts[-1]] = {"_type": "file", "_size": f.stat().st_size, "_ext": f.suffix.lower()}

dossier = {
    "meta": {"project": "openroot", "time": datetime.now(timezone.utc).isoformat(), "ver": "3.1-fixed"},
    "tree": tree, "files": [], "connections": [], "stats": {}
}

print("Scanning files for links...")
total_bytes = 0
count = 0
for f in sorted(all_files):
    count += 1
    if count % 500 == 0: print(f"  Processed {count}/{len(all_files)}...")
    try:
        sz = f.stat().st_size
        total_bytes += sz
    except: sz = 0
    rel = str(f.relative_to(ROOT))
    content = safe_read(f)
    h = sha256_safe(f)
    links = find_links(f, content)
    ftype = detect_type(f)
    lines = len(content.splitlines()) if content else 0
    parent = str(f.parent.relative_to(ROOT)) if f.parent != ROOT else "ROOT"
    imports = []
    for m in re.finditer(r'(?:from|import)\s+([\w.]+)', content):
        imports.append(m.group(1))
    dossier["files"].append({
        "path": rel, "name": f.name, "parent": parent, "type": ftype,
        "ext": f.suffix, "size": sz, "hash": h, "lines": lines,
        "imports": sorted(set(imports))[:20], "links": links, "link_count": len(links)
    })
    for tgt in links:
        dossier["connections"].append({"from": rel, "to": tgt})

# Add structural connections
for f in all_files:
    rel = str(f.relative_to(ROOT))
    parent = str(f.parent.relative_to(ROOT)) if f.parent != ROOT else "ROOT"
    if parent != "ROOT":
        dossier["connections"].append({"from": parent + "/", "to": rel, "type": "contains"})
    siblings = [s for s in all_files if s.parent == f.parent and s != f]
    for sib in siblings[:5]:
        sib_rel = str(sib.relative_to(ROOT))
        dossier["connections"].append({"from": rel, "to": sib_rel, "type": "sibling"})

# Dedupe
seen = set()
unique = []
for c in dossier["connections"]:
    k = (c["from"], c["to"])
    if k not in seen:
        seen.add(k)
        unique.append(c)
dossier["connections"] = unique

# Stats
types = {}
for f in dossier["files"]:
    types[f["type"]] = types.get(f["type"], 0) + 1
most_conn = max(dossier["files"], key=lambda x: x["link_count"])["path"] if dossier["files"] else "none"
orphans = sum(1 for f in dossier["files"] if f["link_count"] == 0)
dossier["stats"] = {
    "total_files": len(dossier["files"]),
    "total_dirs": len(all_dirs),
    "total_links": len([c for c in dossier["connections"] if c.get("type") != "sibling"]),
    "total_connections": len(dossier["connections"]),
    "sibling_connections": len([c for c in dossier["connections"] if c.get("type") == "sibling"]),
    "containment_connections": len([c for c in dossier["connections"] if c.get("type") == "contains"]),
    "total_bytes": total_bytes,
    "orphans": orphans,
    "most_connected": most_conn,
    "by_type": types,
    "time": datetime.now(timezone.utc).isoformat()
}

OUT.write_text(json.dumps(dossier, indent=2, ensure_ascii=False))
LOG.parent.mkdir(parents=True, exist_ok=True)
with open(LOG, "a") as lf:
    lf.write(f"[{datetime.now(timezone.utc).isoformat()}] STRUCTURAL: {len(dossier['files'])} files, {len(dossier['connections'])} connections\n")

print("=" * 50)
print("  STRUCTURAL AUDIT COMPLETE")
print("=" * 50)
print(f"  Files: {len(dossier['files'])}")
print(f"  Directories: {len(all_dirs)}")
print(f"  All Connections: {len(dossier['connections'])}")
print(f"  Contains: {dossier['stats']['containment_connections']}")
print(f"  Siblings: {dossier['stats']['sibling_connections']}")
print(f"  Cross-refs: {dossier['stats']['total_links']}")
print(f"  Size: {total_bytes:,} bytes")
print(f"  Orphans: {orphans}")
print(f"  Most Connected: {most_conn}")
print(f"  Output: {OUT}")
print("=" * 50)
