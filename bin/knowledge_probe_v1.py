#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
"""knowledge_probe_v1.py — cross-ledger keyword search + theorem proof cache.

Searches all sqlite dbs in data/ for concept clusters (synergetics, Newton
chain, agape coordination/cooperation, core atomic functions, 46656,
axioms/definitions/postulates/theorems), plus a bounded text-file sweep.
Maintains a proof cache (data/proof_cache.db) keyed by sha256 of the theorem
statement: prove once, never recompute. 7B drafts, 3B grades.
Idempotent: re-runs preserve cache, overwrite only the dated report.
v1.1 fix: no rowid dependence — explicit column lists, enumerate matches.
"""
import datetime, glob, hashlib, json, os, re, sqlite3, subprocess, urllib.request

ROOT = "/home/jesse/openroot"
DATA_DIR = os.path.join(ROOT, "data")
CACHE_DB = os.path.join(DATA_DIR, "proof_cache.db")
REPORT_PATH = os.path.join(ROOT, "analysis",
    "knowledge_probe_report_%s.md" % datetime.date.today().isoformat())
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_BUILDER = "qwen2.5-coder:7b"
MODEL_GRADER = "qwen2.5:3b"

CLUSTERS = {
    "synergetics": ["synerget", "fuller", "tensegrity", "vector equilibrium", "jitterbug"],
    "newton_chain": ["newton chain", "newton-chain", "newton"],
    "agape_coordination": ["agape", "coordination", "cooperation", "collaborat", "mesh node"],
    "core_atomic_functions": ["core atomic", "atomic function", "core_atom", "primitive op"],
    "taxonomy_46656": ["46656", "46,656", "6^6", "isotropic vector matrix", "vector matrix"],
    "axioms_theorems": ["axiom", "definition", "postulate", "theorem", "lemma"],
}

def q(ident):  # quote sqlite identifier
    """Return an escaped SQLite identifier enclosed in double quotes."""
    return '"' + ident.replace('"', '""') + '"'

def scan_dbs():
    """Return configured keyword-cluster matches from local SQLite ledgers."""
    hits = []
    for db in sorted(glob.glob(os.path.join(DATA_DIR, "*.db"))):
        if os.path.basename(db) == os.path.basename(CACHE_DB):
            continue  # v1.1: self-referential - theorem statements contain search terms
        con = None
        try:
            con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
            con.row_factory = sqlite3.Row
            tables = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
            for table in tables:
                try:
                    cols = [r[1] for r in
                            con.execute("PRAGMA table_info(%s)" % q(table))]
                except sqlite3.Error:
                    continue
                if not cols:
                    continue
                col_list = ", ".join(q(c) for c in cols)
                for cluster, terms in CLUSTERS.items():
                    for term in terms:
                        where = " OR ".join(
                            "CAST(%s AS TEXT) LIKE ?" % q(c) for c in cols)
                        sql = "SELECT %s FROM %s WHERE %s" % (
                            col_list, q(table), where)
                        params = ["%%%s%%" % term] * len(cols)
                        try:
                            rows = con.execute(sql, params).fetchall()
                        except sqlite3.Error:
                            continue  # odd schema / unreadable blob: skip
                        for n, row in enumerate(rows, start=1):
                            vals = {c: row[c] for c in cols
                                    if row[c] is not None}
                            snippet = " ".join(str(v) for v in
                                               vals.values())[:160]
                            hits.append(dict(
                                db=os.path.basename(db), table=table,
                                cluster=cluster, term=term,
                                rowid="match %d" % n,
                                snippet=snippet))
        except sqlite3.Error as exc:
            print("[held] skipping database %s: %s" % (db, exc))
        finally:
            if con is not None:
                con.close()
    return hits

def scan_files():
    """Bounded grep sweep of repo text (excludes .git, venv)."""
    pattern = "|".join(re.escape(t) for ts in CLUSTERS.values() for t in ts)
    cmd = ["grep", "-rilE", pattern, "--include=*.md", "--include=*.json",
           "--include=*.jsonl", "--include=*.py", "--include=*.sh",
           "--exclude-dir=.git", "--exclude-dir=venv",
           "--exclude-dir=node_modules", ROOT]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return [l for l in out.stdout.splitlines() if l.strip()]
    except Exception as e:
        print("[held] file sweep failed:", e)
        return []

