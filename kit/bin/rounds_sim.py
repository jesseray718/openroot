#!/usr/bin/env python3
"""Simulate 100 back-and-forth rounds on gh/termux/python/ssh/coder.
Writes predicted errors into sqlite. Does not talk to the network.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_lib  # noqa: E402

FAMILIES = [
    ("LANG", "paste Python at bash $", "from: too many arguments / import wants imagemagick", "wrap in python3 file.py or python3 -c", 5),
    ("HEREDOC", "split cat << EOF across messages", "EOF becomes a command, file missing", "one paste, quoted EOF, wait for $ before next cmd", 5),
    ("PLACE", "git add PATH copied literally", "pathspec did not match", "git add a real file from git status", 4),
    ("TYPO", "cd openrooot / t remote -v", "No such file / No command t", "openroot ; git remote -v", 3),
    ("PANE", "A15 path on jesse@optiplex3060", "No such file /sdcard on box", "label pane first; refuse cross paths", 5),
    ("CLONE", "gh repo clone while already inside clone", "second 73MB tree", "use existing code/openroot", 3),
    ("MESH", "treat Termux syncthing cli as daemon", "connection refused 42409", "Fork GUI + bus files", 4),
    ("RISH", "assume rish after reboot", "rish null in primer", "degrade to stdlib; start Shizuku by hand", 3),
    ("CANON", "new module while canon false", "empty path copied onto empty path", "seed canon.py print 0.0 first", 5),
    ("TOKEN", "paste ghp_ into chat or commit", "secret scan / account burn", "gh auth token never echoed; rotate scopes", 5),
    ("SSHKEY", "ssh jesse@192.168.1.193 without BatchMode key", "password prompt / hang", "use id_ed25519_optiplex and BatchMode=yes", 4),
    ("SSHIP", "use 192.168.1.x placeholder", "resolves to gateway 192.168.1.1", "live box IP 192.168.1.193 until ip -br addr says else", 5),
    ("TILDE", "paste ~ or escaped tilde", "literal directory named tilde", "absolute paths only", 5),
    ("CWD", "rm -rf while cwd is that dir", "ghost cwd, failed to make path absolute", "cd out first", 5),
    ("PYREPL", "forget to exit >>>", "next git command is syntax error", "exit() then dollar commands", 3),
    ("SQLITE", "copy db while writers open", "malformed disk image", "close python; copy sqlite files together", 3),
    ("CODER_PHONE", "try 7B GGUF on A15 3.5GB", "OOM / thermal throttle", "client only; model on OptiPlex", 5),
    ("CODER_PORT", "curl localhost:8080 from phone", "connection refused", "curl http://192.168.1.193:8080/v1/models", 4),
    ("CODER_MODEL", "point llama-server at missing GGUF", "failed to load model", "ls /home/jesse/models and pass exact file", 4),
    ("SYSTEMD", "pkill syncthing because unit failed", "mesh drop, ID confusion", "if 8384 listens and ID JW5PQXV leave it", 4),
    ("STFOLDER", "unique-ID wipe at 99 percent", "full resync heat", "mkdir .stfolder directory", 5),
    ("GITPUSH", "git push dump photos", "repo bloat", "mesh for binaries; git for claims", 3),
    ("BRANCH", "commit on detached HEAD after clone of tag", "push rejected", "git switch main", 2),
    ("CRLF", "edit on Windows then Termux", "scripts have CR", "strip CR in python", 2),
    ("PERM", "chmod 777 everything", "Syncthing fights, git noise", "files 644 dirs 755", 2),
]


def expand_100():
    out = []
    for i in range(1, 101):
        family, trigger, symptom, fix, sev = FAMILIES[(i - 1) % len(FAMILIES)]
        out.append(
            {
                "round": i,
                "family": family,
                "trigger": "R%03d %s" % (i, trigger),
                "symptom": symptom,
                "fix": fix,
                "severity": sev,
            }
        )
    return out


def main() -> int:
    con = kit_lib.connect()
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    con.execute("DELETE FROM error_pred")
    con.commit()
    rows = expand_100()
    payload = [
        (r["round"], r["family"], r["trigger"], r["symptom"], r["fix"], r["severity"])
        for r in rows
    ]
    con.executemany(
        "INSERT INTO error_pred(round,family,trigger,symptom,fix,severity) VALUES(?,?,?,?,?,?)",
        payload,
    )
    con.execute("INSERT OR REPLACE INTO meta(k,v,t) VALUES(?,?,?)", ("rounds_sim", "100", now))
    con.commit()
    fams = con.execute(
        "SELECT family, COUNT(*) c, AVG(severity) s FROM error_pred GROUP BY family ORDER BY c DESC"
    ).fetchall()
    top = con.execute(
        "SELECT family, trigger, fix FROM error_pred WHERE severity>=5 ORDER BY round LIMIT 8"
    ).fetchall()
    print(
        json.dumps(
            {
                "ok": True,
                "rows": len(rows),
                "db": str(kit_lib.db_path()),
                "families": [dict(x) for x in fams],
                "sev5_sample": [dict(x) for x in top],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
