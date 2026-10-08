#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""tidbit_registry_v1 - sha256-registered, license-gated tidbit intake.

A tidbit = one extracted functional unit from an upstream clone (file,
snippet copy, or adapted function) with recorded provenance. Reassembly
(drawing tidbits together into something stronger than its parts) consults
this registry; composition candidates are only valid when every constituent
passes the license gate.

License gate:
  ok       MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, GPL-3.0-only, LGPL-3.0-only
  blocked  AGPL-3.0-only, CC-BY-NC-4.0, Unlicense, Proprietary
  unknown  anything else -> [held], human verifies SPDX ID and whitelists it

Commands:
  register --path PATH --repo REPO [--commit SHA] --license SPDX_ID \
           [--function DESC] [--test CMD]
  list [--repo FILTER]
  stats
"""
import argparse
import hashlib
import json
import sqlite3
import time

DB = "/home/jesse/openroot/data/tidbit_registry.db"
OK_LICENSES = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0",
               "GPL-3.0-only", "LGPL-3.0-only"}
BLOCKED_LICENSES = {"AGPL-3.0-only", "CC-BY-NC-4.0", "Unlicense", "Proprietary"}

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def connect():
    c = sqlite3.connect(DB)
    c.execute(
        "CREATE TABLE IF NOT EXISTS tidbits("
        "sha256 TEXT PRIMARY KEY, "
        "origin_repo TEXT NOT NULL, "
        "origin_commit TEXT, "
        "license TEXT NOT NULL, "
        "function_desc TEXT, "
        "path TEXT NOT NULL, "
        "test_cmd TEXT, "
        "reuses INTEGER DEFAULT 0, "
        "registered TEXT)"
    )
    return c

def cmd_register(a):
    if a.license in BLOCKED_LICENSES:
        print(json.dumps({"status": "[held]", "reason": "license-blocked",
                          "license": a.license,
                          "detail": "poisons outbound GPL-3.0 — do not reassemble into openroot"}))
        return
    if a.license not in OK_LICENSES:
        print(json.dumps({"status": "[held]", "reason": "license-unknown",
                          "license": a.license,
                          "hint": "verify the SPDX ID at the source repo; whitelist only if GPL-3.0-compatible"}))
        return
    s = sha256_file(a.path)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    c = connect()
    existing = c.execute("SELECT origin_repo, path FROM tidbits WHERE sha256 = ?", (s,)).fetchone()
    if existing:
        c.execute("UPDATE tidbits SET reuses = reuses + 1 WHERE sha256 = ?", (s,))
        c.commit()
        c.close()
        print(json.dumps({"status": "[banked]", "sha256": s,
                          "event": "reuse-incremented",
                          "existing_origin": existing[0], "existing_path": existing[1]}))
        return
    c.execute(
        "INSERT INTO tidbits(sha256, origin_repo, origin_commit, license, "
        "function_desc, path, test_cmd, reuses, registered) "
        "VALUES(?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (s, a.repo, a.commit, a.license, a.function, a.path, a.test, now),
    )
    c.commit()
    c.close()
    print(json.dumps({"status": "[banked]", "sha256": s,
                      "origin": a.repo, "license": a.license}))

def cmd_list(a):
    c = connect()
    if a.repo:
        rows = c.execute(
            "SELECT sha256, origin_repo, origin_commit, license, function_desc, path, reuses "
            "FROM tidbits WHERE origin_repo LIKE ?", (f"%{a.repo}%",)).fetchall()
    else:
        rows = c.execute(
            "SELECT sha256, origin_repo, origin_commit, license, function_desc, path, reuses "
            "FROM tidbits").fetchall()
    c.close()
    print(json.dumps(
        [{"sha256": r[0][:12] + "…", "origin": r[1], "commit": r[2],
          "license": r[3], "function": r[4], "path": r[5], "reuses": r[6]}
         for r in rows], indent=2))

def cmd_stats(_):
    c = connect()
    n = c.execute("SELECT COUNT(*) FROM tidbits").fetchone()[0]
    reuse_total = c.execute("SELECT COALESCE(SUM(reuses), 0) FROM tidbits").fetchone()[0]
    by_repo = c.execute(
        "SELECT origin_repo, COUNT(*) FROM tidbits GROUP BY origin_repo ORDER BY COUNT(*) DESC"
    ).fetchall()
    c.close()
    print(json.dumps({"entries": n, "reuse_total": reuse_total,
                      "by_repo": {r[0]: r[1] for r in by_repo}, "db": DB}))

def main():
    p = argparse.ArgumentParser(prog="tidbit_registry_v1")
    sp = p.add_subparsers(dest="cmd", required=True)

    r = sp.add_parser("register", help="register a tidbit (license-gated)")
    r.add_argument("--path", required=True, help="local path of the tidbit file")
    r.add_argument("--repo", required=True, help="origin repo (owner/name)")
    r.add_argument("--commit", default="unknown", help="origin commit sha")
    r.add_argument("--license", required=True, help="SPDX ID of origin repo license")
    r.add_argument("--function", default="", help="what this tidbit does")
    r.add_argument("--test", default="", help="command that verifies it works")

    l = sp.add_parser("list", help="list registered tidbits")
    l.add_argument("--repo", default=None, help="filter by origin repo substring")

    st = sp.add_parser("stats", help="registry totals")

    r.set_defaults(func=cmd_register)
    l.set_defaults(func=cmd_list)
    st.set_defaults(func=cmd_stats)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
