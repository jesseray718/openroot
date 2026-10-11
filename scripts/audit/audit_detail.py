#!/usr/bin/env python3
"""
audit_detail.py — read-only data-layer audit for the openroot node.
Safety: never writes to any DB (mode=ro URIs); never reads secret files;
output passes a token-redaction pass. Slower parts are bounded.
"""
import json, os, re, sqlite3, subprocess, sys, time
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
OR   = HOME / "openroot"

RE_PAT = [re.compile(p) for p in (
    r"gh[pousr]_[A-Za-z0-9]{16,}",
    r"github_pat_[A-Za-z0-9_]{16,}",
    r"sk-[A-Za-z0-9]{16,}",
    r"AKIA[0-9A-Z]{12,}",
    r"xox[baprs]-[A-Za-z0-9-]+",
    r"(?i)bearer\s+[A-Za-z0-9._-]{12,}",
)]
def red(s):
    s = str(s)
    for p in RE_PAT:
        s = p.sub("<REDACTED>", s)
    return s

L = []
def w(s=""): L.append(red(s))
def sec(t): w(); w("===== %s =====" % t)
def fmt_time(t): return time.strftime("%Y-%m-%d %H:%M", time.localtime(t))

def find_paths(pattern, root, maxdepth):
    try:
        r = subprocess.run(["find", str(root), "-maxdepth", str(maxdepth),
                            "-name", pattern],
                           capture_output=True, text=True, timeout=90)
        return [Path(p) for p in r.stdout.splitlines() if p.strip()]
    except Exception:
        return []

# --- 13. sqlite capability of this interpreter ---------------------
sec("13. SQLITE / FTS5 CAPABILITY (this python)")
try:
    _c = sqlite3.connect(":memory:")
    opts = [r[0] for r in _c.execute("PRAGMA compile_options")]
    _c.close()
    w("sqlite %s | FTS5 compiled in: %s" % (sqlite3.sqlite_version,
      any("FTS5" in o for o in opts)))
except Exception as e:
    w("could not probe sqlite: %s" % e)

# --- 14. database inventory ----------------------------------------
sec("14. DATABASE INVENTORY UNDER ~/openroot (read-only)")
SKIP = {".git", "node_modules", ".next", "venv", "__pycache__",
        ".aider.tags.cache.v4", "attic", "ctx_backup_20260923_194243"}
SHADOW = re.compile(r"_(data|idx|docsize|docid|config|content|segdir|segments)$")
dbs = []
for root, dirs, files in os.walk(OR):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if f.endswith((".db", ".sqlite", ".sqlite3")):
            dbs.append(Path(root) / f)
dbs.sort(key=lambda p: p.stat().st_size, reverse=True)
w("found %d db files; profiling top 25 by size" % len(dbs))
for db in dbs[:25]:
    st = db.stat()
    w()
    w("- %s  (%.1f MB, mtime %s)" % (db.relative_to(HOME),
        st.st_size / 1e6, fmt_time(st.st_mtime)))
    for sfx in ("-journal", "-wal", "-shm"):
        if Path(str(db) + sfx).exists():
            w("  * SIDECAR: %s%s  -> possible hot journal / live writer" % (db.name, sfx))
    try:
        con = sqlite3.connect("%s?mode=ro" % db.resolve().as_uri(),
                              uri=True, timeout=2)
        cur = con.cursor()
        rows = cur.execute("SELECT type, name, sql FROM sqlite_master "
                           "WHERE type IN ('table','view') ORDER BY name").fetchall()
        names = ["%s:%s" % (t, n) for t, n, _ in rows]
        w("  * objects (%d): %s" % (len(rows),
            ", ".join(names[:18]) + (" ..." if len(names) > 18 else "")))
        fts = [n for t, n, s in rows if s and ("fts5" in s.lower() or "fts4" in s.lower())]
        if fts:
            w("  * FTS virtual tables: %s" % ", ".join(fts))
        if st.st_size < 2 * 1024**3:
            counts = []
            for t, n, _ in rows:
                if t != "table" or SHADOW.search(n):
                    continue
                try:
                    c = cur.execute('SELECT COUNT(*) FROM "%s"'
                        % n.replace('"', '""')).fetchone()[0]
                    counts.append("%s=%d" % (n, c))
                except Exception as e:
                    counts.append("%s=ERR(%s)" % (n, type(e).__name__))
            if counts:
                w("  * row counts: %s" % "; ".join(counts[:18]))
        con.close()
    except sqlite3.OperationalError as e:
        msg = str(e)
        if "no such module" in msg:
            w("  * OPEN FAILED: %s (interpreter lacks module; try sqlite3 CLI)" % msg)
        else:
            w("  * OPEN FAILED (ro): %s -> locked by live writer or hot journal" % msg)
    except Exception as e:
        w("  * OPEN FAILED: %s" % e)

# --- 15. newton chain ledger ---------------------------------------
sec("15. NEWTON CHAIN LEDGER")
uniq = list(dict.fromkeys(str(p) for p in
        find_paths("newton_chain.jsonl", HOME, 4)
        + find_paths("newton_chain*.jsonl", OR, 6)))
chains = [Path(u) for u in uniq]
if not chains:
    w("No newton_chain.jsonl found (searched ~ depth 4, ~/openroot depth 6).")
