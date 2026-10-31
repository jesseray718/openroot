# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
import copy
import fcntl
import hashlib
import json
import sqlite3
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
DB = HOME / "pods/pod_interactions/pod.db"
BASELINE = "3aabe240753b4b4fa49c5b282d65b92c"

def utc():
    return datetime.now(timezone.utc).isoformat()

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

lock = open(HOME / "pods/.dossier_ask.lock", "a")
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit("HELD: another question or model test is active")

con = sqlite3.connect(DB, timeout=10)
con.row_factory = sqlite3.Row

baseline = con.execute(
    "SELECT * FROM single_gate_tests_v1 WHERE test_id=?", (BASELINE,)
).fetchone()
compiled = con.execute("""
    SELECT * FROM compiled_gate_dossiers_v2
    WHERE test_id=? ORDER BY rowid DESC LIMIT 1
""", (BASELINE,)).fetchone()

if not baseline or not compiled:
    raise SystemExit("HELD: baseline or compiled packet missing")

manifest = json.loads(compiled["manifest_json"])
packet = compiled["model_packet"]
if sha(packet) != manifest["output_sha256"]:
    raise SystemExit("HELD: compiled packet hash mismatch")

request = copy.deepcopy(json.loads(baseline["request_json"]))
original_request = copy.deepcopy(request)
user_indices = [
    i for i, message in enumerate(request["messages"])
    if message["role"] == "user"
]
if len(user_indices) != 1:
    raise SystemExit("HELD: expected exactly one user message")

request["messages"][user_indices[0]]["content"] = packet

check = copy.deepcopy(request)
check["messages"][user_indices[0]]["content"] = (
    original_request["messages"][user_indices[0]]["content"]
)
if check != original_request:
    raise SystemExit("HELD: settings changed beyond evidence message")

test_id = uuid.uuid4().hex
con.execute("""
    INSERT INTO single_gate_tests_v1(
      test_id,question,artifact_sha256,dossier_json,request_json,
      status,started_utc,expected_answer
    ) VALUES(?,?,?,?,?,?,?,?)
""", (
    test_id, baseline["question"], baseline["artifact_sha256"],
    encode({
        "question": baseline["question"],
        "compile_id": compiled["compile_id"],
        "model_packet": packet,
    }),
    encode(request), "model_running", utc(), baseline["expected_answer"],
))
con.commit()

print("TEST_ID:", test_id, flush=True)
print("BASELINE:", BASELINE, flush=True)
print("COMPILE_ID:", compiled["compile_id"], flush=True)
print("MODEL:", request["model"], flush=True)
print("OPTIONS:", encode(request["options"]), flush=True)
print("ONLY REQUEST CHANGE: user evidence message", flush=True)
print("COLD/WARM CACHE CONDITIONS NOT CONTROLLED", flush=True)
print("ONE MODEL CALL", flush=True)

started = time.monotonic()
response, status, error = None, "failed", None
try:
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=encode(request).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=900) as reply:
        response = json.load(reply)
    if "error" in response:
        raise RuntimeError(response["error"])
    status = "completed_unverified"
except KeyboardInterrupt:
    status, error = "cancelled", "user interruption"
except Exception as exc:
    error = repr(exc)
finally:
    wall = time.monotonic() - started
    con.execute("""
        UPDATE single_gate_tests_v1
        SET response_json=?,status=?,error=?,finished_utc=?,wall_seconds=?
        WHERE test_id=?
    """, (
        encode(response) if response else None, status, error,
        utc(), wall, test_id,
    ))

    receipt = {
        "kind": "compiled_dossier_comparison",
        "test_id": test_id,
        "baseline_test_id": BASELINE,
        "compile_id": compiled["compile_id"],
        "request_sha256": sha(encode(request)),
        "status": status,
        "error": error,
        "wall_seconds": wall,
        "answer_verified": False,
        "cache_conditions_controlled": False,
        "created_utc": utc(),
    }
    receipt_text = encode(receipt)
    receipt_sha = sha(receipt_text)
    con.execute("""
        INSERT OR IGNORE INTO ledger(sha256,path,ingested_at,origin_pod)
        VALUES(?,?,?,?)
    """, (
        receipt_sha, "test://" + test_id,
        receipt["created_utc"], "pod_interactions",
    ))
    con.execute("""
        INSERT INTO chunks(doc_sha256,ordinal,section_path,text)
        VALUES(?,0,?,?)
    """, (receipt_sha, "test/compiled-gate-comparison", receipt_text))
    con.commit()
    con.close()

    print("\nSTATUS:", status, flush=True)
    print("ERROR:", error, flush=True)
    print("\n=== BASELINE / COMPILED ===", flush=True)

    old = json.loads(baseline["response_json"] or "{}")
    new = response or {}
    print("wall_seconds:",
          baseline["wall_seconds"], "/", round(wall, 3), flush=True)
    for key in ("prompt_eval_count", "eval_count", "done_reason"):
        print(key + ":", old.get(key), "/", new.get(key), flush=True)
    for key in ("load_duration", "prompt_eval_duration", "eval_duration"):
        print(
            key + "_seconds:",
            round((old.get(key) or 0) / 1e9, 3), "/",
            round((new.get(key) or 0) / 1e9, 3),
            flush=True,
        )

    print("\nMODEL ANSWER — UNVERIFIED:", flush=True)
    print(new.get("message", {}).get("content", "(no answer)"), flush=True)
    print("\nEXPECTED ANSWER:", flush=True)
    print(baseline["expected_answer"], flush=True)
    print("\nSAVED; NO AUTOMATIC PASS CLAIM", flush=True)
