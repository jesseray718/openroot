#!/usr/bin/env python3
"""
openroot audit: scan repo → dossier.json
- Walks /sdcard/openroot recursively
- Records file metadata, size, hash, type, lines
- Infers connections via imports/includes/references
- Outputs dossier.json with full interconnectivity map
"""

import os
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/sdcard/openroot")
OUT  = ROOT / "dossier.json"
LOG  = ROOT / "logs" / "audit.log"

EXCLUDE_DIRS = {'.git', '__pycache__', '.DS_Store', 'node_modules', '.cache'}

PATTERNS = {
    'py': [
        r'^\s*import\s+([\w.]+)',
        r'^\s*from\s+([\w.]+)\s+import',
        r'open\([\'"](.*?)[\'"]',
        r'Path\([\'"](.*?)[\'"]',
        r'/([\w\-]+/(?:bin|relay|storage|lessons|aec|logs)/[\w\-\.]+)',
    ],
    'sh': [
        r'source\s+([^\s]+)',
        r'\./([\w\-\.]+\.sh)',
        r'/sdcard/openroot/([\w\-/.]+)',
        r'cat\s+(/sdcard/openroot/[\w\-/.]+)',
        r'bash\s+([^\s]+)',
    ],
    'md': [
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'```(\w+)',
        r'/sdcard/openroot/([\w\-/.]+)',
    ],
    'json': [
        r'"path"\s*:\s*"([^"]+)"',
        r'"file"\s*:\s*"([^"]+)"',
        r'"import"\s*:\s*"([^"]+)"',
    ],
}


def sha256(p: Path) -> str:
    """Return SHA-256 hex digest of file content."""
    h = hashlib.sha256()
    try:
        for chunk in iter(lambda: p.read_bytes(65536), b''):
            h.update(chunk)
    except Exception:
        return "ERROR"
    return h.hexdigest()


def read_content(p: Path) -> str:
    """Read up to 5000 chars of text content."""
    try:
        return p.read_text(errors='ignore')[:5000]
    except Exception:
        return ""


def infer_links(path: Path, content: str) -> list:
    """Find cross-references to other files within openroot."""
    ext = path.suffix.lstrip('.')
    links = []

    for pat in PATTERNS.get(ext, []):
        for m in re.finditer(pat, content, re.MULTILINE):
            raw = m.group(1).strip()
            if raw.startswith('http') or raw.startswith('#'):
                continue

            # Try resolving as relative to current file
            candidates = [
                path.parent / raw,
                path.parent / (raw + path.suffix),
                ROOT / raw,
                ROOT / (raw + '.py'),
                ROOT / (raw + '.sh'),
                ROOT / (raw + '.md'),
            ]

            for c in candidates:
                try:
                    resolved = c.resolve()
                    if resolved.exists() and resolved.is_file():
                        rel = str(resolved.relative_to(ROOT))
                        if rel != str(path.relative_to(ROOT)):
                            links.append(rel)
                except Exception:
                    continue

    return sorted(set(links))


def detect_type(p: Path) -> str:
    """Classify file into a category."""
    ext = p.suffix.lower()
    name = p.name.lower()

    if ext == '.py':
        return 'script-python'
    elif ext == '.sh':
        return 'script-shell'
    elif ext == '.md':
        return 'document-markdown'
    elif ext == '.json':
        return 'data-json'
    elif ext in ('.txt', '.log'):
        return 'text-log'
    elif ext in ('.ots',):
        return 'timestamp-proof'
    elif ext in ('.zip', '.tar', '.gz'):
        return 'archive'
    elif name.startswith('.'):
        return 'hidden'
    else:
        return 'other'


def count_lines(content: str) -> int:
    """Count lines in content."""
    return len(content.splitlines()) if content else 0