for ch in chains[:3]:
    st = ch.stat()
    w()
    w("- %s  (%.1f MB, mtime %s)" % (ch.relative_to(HOME),
        st.st_size / 1e6, fmt_time(st.st_mtime)))
    total = valid = 0
    bad, keys, ts_vals = [], set(), []
    first = last = None
    with open(ch, "r", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            if first is None:
                first = line
            last = line
            try:
                obj = json.loads(line)
                valid += 1
                if isinstance(obj, dict):
                    keys.update(obj.keys())
                    for k, v in obj.items():
                        if any(s in k.lower() for s in ("time", "ts", "date")) \
                           and isinstance(v, (str, int, float)):
                            ts_vals.append(v)
            except Exception:
                if len(bad) < 5:
                    bad.append((i, line[:100]))
    w("  * lines=%d  valid_json=%d  malformed=%d" % (total, valid, total - valid))
    for i, s in bad:
        w("    malformed line %d: %s" % (i, s))
    w("  * key union (%d): %s" % (len(keys), ", ".join(sorted(keys)[:25])))
    if ts_vals:
        w("  * timestamps: first-seen=%s  last-seen=%s" % (ts_vals[0], ts_vals[-1]))
    unit_keys = [k for k in keys if any(s in k.lower()
        for s in ("unit", "joule", "watt", "kwh", "energy"))]
    if unit_keys:
        w("  * unit/energy-bearing keys present: %s  (grant-grade telemetry)" % ", ".join(unit_keys))
    else:
        w("  * NOTE: no explicit unit/energy keys in key union — schema may lack units.")
    if first:
        w("  * first entry (trunc): %s" % first[:240])
    if last and last != first:
        w("  * last entry (trunc): %s" % last[:240])

# --- 16. ACRE / PoPW record ----------------------------------------
sec("16. ACRE-0001 / PoPW RECORD")
acres = list(dict.fromkeys(str(p) for p in
        find_paths("*ACRE*", HOME, 5) + find_paths("*ACRE*", OR, 6)))
if not acres:
    w("No *ACRE* files found.")
for a in acres[:8]:
    p = Path(a)
    st = p.stat()
    w("- %s (%d bytes, mtime %s)" % (a, st.st_size, fmt_time(st.st_mtime)))
    if st.st_size < 200000:
        try:
            w("  head: %s" % p.read_text(errors="replace")[:400].replace("\n", " "))
        except Exception as e:
            w("  unreadable: %s" % e)

# --- 17. large files & duplicates ----------------------------------
sec("17. LARGE FILES & DUPLICATE CANDIDATES (>= 20 MB)")
PRUNE = {".cache", ".ollama", ".npm", "snap", ".local", ".var", ".android",
         "node_modules", ".next", "venv", ".git", "__pycache__", ".w3m"}
big = []
for root, dirs, files in os.walk(HOME):
    dirs[:] = [d for d in dirs if d not in PRUNE and not d.startswith(".syncthing.")]
    for f in files:
        p = os.path.join(root, f)
        try:
            st = os.stat(p)
        except OSError:
            continue
        if st.st_size >= 20 * 1e6:
            big.append((st.st_size, p))
big.sort(reverse=True)
w("Skipped reinstallable caches (.cache/.ollama/.npm/snap/.local/node_modules/venv/.git).")
w("Top 40 largest files:")
for sz, p in big[:40]:
    w("  %8.1f MB  %s" % (sz / 1e6, p.replace(str(HOME), "~")))
by_size = defaultdict(list)
for sz, p in big:
    by_size[sz].append(p)
dups = sorted(((sz, ps) for sz, ps in by_size.items() if len(ps) > 1),
              reverse=True)
w()
w("Same-size duplicate groups (verify before deleting anything):")
for sz, ps in dups[:15]:
    w("  %8.1f MB x%d:" % (sz / 1e6, len(ps)))
    for p in ps[:6]:
        w("      %s" % p.replace(str(HOME), "~"))

# --- 18. shell-escape artifact filenames ---------------------------
sec("18. SHELL-ESCAPE ARTIFACT FILENAMES (junk from unquoted heredocs)")
junk_re = re.compile(r"[{}()]|:22000:|^\s|\s+$")
junk = []
for entry in HOME.iterdir():
    if junk_re.search(entry.name):
        junk.append(entry.name)
    if entry.is_dir() and not entry.is_symlink():
        try:
            for e2 in entry.iterdir():
                if junk_re.search(e2.name):
                    junk.append(str(e2.relative_to(HOME)))
        except PermissionError:
            pass
junk.sort()
w("Found %d candidates (first 60). Some may be legit files; nothing is deleted:" % len(junk))
for j in junk[:60]:
    w("  %r" % j)

# --- 19. backup-file churn -----------------------------------------
sec("19. BACKUP-FILE CHURN")
bakdir = HOME / "openroot" / "bin"
if bakdir.is_dir():
    baks = [p.name for p in bakdir.iterdir()
            if ".bak" in p.name or "backup" in p.name.lower()]
    w("%d backup files in ~/openroot/bin (iterative-repair history):" % len(baks))
    for b in baks[:15]:
        w("  %s" % b)
    w("Recommendation: move .bak history into git history instead of sibling files.")

# --- 20. active bot state -------------------------------------------
sec("20. ACTIVE BOT STATE SNAPSHOT")
cand = OR / "data_bot_state.json"
if cand.exists():
    w("- data_bot_state.json (mtime %s):" % fmt_time(cand.stat().st_mtime))
    try:
        w("  " + json.dumps(json.loads(cand.read_text()), indent=2)[:600])
    except Exception as e:
        w("  unreadable: %s" % e)
tap = HOME / ".openroot_tap.tsv"
if tap.exists():
    w()
    w("- ~/.openroot_tap.tsv (mtime %s), first 5 lines:" % fmt_time(tap.stat().st_mtime))
    with open(tap, errors="replace") as fh:
        for _ in range(5):
            line = fh.readline()
            if not line:
                break
            w("  " + line.rstrip()[:160])

sys.stdout.write("\n".join(L) + "\n")
