#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""Summarize OpenRoot activity over a rolling window (default 12h).

Reads the Newton chain, discovery chain, bot heartbeats, and git log,
then produces a compact digest suitable for pasting into a session.
"""

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
NEWTON = ROOT / "ledger" / "newton_chain.jsonl"
DISCOVERY = ROOT / "ledger" / "discovery_chain.jsonl"
HEARTBEATS = ROOT / "data" / "bot_heartbeats.jsonl"


def parse_ts(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def summarize_chain(path: Path, since: datetime, label: str) -> dict:
    records = load_jsonl(path)
    window = []
    for rec in records:
        ts = parse_ts(rec.get("timestamp", ""))
        if ts and ts >= since:
            window.append((ts, rec))

    events = Counter(rec.get("event", "UNKNOWN") for _, rec in window)
    first_ts = min((ts for ts, _ in window), default=None)
    last_ts = max((ts for ts, _ in window), default=None)

    return {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
        "total_records": len(records),
        "window_records": len(window),
        "events": dict(events.most_common()),
        "first_in_window": first_ts.isoformat() if first_ts else None,
        "last_in_window": last_ts.isoformat() if last_ts else None,
        "tail_block_id": records[-1].get("block_id") if records else None,
        "tail_hash": records[-1].get("hash", "")[:16] if records else None,
    }


def git_activity(since: datetime) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--since", since.isoformat(),
             "--pretty=format:%h %ad %s", "--date=short"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return [f"git error: {result.stderr.strip()}"]
        return [line for line in result.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.SubprocessError) as exc:
        return [f"git unavailable: {exc}"]
    

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=float, default=12.0, help="Lookback window in hours")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=args.hours)

    report = {
        "generated_at": now.isoformat(),
        "window_hours": args.hours,
        "window_start": since.isoformat(),
        "chains": [
            summarize_chain(NEWTON, since, "newton_chain"),
            summarize_chain(DISCOVERY, since, "discovery_chain"),
            summarize_chain(HEARTBEATS, since, "bot_heartbeats"),
        ],
        "git_commits": git_activity(since),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("=" * 72)
    print(f"OPENROOT ACTIVITY DIGEST — last {args.hours:g}h")
    print(f"Generated: {report['generated_at']}")
    print(f"Window start: {report['window_start']}")
    print("=" * 72)

    for chain in report["chains"]:
        print(f"\n── {chain['label']} ──")
        if not chain["exists"]:
            print("   [absent] file does not exist")
            continue
        print(f"   total records:  {chain['total_records']}")
        print(f"   in window:      {chain['window_records']}")
        print(f"   tail block_id:  {chain['tail_block_id']}")
        print(f"   tail hash:      {chain['tail_hash']}…")
        if chain["events"]:
            print("   events:")
            for event, count in chain["events"].items():
                print(f"      {event:<32} {count}")
        if chain["first_in_window"]:
            print(f"   first: {chain['first_in_window']}")
            print(f"   last:  {chain['last_in_window']}")

    print(f"\n── git commits ({len(report['git_commits'])}) ──")
    for line in report["git_commits"][:20]:
        print(f"   {line}")
    if len(report["git_commits"]) > 20:
        print(f"   … and {len(report['git_commits']) - 20} more")

    print("\n" + "=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
