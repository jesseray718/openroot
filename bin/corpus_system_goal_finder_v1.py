#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""corpus_system_goal_finder_v1.py — rank local files that describe the
full OpenRoot system + goal, for GitHub-facing documentation.
CANARY:OPENROOT-CORPUS-GOAL-FINDER-V1
Idempotent. Writes report to context_bridge/harvest/.
"""
import os, re, json, time, sqlite3, hashlib
from pathlib import Path

# ---- config (absolute paths, no ~) ----
SCAN_ROOTS = [
    "/home/jesse/openroot",
    "/home/jesse/src/openroot",
]
EXCLUDE_DIRS = {".git", "venv", "__pycache__", "node_modules", ".ollama",
                ".cache", "target", "vendor_archive", "_archive"}
EXTS = {".md", ".txt", ".org", ".markdown"}
MAX_FILE_BYTES = 400_000        # skip huge files
MAX_FILES = 25_000              # hard cap for the thesis tree
REPORT_DIR = Path("/home/jesse/openroot/context_bridge/harvest")
DB_PATH = Path("/home/jesse/openroot/data/corpus_goal_index.db")

# goal/system vocabulary — weighted keywords
KEYWORDS = {
    "system": 2, "systems": 2, "goal": 3, "goals": 2, "mission": 3,
    "vision": 3, "architecture": 3, "overview": 3, "roadmap": 2,
    "constitution": 4, "manifesto": 4, "philosophy": 3, "doctrine": 3,
    "permaculture": 2, "agape": 2, "ledger": 1, "popw": 2,
    "newton chain": 2, "openroot": 1, "master": 2, "thesis": 2,
    "objective": 2, "purpose": 3, "framework": 2, "protocol": 2,
}
QUERY_TEXT = "complete system overview mission goal architecture of openroot project for github readme"

STOP = set("a an the and or of to in for with on is are be this that it as at by we our your you i".split())

def norm_words(text):
    return [w for w in re.findall(r"[a-z][a-z0-9_-]{2,}", text.lower()) if w not in STOP]

def keyword_score(text):
    t = text.lower()
    score = 0.0
    hits = {}
    for kw, w in KEYWORDS.items():
        c = t.count(kw)
        if c:
            score += w * min(c, 8)      # diminishing returns per keyword
            hits[kw] = c
    # headings boost
    headings = re.findall(r"^#{1,3}\s+.*$", text, re.M)
    score += sum(1 for h in headings if any(k in h.lower() for k in KEYWORDS)) * 1.5
    # length penalty: prefer substantial-but-focused docs
    n = len(text.split())
    if n < 150 or n > 25000:
        score *= 0.5
    return score, hits, n

def read_text(p):
    try:
        if p.stat().st_size > MAX_FILE_BYTES:
            return None
        return p.read_text("utf-8", errors="replace")
    except OSError:
        return None

def ollama_embed(text):
    import urllib.request
    body = json.dumps({"model": "nomic-embed-text", "input": text[:4000]}).encode()
    req = urllib.request.Request("http://localhost:11434/api/embed",
                                  data=body,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        emb = json.load(r)["embeddings"][0]
    return emb

def cos(a, b):
    na = sum(x*x for x in a) ** 0.5 or 1.0
    nb = sum(x*x for x in b) ** 0.5 or 1.0
    return sum(x*y for x, y in zip(a, b)) / (na * nb)

def main():
    t0 = time.time()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("""CREATE TABLE IF NOT EXISTS files(
        path TEXT PRIMARY KEY, sha256 TEXT, bytes INT, words INT,
        kw_score REAL, emb_dist REAL, combo REAL,
        top_hits TEXT, scanned_at TEXT)""")

    # gather candidates
    candidates, seen = [], set()
    for root in SCAN_ROOTS:
        rootpath = Path(root)
        if not rootpath.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(rootpath):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in filenames:
                if Path(fn).suffix.lower() in EXTS:
                    p = Path(dirpath) / fn
                    if p not in seen:
                        seen.add(p)
                        candidates.append(p)
                        if len(candidates) >= MAX_FILES:
                            break
            if len(candidates) >= MAX_FILES:
                break
    print(f"[scan] {len(candidates)} candidate files in "
          f"{time.time()-t0:.1f}s")

    # embed query (optional)
    query_vec = None
    try:
        query_vec = ollama_embed(QUERY_TEXT)
        print("[embed] nomic-embed-text live — semantic ranking ON")
    except Exception as e:
        print(f"[embed] Ollama/nomic unavailable ({type(e).__name__}) — keyword-only ranking")

    # score
    rows = []
    for p in candidates:
        txt = read_text(p)
        if not txt:
            continue
        ks, hits, nw = keyword_score(txt)
        emb_dist = None
        if query_vec is not None:
            try:
                vec = ollama_embed(txt)
                sim = cos(query_vec, vec)
                emb_dist = 1.0 - sim
            except Exception:
                emb_dist = None
        combo = ks if emb_dist is None else ks * (0.5) + (10.0 * (1.0 - emb_dist)) * (0.5)
        rows.append((str(p), nw, ks, emb_dist, combo, json.dumps(
            dict(sorted(hits.items(), key=lambda kv: -kv[1])[:6]))))
    print(f"[score] {len(rows)} files scored")

    # persist
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    db.execute("DELETE FROM files")
    for path, nw, ks, ed, combo, hits_json in rows:
        sha = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        db.execute("INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?,?,?,?)",
                   (path, sha, Path(path).stat().st_size, nw, ks, ed, combo, hits_json, now))
    db.commit()

    # shortlist: top 25 by combo, prefer shorter cluster-diverse picks
    rows.sort(key=lambda r: -(r[4]))
    top = rows[:25]

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    report = REPORT_DIR / f"system-goal-shortlist-{ts}.md"
    lines = [
        "# OpenRoot System/Goal Document Shortlist",
        f"\nGenerated: {now}  \nCanary: CANARY:OPENROOT-CORPUS-GOAL-FINDER-V1  ",
        f"Scan roots: {', '.join(SCAN_ROOTS)}  ",
        f"Semantic ranking: {'ON' if query_vec else 'OFF (keyword-only)'}",
        "\n## Top 25 candidates (best GitHub-facing system/goal docs)",
        "",
        "| # | Score | Words | Top keyword hits | Path |",
        "|---|-------|-------|------------------|------|",
    ]
    for i, (path, nw, ks, ed, combo, hits_json) in enumerate(top, 1):
        hits = ", ".join(f"{k}:{v}" for k, v in json.loads(hits_json).items())
        lines.append(f"| {i} | {combo:.1f} | {nw} | {hits} | `{path}` |")
    lines += [
        "",
        "## Recommended merge set for GitHub",
        "",
        "Pick 3–5 of the top files whose paths suggest: constitution/master doc, "
        "README-adjacent overview, philosophy doc, roadmap. Copy them into the repo root "
        "or docs/ and link from README.md.",
        "",
        f"Index DB: `{DB_PATH}`",
    ]
    report.write_text("\n".join(lines), "utf-8")
    print(f"\n=== TOP 10 ===")
    for i, (path, nw, ks, ed, combo, _) in enumerate(top[:10], 1):
        print(f"{i:2}. {combo:7.1f}  {path}")
    print(f"\n[banked] report: {report}")
    print(f"[banked] index db: {DB_PATH} ({len(rows)} rows)")
    db.close()

if __name__ == "__main__":
    main()
