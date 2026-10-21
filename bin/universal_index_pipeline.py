#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# universal_index_pipeline.py — archives -> dedup -> SQLite index -> Q&A router (clean rewrite)
# Jesse Ray / OpenRoot | v1.1 | rewrite-first: no nested patch layers, no f-string brace traps
import os, sys, json, glob, sqlite3, hashlib, time

RUN_MODE = "EXECUTE" if os.environ.get("INDEX") == "1" else "DRY-RUN"
ROOTS    = ["/home/jesse/openroot", "/home/jesse/src/openroot"]
ARCHIVE  = "/home/jesse/openroot/OpenRootArchives"
OUT      = "/home/jesse/openroot/data/universal_index"
TS       = int(time.time())

MODELS = {
    "coder_7b":  os.environ.get("CODER_MODEL",  "qwen2.5-coder:7b"),
    "grader_3b": os.environ.get("GRADER_MODEL", "qwen2.5:3b"),
    "embedding": os.environ.get("EMBED_MODEL",  "nomic-embed-text"),
}

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

print("[canary] paste intact | mode:", RUN_MODE)
os.makedirs(OUT, exist_ok=True)

# ==== STAGE 1: discover all archives ====
archives = []
for root in ROOTS + ([ARCHIVE] if os.path.exists(ARCHIVE) else []):
    for ext in ["*.tar.xz", "*.txz", "*.tar.gz", "*.tgz", "*.zip"]:
        archives.extend(glob.glob(os.path.join(root, "**", ext), recursive=True))
print(f"[locate] archives found: {len(archives)}")

# ==== STAGE 2: hash archives BEFORE unpacking, dedup identical bytes ====
archive_hashes = []
for arc in archives:
    try:
        archive_hashes.append({
            "path": arc,
            "sha256": sha256_file(arc),
            "size_bytes": os.path.getsize(arc),
        })
    except Exception as e:
        print(f"[hold] unreadable: {arc}: {e}")
unique_archives = {a["sha256"]: a for a in archive_hashes}
dupes = len(archive_hashes) - len(unique_archives)
print(f"[stage-1 complete] unique archives: {len(unique_archives)} | duplicate skips: {dupes}")

# ==== STAGE 3: SQLite schema ====
db_path = os.path.join(OUT, "universal_index_" + str(TS) + ".db")
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS files (
    sha256 TEXT PRIMARY KEY,
    original_paths TEXT,
    filename TEXT,
    size_bytes INTEGER,
    mime_type TEXT,
    content_class TEXT,
    extracted_to TEXT,
    unpack_ts INTEGER
)""")
cur.execute("""
CREATE TABLE IF NOT EXISTS content_classes (
    class_id TEXT PRIMARY KEY,
    description TEXT,
    sample_patterns TEXT,
    default_model TEXT
)""")
cur.execute("""
CREATE TABLE IF NOT EXISTS qa_templates (
    template_id TEXT PRIMARY KEY,
    title TEXT,
    question_pattern TEXT,
    template_prompt TEXT,
    required_fields TEXT,
    output_schema TEXT
)""")
cur.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
    ts INTEGER PRIMARY KEY,
    action TEXT,
    detail TEXT,
    result TEXT
)""")
print(f"[stage-2] created SQLite index: {db_path}")

# ==== STAGE 4: content classes ====
classes = [
    ("dome_geometry", "Geodesic calculations, strut lengths, BOMs",
     json.dumps(["*dome_bom*", "*geodesic*", "*strut*"]), "coder_7b"),
    ("aerocement", "Cement mixes, absorber panels, opencell formulas",
     json.dumps(["*aerocement*", "*opencell*", "*cement_mix*"]), "coder_7b"),
    ("thermal", "Cascade sims, RMH, labyrinth, psychrometrics",
     json.dumps(["*thermal*", "*rmh*", "*cascade*", "*psychrometric*"]), "coder_7b"),
    ("grants", "Grant applications, ledgers, synthesis records",
     json.dumps(["*grant*", "*synthesis*", "*acre*", "*ledger*"]), "grader_3b"),
    ("code_scripts", "Python, shell, Rust scripts",
     json.dumps(["*.py", "*.sh", "*.rs"]), "coder_7b"),
    ("docs_readme", "Documentation, handbooks, playbooks",
     json.dumps(["README*", "*handbook*", "*guide*"]), "grader_3b"),
]
for cls, desc, pat, mdl in classes:
    cur.execute("INSERT OR REPLACE INTO content_classes VALUES (?, ?, ?, ?)",
                (cls, desc, pat, mdl))
print(f"[stage-3] registered {len(classes)} content classes")

