#!/usr/bin/env bash
# ============================================================
#  OPENROOT GENERALIZED POD BUILDER v1
#  Same cell discipline as podbench v3 knowledge pod:
#  sha256 + blake3(or blake2b) + base36 + bytes + mtime + FTS5
#  Usage: bash build_pod.sh <output.db> <dir-or-file> [dir-or-file...]
#  Example:
#    bash build_pod.sh bench/state/pod_knowledge_fts5.db \
#      docs/survey/OPENROOT_PROJECT_SURVEY_20261105.md bench/PODBENCH_100_SPEC_v1.md \
#      bench/bin bench/questions
#    bash build_pod.sh ~/pods/curriculum.db ~/pod_sources/math ~/pod_sources/physics
# ============================================================
set -u
OUT="${1:?usage: build_pod.sh <out.db> <source>...}"; shift
command -v python3 >/dev/null || { echo "need python3"; exit 1; }
for s in "$@"; do [ -e "$s" ] || { echo "MISSING SOURCE: $s"; exit 1; }; done

python3 - "$OUT" "$@" <<'PYEOF'
import sqlite3, sys, os, hashlib, datetime
try:
    import blake3 as _b3; HAVE_B3 = True
except ImportError:
    HAVE_B3 = False
def blake_of(d: bytes):
    if HAVE_B3: return _b3.blake3(d).hexdigest(), "blake3"
    return hashlib.blake2b(d, digest_size=32).hexdigest(), "blake2b-fallback"
def b36(n: int) -> str:
    a = "0123456789abcdefghijklmnopqrstuvwxyz"; s = ""
    while n: s = a[n % 36] + s; n //= 36
    return s or "0"
TS = lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SCHEMA = """
CREATE TABLE IF NOT EXISTS cells (
  cid INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT, chunk_ix INTEGER, sha256 TEXT, blake_hex TEXT, blake_algo TEXT,
  base36 TEXT, bytes INTEGER, mtime REAL, ingested_at TEXT, content TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS cell_words USING fts5(content, source);
CREATE TABLE IF NOT EXISTS pod_meta (key TEXT, value TEXT);
"""
TEXT_EXT = {".md",".txt",".py",".sh",".json",".jsonl",".tsv",".csv",".tex",".yaml",".yml",".conf",".log"}
SKIP_DIR = {".git","node_modules","__pycache__",".venv"}

def collect(sources):
    files = []
    for s in sources:
        if os.path.isfile(s): files.append(s)
        else:
            for root, dirs, fnames in os.walk(s):
                dirs[:] = [d for d in dirs if d not in SKIP_DIR]
                files += [os.path.join(root, f) for f in fnames]
    return sorted(files)

def ingest(con, path):
    data = open(path, "rb").read()
    # text gate: skip likely-binary payloads honestly
    if os.path.splitext(path)[1].lower() not in TEXT_EXT:
        try: data.decode("utf-8")
        except UnicodeDecodeError:
            return ("SKIP_BINARY", path)
    text = data.decode("utf-8", errors="replace")
    sha = hashlib.sha256(data).hexdigest()
    blake, algo = blake_of(data)
    mt = os.path.getmtime(path)
    lines, chunk, ix, n = text.split("\n"), [], 0, 0
    def flush(ix, chunk):
        body = "\n".join(chunk).strip()
        if not body: return 0
        b = body.encode()
        h = hashlib.sha256(b).hexdigest()
        con.execute("INSERT INTO cells(source,chunk_ix,sha256,blake_hex,blake_algo,"
                    "base36,bytes,mtime,ingested_at,content) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (os.path.relpath(path), ix, h, blake_of(b)[0], blake_of(b)[1],
                     b36(int(h,16)), len(b), mt, TS(), body))
        con.execute("INSERT INTO cell_words(content,source) VALUES (?,?)", (body, os.path.relpath(path)))
        return 1
    for ln in lines:
        chunk.append(ln)
        if sum(len(x) for x in chunk) >= 400:
            n += flush(ix, chunk); ix += 1; chunk = []
    if chunk: n += flush(ix, chunk)
    return ("OK", n)

out, sources = sys.argv[1], sys.argv[2:]
fresh = not os.path.exists(out)
con = sqlite3.connect(out); con.executescript(SCHEMA)
files = collect(sources)
ok = skipped = cells = 0
for f in files:
    r, n = ingest(con, f)
    if r == "OK": ok += 1; cells += n
    else: skipped += 1
con.execute("INSERT INTO pod_meta VALUES ('built_at',?)", (TS(),))
con.execute("INSERT INTO pod_meta VALUES ('blake_algo',?)", ("blake3" if HAVE_B3 else "blake2b-fallback",))
con.execute("INSERT INTO pod_meta VALUES ('sources',?)", (";".join(sources),))
con.commit(); con.close()
print(f"POD_BUILT db={out} files_ok={ok} files_skipped_binary={skipped} cells={cells} "
      f"fresh={fresh} blake={'blake3' if HAVE_B3 else 'blake2b-fallback'}")
PYEOF
[ -f "$OUT" ] && sha256sum "$OUT"

