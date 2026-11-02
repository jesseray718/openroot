# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""
# SPDX-License-Identifier: GPL-3.0
synergetic_compounding_v2.py — fractal self-similar pathway amplifier
=====================================================================

WHAT IT DOES
    Streams every SQLite manifest database under <root>/data, collapses each
    file record into a normalised "shape" (its filename with volatile parts
    erased), and ranks the shapes that recur across the widest span of
    directories. Recurring shapes are where work compounds: the hundredth
    instance should cost less than the first.

WHAT IT IS NOT
    The score is a HAND-TUNED RANKING HEURISTIC, not a measurement. Every
    constant under TUNABLE HEURISTICS is a guess. Under SCOPE.md's evidence
    rules this output is a hypothesis, not a receipt. If you want a real eta
    figure, pass --hours-per-instance with a rate you actually measured; the
    script then reports your arithmetic rather than inventing one.

FIXES OVER v1
    1. Platform-aware root detection — runs on Termux and OptiPlex alike.
       (v1 hardcoded /home/jesse/openroot and died on the phone.)
    2. Schema introspection — discovers real column names instead of
       assuming `size` and `hashed_at`. (v1 emitted 73 spurious warnings
       and read zero rows because of this.)
    3. --dry-run is honoured. (v1 ignored it and wrote anyway.)
    4. Streaming aggregation — bounded memory on the 581k-row manifest.
    5. Atomic ledger append; degrades gracefully on read-only mounts.
    6. Quiet by default; --verbose explains every skipped database.
    7. No fabricated time savings unless you supply the rate.

USAGE
    python3 bin/synergetic_compounding_v2.py --top 20
    python3 bin/synergetic_compounding_v2.py --dry-run --verbose
    python3 bin/synergetic_compounding_v2.py --hours-per-instance 0.25 --emit-todo
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

# ---------------------------------------------------------------------------
# TUNABLE HEURISTICS — hand-chosen, not measured. Change freely.
# ---------------------------------------------------------------------------

# Share multiplier by how widely a shape's content reaches.
SHARE_WEIGHT = {
    "private": 1.0,   # one directory only
    "shared": 1.5,    # 2-3 directories
    "commons": 2.0,   # 4+ directories
}

COORDINATION_PER_DIR = 0.05   # spread penalty slope
COUNT_DAMPING = 0.5           # sqrt(N): stops raw count dominating outright
PARENT_SET_CAP = 10000        # memory guard on breadth tracking

# Candidate table names, in preference order.
MANIFEST_TABLES = ("manifest", "hash_manifest")

# Column-name candidates, in preference order.
PATH_COLS = ("path", "file_path", "rel_path", "abs_path")
SIZE_COLS = ("size", "size_bytes", "bytes", "st_size", "file_size")
TIME_COLS = ("hashed_at", "scanned_at", "indexed_at", "mtime", "mtime_ns")

# Volatile path segments erased before shapes are compared.
VOLATILE_PATTERNS = [
    (re.compile(r"[0-9a-fA-F]{16,}"), "[HEX]"),
    (re.compile(r"\d{8}[T_-]?\d{0,6}Z?"), "[STAMP]"),
    (re.compile(r"\d+"), "#"),
]


# ---------------------------------------------------------------------------
# Environment detection
# ---------------------------------------------------------------------------

def detect_root(cli_root: str | None) -> Path:
    """Resolve the OpenRoot tree, preferring explicit input over inference."""
    if cli_root:
        return Path(cli_root).expanduser().resolve()

    env = os.environ.get("OPENROOT_ROOT")
    if env:
        return Path(env).expanduser().resolve()

    home = Path.home()
    for candidate in (home / "openroot", Path("/home/jesse/openroot")):
        if (candidate / "data").is_dir():
            return candidate

    return home / "openroot"


def host_label() -> str:
    """Identify the platform so receipts record where they were produced."""
    if Path("/data/data/com.termux/files/home").is_dir():
        return "termux"
    return os.uname().nodename or "unknown"


# ---------------------------------------------------------------------------
# Timestamp handling — manifests mix ISO strings and nanosecond integers
# ---------------------------------------------------------------------------

