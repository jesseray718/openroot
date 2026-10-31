# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
import ast
import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
DB = HOME / "pods/pod_interactions/pod.db"
SOURCE_DB = HOME / "pods/pod_openroot_live_v1/pod.db"
TEST_ID = "3aabe240753b4b4fa49c5b282d65b92c"
ARTIFACT = "27fb8b29e0d83a122239150ac5e37bf0863f770acb93024713657c05f2a534bc"

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_only(path):
    return sqlite3.connect(
        path.resolve().as_uri() + "?mode=ro", uri=True, timeout=3
    )

def main():
    started = __import__("time").monotonic()

    db = read_only(DB)
    try:
        row = db.execute("""
            SELECT question,dossier_json FROM single_gate_tests_v1
            WHERE test_id=?
        """, (TEST_ID,)).fetchone()
    finally:
        db.close()
    if not row:
        raise SystemExit("HELD: original test not found")
    question, original_json = row

    source_db = read_only(SOURCE_DB)
    try:
        row = source_db.execute(
            "SELECT content FROM source_bytes WHERE sha256=?",
            (ARTIFACT,),
        ).fetchone()
    finally:
        source_db.close()
    if not row or hashlib.sha256(row[0]).hexdigest() != ARTIFACT:
        raise SystemExit("HELD: original source missing or hash mismatch")

    raw = row[0]
    source = raw.decode("utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    spans = {}
    reasons = {}

    def select(node, reason):
        start = node.lineno
        decorators = getattr(node, "decorator_list", [])
        if decorators:
            start = min(start, *(d.lineno for d in decorators))
        end = node.end_lineno
        key = (start, end)
        spans[key] = node
        reasons.setdefault(key, set()).add(reason)

    def calls_named(node, name):
        return any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == name
            for child in ast.walk(node)
        )

    tasks = sorted(set(re.findall(r"\btask\s*(\d+)\b", question.lower())))
    if not tasks:
        raise SystemExit("HELD: this compiler requires named task numbers")

    matched_tasks = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        receipt_tasks = set()
        for child in ast.walk(node):
            if not (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == "receipt"
                and child.args
                and isinstance(child.args[0], ast.Constant)
                and isinstance(child.args[0].value, str)
            ):
                continue
            match = re.match(r"task(\d+)\.", child.args[0].value)
            if match:
                receipt_tasks.add(match.group(1))
        for task in tasks:
            if task in receipt_tasks:
                select(node, f"enclosing top-level statement for task{task} receipt")
                matched_tasks.add(task)

    if matched_tasks != set(tasks):
        raise SystemExit(
            f"HELD: missing task receipt statements: {set(tasks)-matched_tasks}"
        )

    definitions = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    pending = list(spans.values())
    expanded = set()
    while pending:
        node = pending.pop()
        for name, definition in definitions.items():
            if name not in expanded and calls_named(node, name):
                expanded.add(name)
                select(definition, "local function dependency: " + name)
                pending.append(definition)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = {
                child.id for target in node.targets
                for child in ast.walk(target)
                if isinstance(child, ast.Name)
            }
            if "CONFIRM" in targets:
                select(node, "definition of task6 conditional flag")

    if "receipt" not in expanded:
        raise SystemExit("HELD: receipt implementation not selected")

    records = []
    packet_parts = [
        "QUESTION\n" + question,
        "EVIDENCE E1: captured gh_window_opener_v1.py",
        "Selected original-source spans follow. Gaps are omitted; "
        "absence from this packet does not prove absence from the file. "
        "Some runtime globals are not included. Do not execute this packet.",
    ]

    for start, end in sorted(spans):
        a, b = offsets[start - 1], offsets[end]
        text = source[a:b]
        if text != "".join(lines[start - 1:end]):
            raise RuntimeError("source span verification failed")
        records.append({
            "source_lines": [start, end],
            "char_start": a,
            "char_end": b,
            "sha256": sha(text),
            "selection_reasons": sorted(reasons[(start, end)]),
        })
        packet_parts.append(f"[E1 lines {start}-{end}]\n{text.rstrip()}")

    packet = "\n\n".join(packet_parts)
    if len(packet) >= len(original_json):
        raise SystemExit(
            f"HELD: no size improvement: "
            f"{len(packet)} >= {len(original_json)} characters"
        )

    compile_id = uuid.uuid4().hex
    folder = HOME / "openroot/data/compiled_dossiers" / compile_id
    folder.mkdir(parents=True)
    (folder / "original_dossier.json").write_text(original_json)
    (folder / "captured_source.py").write_bytes(raw)
    (folder / "model_packet.txt").write_text(packet)

    manifest = {
        "kind": "targeted_gate_dossier_compilation_v2",
        "compile_id": compile_id,
        "test_id": TEST_ID,
        "question": question,
        "compiler_scope": "task-receipt control-flow questions only",
        "source_db": str(SOURCE_DB),
        "artifact_sha256": ARTIFACT,
        "input_dossier_sha256": sha(original_json),
        "output_sha256": sha(packet),
        "input_chars": len(original_json),
        "output_chars": len(packet),
        "character_reduction_percent": round(
            100 * (1 - len(packet) / len(original_json)), 2
        ),
        "character_count_is_not_token_count": True,
        "selected_spans": records,
        "complete_source_archived": True,
        "full_control_flow_analysis_performed": False,
        "span_integrity_verified": True,
        "answer_correctness_verified": False,
        "model_called": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": __import__("time").monotonic() - started,
        "archive_directory": str(folder),
    }
    (folder / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )

    con = sqlite3.connect(DB, timeout=10)
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS compiled_gate_dossiers_v2(
                compile_id TEXT PRIMARY KEY,
                test_id TEXT NOT NULL,
                artifact_sha256 TEXT NOT NULL,
                model_packet TEXT NOT NULL,
                manifest_json TEXT NOT NULL
            )
        """)
        con.execute(
            "INSERT INTO compiled_gate_dossiers_v2 VALUES(?,?,?,?,?)",
            (compile_id, TEST_ID, ARTIFACT, packet, encode(manifest)),
        )
        receipt = encode(manifest)
        digest = sha(receipt)
        con.execute("""
            INSERT OR IGNORE INTO ledger(
                sha256,path,ingested_at,origin_pod
            ) VALUES(?,?,?,?)
        """, (
            digest, "compilation://" + compile_id,
            manifest["created_utc"], "pod_interactions",
        ))
        con.execute("""
            INSERT INTO chunks(doc_sha256,ordinal,section_path,text)
            VALUES(?,0,?,?)
        """, (digest, "compilation/targeted-gate-v2", receipt))
        con.commit()
    finally:
        con.close()

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print("\n=== MODEL PACKET ===\n")
    print(packet)
    print("\nSMALLER PACKET VERIFIED; NO MODEL CALL")
    print("NO SOURCE FILES EXECUTED; NO ANSWERS AUTO-VERIFIED")

if __name__ == "__main__":
    main()
