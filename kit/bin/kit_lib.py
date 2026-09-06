#!/usr/bin/env python3
"""Shared paths and sqlite helpers. stdlib only."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

A15_HOME = Path("/data/data/com.termux/files/home")
A15_CODE = A15_HOME / "code" / "openroot"
A15_MESH = Path("/storage/emulated/0/openroot")
SSH_HOME = Path("/home/jesse")
SSH_ROOT = SSH_HOME / "openroot"
SSH_MODELS = SSH_HOME / "models"


def detect_pane() -> str:
    cwd = str(Path.cwd())
    host = os.uname().nodename if hasattr(os, "uname") else ""
    if cwd.startswith("/home/jesse") or "optiplex" in host.lower():
        return "SSH"
    if cwd.startswith("/data/data/com.termux") or cwd.startswith("/storage/emulated"):
        return "A15"
    if (A15_HOME / "code").exists() or str(Path.home()).startswith("/data/data/com.termux"):
        return "A15"
    if Path("/home/jesse").exists() and Path("/home/jesse").is_dir():
        try:
            if os.access("/home/jesse", os.W_OK):
                return "SSH"
        except Exception:
            pass
    return "UNKNOWN"


def kit_root() -> Path:
    pane = detect_pane()
    if pane == "SSH":
        return SSH_ROOT / "kit"
    if pane == "A15":
        return A15_CODE / "kit"
    here = Path(__file__).resolve().parent.parent
    return here / "var"


def db_path() -> Path:
    root = kit_root()
    root.mkdir(parents=True, exist_ok=True)
    return root / "openroot_kit.sqlite"


def connect(schema_sql: str | None = None) -> sqlite3.Connection:
    path = db_path()
    con = sqlite3.connect(str(path))
    con.execute("PRAGMA journal_mode=DELETE")
    con.row_factory = sqlite3.Row
    if schema_sql:
        con.executescript(schema_sql)
        con.commit()
    return con