def parse_ts(value) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        v = float(value)
        try:
            if v > 1e17:      # nanoseconds
                return datetime.fromtimestamp(v / 1e9, tz=timezone.utc)
            if v > 1e11:      # milliseconds
                return datetime.fromtimestamp(v / 1e3, tz=timezone.utc)
            if v > 1e8:       # seconds
                return datetime.fromtimestamp(v, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
        return None

    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Schema introspection
# ---------------------------------------------------------------------------

def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}
    except sqlite3.Error:
        return set()


def find_manifest_table(conn: sqlite3.Connection):
    """Return (table, columns) for the first table that looks like a manifest."""
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    except sqlite3.Error:
        return None, set()

    for candidate in MANIFEST_TABLES:
        if candidate in tables:
            cols = table_columns(conn, candidate)
            if any(c in cols for c in PATH_COLS):
                return candidate, cols
    return None, set()


def pick(cols: set[str], candidates) -> str | None:
    for name in candidates:
        if name in cols:
            return name
    return None


# ---------------------------------------------------------------------------
# Shape normalisation
# ---------------------------------------------------------------------------

def normalise(text: str) -> str:
    for pattern, replacement in VOLATILE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def shape_of(path_str: str) -> tuple[str, str]:
    """Return (shape_key, parent_dir) for a file path."""
    posix = PurePosixPath(path_str)
    stem = normalise(posix.stem)
    suffix = posix.suffix.lower()
    shape = f"{stem}{suffix}" if suffix else stem
    return shape, normalise(str(posix.parent))


def share_band(breadth: int) -> str:
    if breadth <= 1:
        return "private"
    if breadth <= 3:
        return "shared"
    return "commons"


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

class Family:
    """Accumulator for one recurring shape."""

    __slots__ = ("shape", "count", "total_bytes", "first", "last", "parents", "capped")

    def __init__(self, shape: str):
        self.shape = shape
        self.count = 0
        self.total_bytes = 0
        self.first: datetime | None = None
        self.last: datetime | None = None
        self.parents: set[str] = set()
        self.capped = False

    def add(self, size: int, stamp: datetime | None, parent: str) -> None:
        self.count += 1
        self.total_bytes += size
        if stamp is not None:
            if self.first is None or stamp < self.first:
                self.first = stamp
            if self.last is None or stamp > self.last:
                self.last = stamp
        if not self.capped:
            self.parents.add(parent)
            if len(self.parents) >= PARENT_SET_CAP:
                self.capped = True

    @property
    def breadth(self) -> int:
        return len(self.parents)

    def score(self) -> dict:
        n_eff = self.count ** COUNT_DAMPING
        r_eff = 1.0 + math.log1p(self.breadth)
        band = share_band(self.breadth)
        a_weight = SHARE_WEIGHT[band]
        cost = COORDINATION_PER_DIR * self.breadth
        value = (n_eff * r_eff * math.exp(a_weight)) / (1.0 + cost)
        return {
            "score": round(value, 3),
            "n_eff": round(n_eff, 3),
            "r_eff": round(r_eff, 3),
            "band": band,
            "a_weight": a_weight,
            "cost": round(cost, 3),
        }


def scan_database(db_path: Path, families: dict[str, Family], verbose: bool):
    """Stream one database into the family accumulators. Returns a status string."""
    conn = None
    try:
        conn = sqlite3.connect(
            f"file:{db_path}?mode=ro", uri=True, timeout=3
        )
        table, cols = find_manifest_table(conn)
        if table is None:
            return "skip: no manifest table"

        path_col = pick(cols, PATH_COLS)
        size_col = pick(cols, SIZE_COLS)
        time_col = pick(cols, TIME_COLS)

        selection = ", ".join(
            [
                f'"{path_col}"',
                f'"{size_col}"' if size_col else "NULL",
                f'"{time_col}"' if time_col else "NULL",
            ]
        )

        rows = 0
        for raw_path, raw_size, raw_time in conn.execute(
            f'SELECT {selection} FROM "{table}"'
        ):
            if not raw_path:
                continue
            try:
                size = int(raw_size) if raw_size is not None else 0
            except (TypeError, ValueError):
                size = 0

            shape, parent = shape_of(str(raw_path))
            family = families.get(shape)
            if family is None:
                family = Family(shape)
                families[shape] = family
            family.add(size, parse_ts(raw_time), parent)
            rows += 1

        detail = f"{rows} rows"
        if not size_col:
            detail += " (no size column)"
        if not time_col:
            detail += " (no time column)"
        return f"ok: {detail}"

    except sqlite3.Error as exc:
        return f"skip: {exc}"
    except OSError as exc:
        return f"skip: {exc}"
    finally:
        if conn is not None:
            conn.close()


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------

