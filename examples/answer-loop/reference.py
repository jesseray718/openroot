"""Disposable answer-loop experiment. Not a production ledger or pod tool."""

import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path


class Held(Exception):
    """Input or state could not be verified."""


def digest(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def pairs(values):
    result = {}
    for key, value in values:
        if key in result:
            raise Held("duplicate JSON key")
        result[key] = value
    return result


def constant(value):
    raise Held("nonstandard JSON constant: " + value)


def chain_hash(record, recipe):
    field = "ph" if recipe.startswith("legacy-") else "hash"
    core = {k: v for k, v in record.items() if k != field}
    if recipe == "v1":
        return digest(canonical(core))
    if recipe == "legacy-sorted":
        data = json.dumps(core, sort_keys=True, ensure_ascii=True,
                          allow_nan=False).encode()
    elif recipe == "legacy-compact":
        data = canonical(core)
    else:
        raise Held("unknown hash recipe")
    return hashlib.blake2b(data, digest_size=32).hexdigest()


def read_chain(path, expected_tip=None):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise Held("chain missing or not a regular file")
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise Held("incomplete chain line")
    rows = []
    previous = None
    try:
        text = raw.decode("utf-8")
        for line in text.splitlines():
            if not line.strip():
                raise Held("blank chain line")
            row = json.loads(line, object_pairs_hook=pairs, parse_constant=constant)
            if not isinstance(row, dict):
                raise Held("non-object chain row")
            if row.get("version") == "answer-loop/1":
                recipes = ("v1",)
                field = "hash"
            elif "version" not in row:
                recipes = ("legacy-sorted", "legacy-compact")
                field = "ph"
            else:
                raise Held("unsupported chain version")
            if row.get("prev") != previous:
                raise Held("chain link mismatch")
            matched = [r for r in recipes if row.get(field) == chain_hash(row, r)]
            if not matched:
                raise Held("chain hash mismatch")
            previous = row[field]
            rows.append((row, matched[0]))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise Held("invalid chain: " + str(exc)) from exc
    if expected_tip is not None and previous != expected_tip:
        raise Held("trusted tip mismatch")
    return rows, raw


def words(text):
    return list(dict.fromkeys(re.findall(r"[a-z0-9]+", text.lower())))[:32]


def redact(text):
    # This illustrative policy is not a comprehensive secret detector.
    return re.sub(r"(?i)\b(api[_-]?key|token|password)\s*[:=]\s*\S+",
                  r"\1=[REDACTED]", text)


def pod_hash(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise Held("pod missing or not a regular file")
    for suffix in ("-wal", "-journal"):
        if Path(str(path) + suffix).exists():
            raise Held("pod has uncheckpointed or active journal state")
    return digest(path.read_bytes())


def open_pod(path):
    path = Path(path).resolve(strict=True)
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    required = {"cell": {"tid", "sha256", "bytes", "payload_ref"},
                "cell_fts": {"tid", "body"}}
    try:
        for table, columns in required.items():
            actual = {row[1] for row in con.execute("PRAGMA table_info(" + table + ")")}
            if not columns.issubset(actual):
                raise Held("pod schema mismatch: " + table)
        ddl = con.execute("SELECT sql FROM sqlite_master WHERE name='cell_fts'").fetchone()
        if not ddl or not re.search(r"\bUSING\s+fts5\s*\(", ddl[0], re.I):
            raise Held("cell_fts is not FTS5")
    except BaseException:
        con.close()
        raise
    return con


def body_for(con, tid):
    cell = con.execute("SELECT sha256, bytes FROM cell WHERE tid=?", (tid,)).fetchall()
    bodies = con.execute("SELECT DISTINCT body COLLATE BINARY FROM cell_fts WHERE tid=?",
                         (tid,)).fetchall()
    if len(cell) != 1 or len(bodies) != 1 or not isinstance(bodies[0][0], str):
        raise Held("missing or ambiguous evidence: " + str(tid))
    body = bodies[0][0]
    data = body.encode()
    if cell[0] != (digest(data), len(data)):
        raise Held("cell body does not match metadata: " + str(tid))
    return body


def retrieve(con, question, budget=1200, per_file=2, superseded=()):
    terms = words(question)
    if not terms or budget < 1 or per_file < 1:
        raise Held("question and positive budgets required")
    query = " OR ".join('"' + word + '"' for word in terms)
    rows = con.execute(
        "SELECT cell.tid, cell.payload_ref, bm25(cell_fts) "
        "FROM cell_fts JOIN cell ON cell.tid=cell_fts.tid "
        "WHERE cell_fts MATCH ? ORDER BY bm25(cell_fts), cell.tid LIMIT 100",
        (query,)).fetchall()
    candidates, seen = [], set()
    for tid, source, score in rows:
        if tid in superseded or tid in seen:
            continue
        seen.add(tid)
        body = body_for(con, tid)
        covered = set(re.findall(r"[a-z0-9]+", body.lower())) & set(terms)
        # Select a window around the earliest question term, not just the prefix.
        match = re.search("|".join(re.escape(t) for t in terms), body, re.I)
        start = max(0, match.start() - 80) if match else 0
        snippet = redact(body[start:start + 300])
        candidates.append((tid, source or tid, score, body, snippet, covered))
    selected, covered, counts, used = [], set(), {}, 0
    while candidates:
        candidates.sort(key=lambda c: (-len(c[5] - covered), c[2], c[0]))
        tid, source, score, body, snippet, hits = candidates.pop(0)
        if counts.get(source, 0) >= per_file or any(s["snippet"] == snippet for s in selected):
            continue
        remaining = budget - used
        if remaining <= 0:
            break
        snippet = snippet[:remaining]
        if not snippet:
            continue
        selected.append({"tid": tid, "body_sha256": digest(body.encode()), "snippet": snippet})
        used += len(snippet)
        covered.update(hits)
        counts[source] = counts.get(source, 0) + 1
    return selected


def prompt_for(question, route):
    return ("Answer using only the evidence. If it is insufficient, say so.\n"
            + "\n".join("[" + r["tid"] + "] " + r["snippet"] for r in route)
            + "\nQuestion: " + redact(question) + "\nAnswer:")


class StubModel:
    def __init__(self, answer="Synthetic answer"):
        self.answer = answer
        self.requests = 0

    def generate(self, prompt):
        self.requests += 1
        return self.answer


def corrections(path):
    rows, raw = read_chain(path)
    result = []
    for row, recipe in rows:
        if recipe != "v1" or row.get("kind") not in ("BLOCK", "SUPERSEDE"):
            raise Held("unsupported correction")
        target = row.get("target")
        if not isinstance(target, str) or not target:
            raise Held("invalid correction target")
        result.append(row)
    return result, raw


def validate_pathway(row):
    route = row.get("route")
    if (row.get("kind") != "pathway" or not isinstance(row.get("question"), str)
        or not isinstance(row.get("answer"), str)
        or not isinstance(route, list) or not route or not all(
            isinstance(item, dict) and isinstance(item.get("tid"), str)
            and isinstance(item.get("snippet"), str)
            and isinstance(item.get("body_sha256"), str) for item in route
        )):
        raise Held("invalid pathway record")
    if len({item["tid"] for item in route}) != len(route):
        raise Held("duplicate route cell")
    if (row.get("answer_sha256") != digest(row["answer"].encode())
        or row.get("prompt_sha256") != digest(prompt_for(row["question"], route).encode())):
        raise Held("saved answer or prompt mismatch")


def ask(pod, chain, correction_chain, question, model, expected_tip=None,
        check_drift=False):
    """Run only against isolated synthetic files; caller serializes all access."""
    if not isinstance(question, str) or not words(question):
        raise Held("nonempty question required")
    if not isinstance(model, StubModel):
        raise Held("only the synthetic stub model is supported")
    rows, raw = read_chain(chain, expected_tip)
    for row, recipe in rows:
        if recipe == "v1":
            validate_pathway(row)
    changes, corrections_raw = corrections(correction_chain)
    superseded = {c["target"] for c in changes if c["kind"] == "SUPERSEDE"}
    before = pod_hash(pod)
    con = open_pod(pod)
    try:
        con.execute("BEGIN")
        saved = next((r for r, recipe in reversed(rows)
                      if recipe == "v1" and r.get("kind") == "pathway"
                      and r.get("question") == question), None)
        invalidated = False
        if saved:
            route = saved["route"]
            invalidated = any(
                (c["kind"] == "BLOCK" and c["target"] == saved["hash"])
                or (c["kind"] == "SUPERSEDE"
                    and c["target"] in {item["tid"] for item in route})
                for c in changes)
            for item in route:
                try:
                    body = body_for(con, item["tid"])
                    if digest(body.encode()) != item["body_sha256"]:
                        invalidated = True
                except Held:
                    invalidated = True
            if not invalidated:
                drift = check_drift and retrieve(con, question, superseded=superseded) != route
                if (pod_hash(pod) != before or Path(chain).read_bytes() != raw
                    or Path(correction_chain).read_bytes() != corrections_raw):
                    raise Held("state changed during replay")
                return {"mode": "replay", "answer": saved["answer"],
                        "tip": rows[-1][0].get("hash", rows[-1][0].get("ph")),
                        "drift_warning": bool(drift)}
        route = retrieve(con, question, superseded=superseded)
        if not route:
            if (pod_hash(pod) != before or Path(chain).read_bytes() != raw
                or Path(correction_chain).read_bytes() != corrections_raw):
                raise Held("state changed during retrieval")
            return {"mode": "insufficient", "answer": "Insufficient local evidence."}
        prompt = prompt_for(question, route)
        started = time.monotonic()
        requests_before = model.requests
        answer = model.generate(prompt)
        elapsed = time.monotonic() - started
        if not isinstance(answer, str) or model.requests != requests_before + 1:
            raise Held("invalid stub response or request count")
        if (pod_hash(pod) != before or Path(chain).read_bytes() != raw
            or Path(correction_chain).read_bytes() != corrections_raw):
            raise Held("state changed during generation")
        row = {"version": "answer-loop/1", "kind": "pathway", "question": question,
               "route": route, "prompt_sha256": digest(prompt.encode()),
               "answer": answer, "answer_sha256": digest(answer.encode()),
               "model": "stub", "model_requests": model.requests - requests_before,
               "elapsed_seconds": elapsed, "tokens": None,
               "measured_joules": None, "estimated_joules": None,
               "prev": rows[-1][0].get("hash", rows[-1][0].get("ph")) if rows else None}
        row["hash"] = chain_hash(row, "v1")
        with Path(chain).open("ab") as stream:
            stream.write(canonical(row) + b"\n")
        return {"mode": "generated", "answer": answer, "tip": row["hash"],
                "invalidated": invalidated}
    finally:
        con.close()