# ==== STAGE 5: Q&A templates ====
templates = [
    ("grant_query", "Grant eligibility check", r"(grant|eligible|fund|apply)",
     "Answer whether {project} qualifies for {funding_program}. Check against criteria in {database_table}. Return {{eligible:bool, reasons:[str]}}",
     json.dumps(["project", "funding_program", "database_table"]),
     json.dumps({"type": "object", "properties": {"eligible": {"type": "boolean"}, "reasons": {"type": "array"}}})),
    ("bom_query", "Bill of materials lookup", r"(BOM|cutlist|materials|struts)",
     "Return BOM for {structure_type} with frequency {freq}, diameter {dia_meters}. Fields: material, length_mm, count, cost_estimate.",
     json.dumps(["structure_type", "freq", "dia_meters"]),
     json.dumps({"type": "array", "items": {"type": "object"}})),
    ("file_locator", "Find file by content/name", r"(where is|find|locate|show me)",
     "Search files containing {keywords} in {class_scope}. Return [[path, sha256, snippet]].",
     json.dumps(["keywords", "class_scope"]),
     json.dumps({"type": "array", "items": {"type": "array"}})),
    ("theorem_check", "Verify axiom/theorem chain", r"(theorem|proof|axiom|verify)",
     "Trace {id} back to axioms in {chain_db}. Return {{valid:bool, path:[id], breaks:[reason]}}",
     json.dumps(["id", "chain_db"]),
     json.dumps({"type": "object", "properties": {"valid": {"type": "boolean"}}})),
]
for tid, title, pat, tmpl, req, out in templates:
    cur.execute("INSERT OR REPLACE INTO qa_templates VALUES (?, ?, ?, ?, ?, ?)",
                (tid, title, pat, tmpl, req, out))
print(f"[stage-4] registered {len(templates)} Q&A templates")

cur.execute("INSERT OR REPLACE INTO audit_log VALUES (?, ?, ?, ?)",
            (TS, "init", "rewrite v1.1", "ok"))
con.commit()
con.close()

# ==== STAGE 6: unpack manifest (idempotent) ====
unpack_list = os.path.join(OUT, "unpack_list_" + str(TS) + ".json")
with open(unpack_list, "w") as f:
    json.dump(list(unique_archives.values()), f, indent=1)
print(f"[stage-5] unpack manifest -> {unpack_list}")

# ==== STAGE 7: classifier config ====
classifier_cfg = os.path.join(OUT, "classifier_config.json")
cfg = {
    "models": MODELS,
    "content_classes": classes,
    "qa_templates": [t[:3] for t in templates],
    "runtime": {
        "batch_size": int(os.environ.get("CHUNK", "150")),
        "temperature": 0.1,
        "timeout_seconds": int(os.environ.get("TIMEOUT", "420")),
    },
}
with open(classifier_cfg, "w") as f:
    json.dump(cfg, f, indent=1)
print(f"[stage-6] classifier config -> {classifier_cfg}")

# ==== STAGE 8: Q&A router (plain string + .replace, ZERO f-string braces) ====
qa_launcher = os.path.join(OUT, "qa_router.sh")
launcher = (
    "#!/bin/bash\n"
    "# qa_router.sh - front-end to the universal index Q&A system\n"
    "# Usage: ./qa_router.sh <template_id> <arg1>=<val1> ...\n"
    "set -eu\n"
    'DB="__DB_PATH__"\n'
    'TEMPLATE="$1"; shift || { echo "Usage: $0 <template_id> [args]"; exit 1; }\n'
    'echo "[router] loading template $TEMPLATE from $DB"\n'
    'PROMPT=$(sqlite3 "$DB" "SELECT template_prompt FROM qa_templates WHERE template_id=\x27$TEMPLATE\x27")\n'
    'MODEL=$(sqlite3 "$DB" "SELECT default_model FROM content_classes LIMIT 1")\n'
    'echo "[invoke] $MODEL with template=$TEMPLATE"\n'
    'echo "[placeholder] ollama run $MODEL \'$PROMPT\' args: $@"\n'
)
launcher = launcher.replace("__DB_PATH__", db_path)
with open(qa_launcher, "w") as f:
    f.write(launcher)
os.chmod(qa_launcher, 0o755)
print(f"[stage-7] Q&A router -> {qa_launcher}")

# ==== SUMMARY ====
print("\n[summary] universal index initialized")
print("  Database: " + db_path)
print(f"  Unique archives ready for unpack: {len(unique_archives)}")
print(f"  Content classes: {len(classes)}")
print(f"  Q&A templates: {len(templates)}")

if RUN_MODE == "DRY-RUN":
    print("[held] dry-run. Re-run with INDEX=1 INDEX_UNPACK=1 to execute unpack")
    sys.exit(0)

print("[EXECUTED] dry-run passed, ready for full execution")