def audit():
    """Main audit function — walks tree, builds dossier, writes JSON."""

    timestamp = datetime.now(timezone.utc).isoformat()
    dossier = {
        "meta": {
            "project": "openroot",
            "root_path": str(ROOT),
            "generated_at": timestamp,
            "auditor_version": "1.0.0",
        },
        "files": [],
        "connections": [],
        "stats": {},
    }

    file_map = {}
    total_bytes = 0

    for f in sorted(ROOT.rglob('*')):
        # Skip excluded dirs
        if any(ex in f.parts for ex in EXCLUDE_DIRS):
            continue
        if f.is_dir():
            continue
        if f.name == 'dossier.json':
            continue

        try:
            stat = f.stat()
            sz = stat.st_size
            total_bytes += sz
        except Exception:
            sz = 0

        rel       = str(f.relative_to(ROOT))
        content   = read_content(f)
        h         = sha256(f)
        links     = infer_links(f, content)
        ftype     = detect_type(f)
    lines     = count_lines(content)
        parent    = str(f.parent.relative_to(ROOT)) if f.parent != ROOT else "ROOT"

        meta = {
            "path": rel,
            "name": f.name,
            "parent_dir": parent,
            "type": ftype,
            "extension": f.suffix,
            "size_bytes": sz,
            "size_human": _human(sz),
            "sha256": h,
            "lines": lines,
            "links": links,
            "link_count": len(links),
            "modified": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat() if sz else "",
        }

        dossier["files"].append(meta)
        file_map[rel] = meta

        for tgt in links:
            dossier["connections"].append({"from": rel, "to": tgt})

    # Deduplicate connections
    seen = set()
    unique_conns = []
    for c in dossier["connections"]:
        key = (c["from"], c["to"])
        if key not in seen:
            seen.add(key)
            unique_conns.append(c)
    dossier["connections"] = unique_conns

    # Stats
    type_counts = {}
    for entry in dossier["files"]:
        t = entry["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    dossier["stats"] = {
        "total_files": len(dossier["files"]),
        "total_connections": len(dossier["connections"]),
        "total_bytes": total_bytes,
        "total_human": _human(total_bytes),
        "by_type": type_counts,
        "orphan_files": sum(1 for f in dossier["files"] if f["link_count"] == 0),
        "most_connected": max(
            dossier["files"], key=lambda x: x["link_count"]
        )["path"] if dossier["files"] else "none",
        "generated_at": timestamp,
    }

    # Write dossier.json
    OUT.write_text(json.dumps(dossier, indent=2, ensure_ascii=False))

    # Write log entry
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, 'a') as lf:
        lf.write(f"[{timestamp}] AUDIT COMPLETE\n")
        lf.write(f"  Files: {dossier['stats']['total_files']}\n")
        lf.write(f"  Connections: {dossier['stats']['total_connections']}\n")
        lf.write(f"  Total size: {dossier['stats']['total_human']}\n")
        lf.write(f"  Orphans: {dossier['stats']['orphan_files']}\n")
        lf.write(f"  Most connected: {dossier['stats']['most_connected']}\n")
        lf.write(f"  Output: {OUT}\n")
        lf.write("---\n")

    # Print summary to stdout
    print("=" * 60)
    print("  OPENROOT AUDIT — COMPLETE")
    print("=" * 60)
    print(f"  Files scanned:     {dossier['stats']['total_files']}")
    print(f"  Connections found:  {dossier['stats']['total_connections']}")
    print(f"  Total size:        {dossier['stats']['total_human']}")
    print(f"  Orphan files:      {dossier['stats']['orphan_files']}")
    print(f"  Most connected:    {dossier['stats']['most_connected']}")
    print(f"  Output written:    {OUT}")
    print(f"  Log appended:      {LOG}")
    print("=" * 60)
    print("\nBy type:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t:20s} {c}")
    print("\nDone. Open dossier.json in Markor or your editor of choice.")


def _human(n: int) -> str:
    """Convert bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


if __name__ == "__main__":
    audit()