def load_known_shapes(ledger: Path) -> set[str]:
    known: set[str] = set()
    if not ledger.is_file():
        return known
    try:
        with ledger.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                shape = record.get("shape")
                if shape:
                    known.add(shape)
    except OSError:
        pass
    return known


def write_receipt(ledger: Path, record: dict) -> str:
    """Append one receipt atomically. Returns the receipt id, or '' on failure."""
    payload = json.dumps(record, sort_keys=True, default=str)
    receipt_id = hashlib.sha256(payload.encode()).hexdigest()[:16]
    line = json.dumps({"id": receipt_id, **record}, sort_keys=True, default=str)

    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return receipt_id
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def render_table(ranked, top: int, hours_per_instance: float) -> None:
    header = (
        f"{'#':>3}  {'shape':<38} {'N':>7} {'dirs':>5} "
        f"{'band':<8} {'score':>10}"
    )
    print(header)
    print("-" * len(header))

    for index, (family, metrics) in enumerate(ranked[:top], start=1):
        shape = family.shape
        if len(shape) > 38:
            shape = shape[:35] + "..."
        print(
            f"{index:>3}  {shape:<38} {family.count:>7} {family.breadth:>5} "
            f"{metrics['band']:<8} {metrics['score']:>10.2f}"
        )

    if hours_per_instance > 0:
        print()
        print(f"Time arithmetic at your supplied rate of "
              f"{hours_per_instance} h/instance:")
        total = 0.0
        for family, _ in ranked[:top]:
            saved = family.count * hours_per_instance
            total += saved
            print(f"  {family.shape[:44]:<44} {saved:>9.2f} h")
        print(f"  {'TOTAL (top ' + str(min(top, len(ranked))) + ')':<44} {total:>9.2f} h")


