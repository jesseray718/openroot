#!/usr/bin/env python3
"""Modular tidbit CLI. list | get ID | module NAME | search Q"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_lib  # noqa: E402


def main(argv: list[str]) -> int:
    con = kit_lib.connect()
    if len(argv) < 2 or argv[1] in ("list",):
        rows = con.execute("SELECT id,module,title,pane FROM tidbit ORDER BY id").fetchall()
        for r in rows:
            print(f"{r['id']}  {r['module']:8}  {r['pane']:5}  {r['title']}")
        return 0
    cmd = argv[1]
    if cmd == "get" and len(argv) >= 3:
        r = con.execute("SELECT * FROM tidbit WHERE id=?", (argv[2].upper(),)).fetchone()
        if not r:
            print("missing")
            return 2
        print(json.dumps(dict(r), indent=2))
        return 0
    if cmd == "module" and len(argv) >= 3:
        rows = con.execute(
            "SELECT id,title,body FROM tidbit WHERE module=?", (argv[2],)
        ).fetchall()
        for r in rows:
            print(f"## {r['id']} {r['title']}\n{r['body']}\n")
        return 0 if rows else 2
    if cmd == "search" and len(argv) >= 3:
        q = "%" + argv[2] + "%"
        rows = con.execute(
            "SELECT id,title FROM tidbit WHERE title LIKE ? OR body LIKE ?",
            (q, q),
        ).fetchall()
        for r in rows:
            print(f"{r['id']}  {r['title']}")
        return 0
    print("usage: tidbit.py [list|get ID|module NAME|search Q]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
