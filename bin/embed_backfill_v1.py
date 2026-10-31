# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
import sqlite3, json, urllib.request, sys
DB = "/home/jesse/openroot/data/pathways.db"
c = sqlite3.connect(DB)
c.execute("CREATE TABLE IF NOT EXISTS embeddings(row_sha TEXT PRIMARY KEY, dim INTEGER, vec TEXT)")
rows = c.execute("SELECT row_sha, report_path FROM pathways WHERE report_path IS NOT NULL").fetchall()
done = 0
for row_sha, rp in rows:
    if c.execute("SELECT 1 FROM embeddings WHERE row_sha=?", (row_sha,)).fetchone():
        continue
    try:
        text = open(rp, errors="replace").read()
        body = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode()
        req = urllib.request.Request("http://localhost:11434/api/embeddings", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            vec = json.loads(r.read())["embedding"]
        c.execute("INSERT OR REPLACE INTO embeddings VALUES(?,?,?)", (row_sha, len(vec), json.dumps(vec)))
        c.commit()
        done += 1
        print(f"[banked] embedded {rp.split('/')[-1]} dim={len(vec)}")
    except Exception as e:
        print(f"[held] failed {rp}: {e}")
c.close()
print(f"[banked] backfill complete: {done} new embeddings")
sys.exit(0)
