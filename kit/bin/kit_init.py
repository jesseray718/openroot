#!/usr/bin/env python3
"""Initialize kit dirs + sqlite + load tidbits. Safe on A15, SSH, or sandbox."""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
sys.path.insert(0, str(HERE))
import kit_lib  # noqa: E402

SCHEMA = (KIT / "sql" / "schema.sql").read_text()
TIDBITS = json.loads((KIT / "data" / "tidbits.json").read_text())


def main() -> int:
    pane = kit_lib.detect_pane()
    root = kit_lib.kit_root()
    root.mkdir(parents=True, exist_ok=True)
    con = kit_lib.connect(SCHEMA)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    con.execute(
        "INSERT OR REPLACE INTO meta(k,v,t) VALUES(?,?,?)",
        ("pane", pane, now),
    )
    con.execute(
        "INSERT OR REPLACE INTO meta(k,v,t) VALUES(?,?,?)",
        ("kit_root", str(root), now),
    )
    n = 0
    for tb in TIDBITS["tidbits"]:
        con.execute(
            """INSERT OR REPLACE INTO tidbit(id,module,title,body,pane,eta_note,created)
               VALUES(?,?,?,?,?,?,?)""",
            (
                tb["id"],
                tb["module"],
                tb["title"],
                tb["body"],
                tb["pane"],
                tb.get("eta_note"),
                now,
            ),
        )
        n += 1
    con.execute(
        "INSERT INTO pane_event(t,pane,host,cwd,ok,note) VALUES(?,?,?,?,?,?)",
        (now, pane, None, str(Path.cwd()), 1, "kit_init"),
    )
    con.commit()
    print(
        json.dumps(
            {
                "ok": True,
                "pane": pane,
                "db": str(kit_lib.db_path()),
                "tidbits": n,
                "cwd": str(Path.cwd()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