def ollama(prompt, model, timeout=600):
    """Submit a prompt to a local Ollama model and return its response text."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False})
    req = urllib.request.Request(OLLAMA_URL, data=payload.encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["response"]

def ensure_cache():
    """Initialize the proof cache schema and return an open connection."""
    con = sqlite3.connect(CACHE_DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS proofs (
        theorem_id TEXT PRIMARY KEY, statement TEXT, status TEXT, proof TEXT,
        grader_verdict TEXT, model TEXT, sha256 TEXT, created_at TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_proofs_status ON proofs(status)")
    con.commit()
    return con

def prove(statement):
    """Return a cached or newly graded proof result for a statement.

    Cached successful and failed results are not recomputed. Failures while
    generating or grading a new proof produce an ``UNBANKED`` result.
    """
    tid = hashlib.sha256(statement.encode()).hexdigest()[:16]
    con = ensure_cache()
    row = con.execute(
        "SELECT * FROM proofs WHERE theorem_id=?", (tid,)).fetchone()
    if row and row["status"] == "PROVED":
        proof = row["proof"]
        print("[cache-hit] theorem %s already proved %s — no recompute"
              % (tid, row["created_at"]))
        con.close()
        return {"statement": statement, "status": "PROVED", "proof": proof}
    if row and row["status"] == "FAILED":
        print("[held] theorem %s previously graded FAIL — see cache" % tid)
        con.close()
        return {"statement": statement, "status": "FAILED"}
    try:
        draft = ollama(
            "Prove this statement rigorously and concisely. "
            "State premises, steps, conclusion.\nSTATEMENT: " + statement,
            MODEL_BUILDER)
        verdict = ollama(
            "Grade the following proof against this statement. "
            "Reply first line VERDICT: PASS or VERDICT: FAIL, "
            "second line FIX: none or a correction.\nSTATEMENT: %s\nPROOF: %s"
            % (statement, draft), MODEL_GRADER)
        first_line = verdict.splitlines()[0] if verdict.splitlines() else ""
        status = "PROVED" if first_line == "VERDICT: PASS" else "FAILED"
        con.execute("INSERT OR REPLACE INTO proofs VALUES (?,?,?,?,?,?,?,?)",
            (tid, statement, status, draft, verdict, MODEL_BUILDER,
             hashlib.sha256(draft.encode()).hexdigest(),
             datetime.datetime.now().isoformat(timespec="seconds")))
        con.commit()
        print("[%s] theorem %s graded %s" %
              ("banked" if status == "PROVED" else "held", tid, status))
        return {"statement": statement, "status": status, "proof": draft}
    except Exception as e:
        print("[held] ollama unreachable (%s) — theorem %s unbanked" % (e, tid))
        return {"statement": statement, "status": "UNBANKED"}
    finally:
        con.close()

def main():
    """Scan local knowledge sources, exercise the proof cache, and write a report."""
    print("[stage 1] scanning sqlite ledgers in %s" % DATA_DIR)
    db_hits = scan_dbs()
    print("[stage 2] sweeping repo text files (%d ledger hits so far)"
          % len(db_hits))
    file_hits = scan_files()
    print("[stage 3] proof cache: prove once, never recompute")
    demo = prove("Algebraic identity: (a+b)^2 = a^2 + 2ab + b^2 for all real a,b")
    cache_hit_demo = prove("Algebraic identity: (a+b)^2 = a^2 + 2ab + b^2 for all real a,b")

    lines = ["# Knowledge Probe Report — %s" % datetime.date.today().isoformat(), ""]
    by_cluster = {}
    for h in db_hits:
        by_cluster.setdefault(h["cluster"], []).append(h)
    lines.append("## Sqlite ledger hits (%d total across %d dbs)"
                 % (len(db_hits), len(glob.glob(os.path.join(DATA_DIR, "*.db")))))
    for cluster in CLUSTERS:
        ch = by_cluster.get(cluster, [])
        lines.append("\n### %s — %d hit(s)" % (cluster, len(ch)))
        if not ch:
            lines.append("- **zero hits** — concept not yet in ledgers "
                         "(signal: unbuilt/unnamed in this dataset)")
        for h in ch[:25]:
            lines.append("- `%s::%s` [%s=%s]: %s" %
                         (h["db"], h["table"], h["term"], h["rowid"],
                          h["snippet"].replace("\n", " ")[:140]))
        if len(ch) > 25:
            lines.append("- ... %d more truncated in ledger" % (len(ch) - 25))
    lines.append("\n## Repo text files matching clusters (%d files)" % len(file_hits))
    for f in file_hits[:60]:
        lines.append("- %s" % os.path.relpath(f, ROOT))
    lines.append("\n## Proof cache demo")
    lines.append("- first call: %s" % demo["status"])
    lines.append("- second call: %s (this is the never-recompute property)"
                 % cache_hit_demo["status"])
    lines.append("\n## Note")
    lines.append("Boot seed records axiom_engine at 53 axioms / 56 defs "
                 "(sha256 chain GREEN). If taxonomy_46656 shows zero hits, "
                 "the 6^6 (=46656, Fuller's synergetics magnitude class) "
                 "target taxonomy is **unbuilt** — a genuine gap, not a "
                 "search failure.")
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("[banked] %s (%d db hits, %d files, cache at %s)"
          % (REPORT_PATH, len(db_hits), len(file_hits), CACHE_DB))

if __name__ == "__main__":
    main()
# [exit=0]
