#!/usr/bin/env python3
"""Repo link checker — governor/TASK-005. Stdlib only."""
import re, sys
from pathlib import Path
from urllib.request import Request, urlopen
repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
mds = list(repo.rglob("*.md"))
urls = set()
for md in mds:
    for m in re.finditer(r"https?://[^\s)\]]+", md.read_text(errors="ignore")):
        urls.add(m.group(0).rstrip("."))
broken = []
for u in sorted(urls):
    try:
        r = urlopen(Request(u, method="HEAD", headers={"User-Agent": "OpenRoot/1.0"}), timeout=15)
        if r.status >= 400: broken.append((u, r.status))
    except Exception as e: broken.append((u, str(e)[:60]))
print(f"Checked {len(urls)} URLs in {len(mds)} files")
for u, e in broken:
    print(f"  BROKEN {e}: {u}")
sys.exit(1 if broken else 0)