def emit_todo(root: Path, ranked, top: int) -> Path | None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = root / "context_bridge" / f"synergetic_todo_{stamp}.md"

    lines = [
        f"# Synergetic compounding TODO — {stamp}",
        "",
        "Generated by bin/synergetic_compounding_v2.py.",
        "Ranked by hand-tuned heuristic. Verify before acting.",
        "",
        "| # | shape | instances | dirs | band | score |",
        "|---|-------|-----------|------|------|-------|",
    ]
    for index, (family, metrics) in enumerate(ranked[:top], start=1):
        lines.append(
            f"| {index} | `{family.shape}` | {family.count} | "
            f"{family.breadth} | {metrics['band']} | {metrics['score']:.2f} |"
        )
    lines.append("")

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines), encoding="utf-8")
        return target
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Rank recurring file shapes across OpenRoot manifests."
    )
    parser.add_argument("--root", help="OpenRoot tree (default: auto-detect)")
    parser.add_argument("--top", type=int, default=15, help="rows to display")
    parser.add_argument(
        "--min-instances", type=int, default=2,
        help="ignore shapes appearing fewer times (default: 2)",
    )
    parser.add_argument(
        "--hours-per-instance", type=float, default=0.0,
        help="your measured rate; 0 disables time arithmetic",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="analyse only; write nothing")
    parser.add_argument("--verbose", action="store_true",
                        help="explain every skipped database")
    parser.add_argument("--emit-todo", action="store_true",
                        help="write a markdown action list")
    args = parser.parse_args(argv)

    root = detect_root(args.root)
    data_dir = root / "data"
    ledger = root / "acre" / "LEDGER.jsonl"

    print("=" * 68)
    print("SYNERGETIC COMPOUNDING v2")
    print("=" * 68)
    print(f"host      : {host_label()}")
    print(f"root      : {root}")
    print(f"data dir  : {data_dir}  ({'found' if data_dir.is_dir() else 'MISSING'})")
    print(f"ledger    : {ledger}")
    print(f"mode      : {'DRY RUN (nothing written)' if args.dry_run else 'live'}")
    print()

    if not data_dir.is_dir():
        print(f"FATAL: no data directory at {data_dir}")
        print("Hint: pass --root, or set OPENROOT_ROOT.")
        return 2

    databases = sorted(
        set(data_dir.glob("*.db")) | set(data_dir.glob("*.sqlite3"))
    )
    print(f"[1/4] scanning {len(databases)} database(s)...")

    families: dict[str, Family] = {}
    ok = skipped = 0
    for db_path in databases:
        status = scan_database(db_path, families, args.verbose)
        if status.startswith("ok:"):
            ok += 1
            if args.verbose:
                print(f"      {db_path.name:<44} {status}")
        else:
            skipped += 1
            if args.verbose:
                print(f"      {db_path.name:<44} {status}")

    print(f"      readable manifests: {ok}   skipped: {skipped}")

    total_rows = sum(f.count for f in families.values())
    print()
    print(f"[2/4] extracted {total_rows} file records")
    print(f"      distinct shapes: {len(families)}")

    ranked = [
        (family, family.score())
        for family in families.values()
        if family.count >= args.min_instances
    ]
    ranked.sort(key=lambda pair: pair[1]["score"], reverse=True)
    print(f"      shapes meeting min-instances ({args.min_instances}): {len(ranked)}")

    if not ranked:
        print()
        print("Nothing to rank. Either the manifests are empty or every shape")
        print("appears once. Try --min-instances 1 to see singletons.")
        return 0

    print()
    print(f"[3/4] top {min(args.top, len(ranked))} recurring shapes")
    print()
    render_table(ranked, args.top, args.hours_per_instance)

    print()
    print("[4/4] receipts")
    if args.dry_run:
        print("      dry run — ledger untouched")
        receipt_ids = []
    else:
        known = load_known_shapes(ledger)
        receipt_ids = []
        for family, metrics in ranked[:args.top]:
            if family.shape in known:
                continue
            record = {
                "type": "synergetic-compounding",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "host": host_label(),
                "root": str(root),
                "shape": family.shape,
                "instances": family.count,
                "directories": family.breadth,
                "breadth_capped": family.capped,
                "total_bytes": family.total_bytes,
                "band": metrics["band"],
                "score": metrics["score"],
                "score_is_heuristic": True,
                "first_seen": family.first.isoformat() if family.first else None,
                "last_seen": family.last.isoformat() if family.last else None,
            }
            rid = write_receipt(ledger, record)
            if rid:
                receipt_ids.append(rid)

        if receipt_ids:
            print(f"      wrote {len(receipt_ids)} new receipt(s) to {ledger}")
            print(f"      ids: {', '.join(receipt_ids[:5])}")
        else:
            print("      no new receipts (all shapes already recorded, or "
                  "ledger not writable)")

    summary = {
        "host": host_label(),
        "root": str(root),
        "databases_scanned": len(databases),
        "databases_readable": ok,
        "records_extracted": total_rows,
        "distinct_shapes": len(families),
        "ranked_shapes": len(ranked),
        "receipts_written": len(receipt_ids),
        "top": [
            {
                "shape": family.shape,
                "instances": family.count,
                "directories": family.breadth,
                "score": metrics["score"],
                "band": metrics["band"],
            }
            for family, metrics in ranked[:args.top]
        ],
    }

    if not args.dry_run:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = root / f"compost_cycle_{stamp}.json"
        try:
            summary_path.write_text(
                json.dumps(summary, indent=2, default=str), encoding="utf-8"
            )
            print(f"      summary: {summary_path}")
        except OSError as exc:
            print(f"      summary not written: {exc}")

    if args.emit_todo and not args.dry_run:
        todo_path = emit_todo(root, ranked, args.top)
        if todo_path:
            print(f"      todo list: {todo_path}")

    print()
    print("=" * 68)
    print("NOTE: scores are a hand-tuned ranking heuristic, not measurements.")
    print("Treat them as a hypothesis about where work compounds.")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())

