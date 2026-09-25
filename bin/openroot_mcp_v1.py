#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
"""openroot_mcp_v1.py — local-sovereignty MCP surface over existing OpenRoot tooling."""
import sqlite3, subprocess
from fastmcp import FastMCP

mcp = FastMCP("openroot")
REPO = "/home/jesse/openroot"

@mcp.tool()
def fts_search(query: str, table: str = "theorem_fts") -> str:
    """Full-text search across local theorem/ledgere FTS5 indexes."""
    con = sqlite3.connect(f"{REPO}/data/theorem_compound.db")
    rows = con.execute(f"SELECT statement, rationale FROM {table} WHERE {table} MATCH ? LIMIT 10", (query,)).fetchall()
    return "\n".join(f"{s} :: {r[:120]}" for s, r in rows) or "no hits"

@mcp.tool()
def git_read(cmd: str) -> str:
    """Read-only git ops (status/log/diff). Mutating commands are refused."""
    if any(w in cmd for w in ("push", "reset", "commit", "merge", "rebase", "delete")):
        return "[held] mutating git blocked at MCP boundary — use terminal push_guard"
    return subprocess.run(["bash", "-lc", f"cd {REPO} && git {cmd}"], capture_output=True, text=True, timeout=60).stdout

@mcp.tool()
def theorem_round(rounds: int = 3) -> str:
    """Run one compounding pass of the 7B-author/3B-grade theorem loop."""
    r = subprocess.run(["python3", f"{REPO}/bin/theorem_compounder_v1.py"],
                       capture_output=True, text=True, timeout=3600)
    return r.stdout[-2000:] or r.stderr[-500:]

if __name__ == "__main__":
    mcp.run()  # stdio transport, zero network
