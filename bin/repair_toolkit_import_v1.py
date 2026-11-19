#!/usr/bin/env python3
"""repair_toolkit_import_v1.py — repair the broken import line in
openroot_toolkit.py (the `import sqlite5 if ... else ...` line, which is
not valid Python).

Repairs exactly that one line, leaves everything else untouched, writes a
timestamped backup first, and is idempotent (safe to re-run).

Usage:
  python3 repair_toolkit_import_v1.py [path-to-openroot_toolkit.py]
"""
import datetime
import difflib
import os
import py_compile
import re
import sys

BROKEN_EXACT = (
    "import sqlite5 if 'sqlite5' in sys.modules else sqlite3 # Fallback handling"
)
BROKEN_REGEX = re.compile(r"^\s*import sqlite5 if .*sqlite3.*$", re.M)
FIXED = (
    "try:  # sqlite5 (optional/future) with stdlib fallback\n"
    "    import sqlite5 as sqlite3  # type: ignore\n"
    "except ImportError:\n"
    "    import sqlite3"
)


def main(path):
    if not os.path.isfile(path):
        print("TOOLKIT_ABSENT_OK %s" % path)
        return 0

    with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
        src = f.read()

    if BROKEN_EXACT not in src and not BROKEN_REGEX.search(src):
        # Nothing to repair; confirm the file compiles as-is.
        try:
            py_compile.compile(path, doraise=True)
            print("ALREADY_OK py_compile OK")
            return 0
        except Exception as e:
            print("ALREADY_OK_BUT_COMPILE_FAIL %r" % (e,))
            return 1

    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    bak = "%s.bak.%s" % (path, stamp)
    with open(bak, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(src)

    if BROKEN_EXACT in src:
        fixed = src.replace(BROKEN_EXACT, FIXED, 1)
    else:
        fixed = BROKEN_REGEX.sub(FIXED, src, count=1)

    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(fixed)

    try:
        py_compile.compile(path, doraise=True)
    except Exception as e:
        print("REPAIRED_BUT_STILL_FAILS %r backup=%s" % (e, bak))
        return 1

    print("REPAIR_OK backup=%s" % bak)
    diff_lines = list(difflib.unified_diff(
        src.splitlines(), fixed.splitlines(), lineterm="", n=1))
    for line in diff_lines[:40]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "openroot_toolkit.py"))
