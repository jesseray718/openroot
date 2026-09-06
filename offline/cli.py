#!/usr/bin/env python3
"""offline_cli.py – Non-coder friendly CLI for the OpenRoot offline toolkit.

Commands
--------
  init    Bootstrap local data directories and write default config.
  status  Show queue stats, dedup index, storage usage, and pressure state.
  work    Enqueue a work item for offline processing.
  sync    Replay pending queue items (no-op if no sync endpoint is configured).
  purge   Hard-purge records eligible for deletion according to retention policy.
  doctor  Validate local environment and config.

Usage
-----
  python -m offline.cli <command> [options]

Or, after adding to PATH / scripts:
  offline:init
  offline:status
  offline:work  --type <op_type> --payload '{"key":"value"}'
  offline:sync
  offline:purge [--confirm]
  offline:doctor
"""
import argparse
import json
import logging
import sys
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure repository root on path when executed directly
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from offline.config import load_config
from offline.queue import OperationQueue
from offline.dedup import DedupIndex
from offline.lifecycle import DataLifecycle
from offline.priority import PriorityScorer
from offline.thermal import ThermalRegulator

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hr():
    print("─" * 60)


def _fmt_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b //= 1024
    return f"{b:.1f} TB"


def _dir_size(path: str) -> int:
    total = 0
    p = Path(path)
    if p.exists():
        for f in p.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    return total


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(cfg: dict, args) -> None:
    data_dir = cfg["data_dir"]
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    # Write example config.json if absent
    cfg_file = Path(data_dir) / "config.json"
    if not cfg_file.exists():
        example = {
            "soft_delete_retention_days": 30,
            "priority_weight_urgency": 1.0,
            "priority_weight_impact": 1.0,
            "thermal_cpu_high_threshold": 80.0,
            "thermal_cpu_low_threshold": 40.0,
            "thermal_max_concurrency": 4,
            "sync_endpoint": "",
        }
        with open(cfg_file, "w") as fh:
            json.dump(example, fh, indent=2)
        print(f"✓ Config written → {cfg_file}")
    else:
        print(f"✓ Config already exists → {cfg_file}")
    print(f"✓ Data directory ready → {data_dir}")
    print("\nOffline toolkit initialized. Run `offline:status` to check.")


def cmd_status(cfg: dict, args) -> None:
    q = OperationQueue(cfg["queue_file"])
    d = DedupIndex(cfg["dedup_index_file"])
    lc = DataLifecycle(cfg["lifecycle_file"], cfg["soft_delete_retention_days"])
    tr = ThermalRegulator(
        cfg["thermal_cpu_high_threshold"],
        cfg["thermal_cpu_low_threshold"],
        cfg["thermal_max_concurrency"],
    )

    _hr()
    print("  OpenRoot Offline Toolkit — Status")
    _hr()

    # Queue
    qs = q.stats()
    print(f"\n📋 Queue")
    print(f"   Total entries : {qs['total']}")
    for status, count in qs.get("by_status", {}).items():
        print(f"   {status:<12}: {count}")

    # Dedup
    ds = d.stats()
    print(f"\n🔍 Dedup Index")
    print(f"   Canonical records : {ds['total_canonical']}")
    print(f"   Total references  : {ds['total_references']}")
    print(f"   Deduped savings   : {ds['deduped_savings']}")

    # Lifecycle
    ls = lc.stats()
    print(f"\n🗑  Lifecycle")
    print(f"   Soft-deleted       : {ls['soft_deleted']}")
    print(f"   Hard-purged        : {ls['hard_purged']}")
    print(f"   Eligible for purge : {ls['eligible_for_purge']}")

    # Thermal
    snap = tr.snapshot()
    pressure = tr.pressure_state()
    allowed = tr.allowed_concurrency()
    print(f"\n🌡  Resource Pressure")
    print(f"   CPU        : {snap['cpu_percent']}%")
    print(f"   Memory     : {snap['mem_percent']}%")
    temp_str = f"{snap['temperature_c']}°C" if snap['temperature_c'] is not None else "N/A"
    print(f"   Temp       : {temp_str}")
    print(f"   State      : {pressure}")
    print(f"   Concurrency: {allowed}/{cfg['thermal_max_concurrency']}")

    # Storage
    size = _dir_size(cfg["data_dir"])
    print(f"\n💾 Storage  {_fmt_bytes(size)}  →  {cfg['data_dir']}")
    _hr()


def cmd_work(cfg: dict, args) -> None:
    scorer = PriorityScorer(
        cfg["priority_weight_urgency"],
        cfg["priority_weight_impact"],
    )
    q = OperationQueue(cfg["queue_file"])

    payload = {}
    if args.payload:
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            payload = {"raw": args.payload}

    urgency = float(args.urgency)
    impact = float(args.impact)
    score = scorer.score(urgency, impact)

    idem_key = q.enqueue(
        op_type=args.type,
        payload=payload,
        urgency=urgency,
        impact=impact,
    )
    print(f"✓ Enqueued  idem_key={idem_key}")
    print(f"  op_type={args.type}  urgency={urgency}  impact={impact}  score={score:.2f}")


def cmd_sync(cfg: dict, args) -> None:
    endpoint = cfg.get("sync_endpoint", "")
    q = OperationQueue(cfg["queue_file"])
    scorer = PriorityScorer(
        cfg["priority_weight_urgency"],
        cfg["priority_weight_impact"],
    )

    pending = scorer.rank(q.pending())
    if not pending:
        print("✓ Queue is empty – nothing to sync.")
        return

    if not endpoint:
        print(f"ℹ  No sync endpoint configured (OFFLINE_SYNC_ENDPOINT is empty).")
        print(f"   {len(pending)} pending operation(s) queued – will sync when endpoint is set.")
        for item in pending:
            print(f"   [{item['_score']:.1f}] {item['op_type']} – {item['idem_key'][:8]}…")
        return

    # Minimal HTTP sync – only runs if endpoint is set
    import urllib.request, urllib.error
    applied = 0
    for item in pending:
        body = json.dumps(item).encode()
        req = urllib.request.Request(endpoint, data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10):
                q.mark_applied(item["idem_key"])
                applied += 1
        except (urllib.error.URLError, OSError) as exc:
            q.mark_failed(item["idem_key"], reason=str(exc))
            print(f"✗ Failed to sync {item['idem_key'][:8]}: {exc}")

    print(f"✓ Synced {applied}/{len(pending)} operation(s).")


def cmd_purge(cfg: dict, args) -> None:
    lc = DataLifecycle(cfg["lifecycle_file"], cfg["soft_delete_retention_days"])
    d = DedupIndex(cfg["dedup_index_file"])
    eligible = lc.purge_eligible()

    if not eligible:
        print("✓ Nothing eligible for purge.")
        return

    print(f"⚠  {len(eligible)} record(s) eligible for hard purge:")
    for e in eligible:
        print(f"   record_id={e['record_id']}")

    if not args.confirm:
        print("\nRe-run with --confirm to execute purge.")
        return

    purged = 0
    for e in eligible:
        if lc.hard_purge(e["record_id"], confirmed=True):
            d.remove(e["record_id"])  # remove from dedup index too
            purged += 1

    print(f"✓ Purged {purged} record(s).")


def cmd_doctor(cfg: dict, args) -> None:
    issues = []
    data_dir = Path(cfg["data_dir"])

    _hr()
    print("  OpenRoot Offline Toolkit — Doctor")
    _hr()

    # Check data dir
    if data_dir.exists():
        print(f"✓ Data dir exists      : {data_dir}")
    else:
        issues.append(f"Data directory missing: {data_dir} (run offline:init)")
        print(f"✗ Data dir missing     : {data_dir}")

    # Python version
    import platform
    pyver = platform.python_version()
    print(f"✓ Python               : {pyver}")
    if tuple(int(x) for x in pyver.split(".")[:2]) < (3, 8):
        issues.append("Python 3.8+ required")

    # Optional: psutil
    try:
        import psutil
        print(f"✓ psutil               : {psutil.__version__} (enhanced metrics)")
    except ImportError:
        print("ℹ  psutil not installed  (fallback heuristics will be used)")

    # Config file
    cfg_file = data_dir / "config.json"
    if cfg_file.exists():
        print(f"✓ Config file          : {cfg_file}")
    else:
        print(f"ℹ  Config file absent   : run offline:init to create one")

    # Sync endpoint
    if cfg.get("sync_endpoint"):
        print(f"✓ Sync endpoint        : {cfg['sync_endpoint']}")
    else:
        print("ℹ  Sync endpoint not set (offline-only mode)")

    _hr()
    if issues:
        print(f"⚠  {len(issues)} issue(s) found:")
        for iss in issues:
            print(f"   • {iss}")
        sys.exit(1)
    else:
        print("✓ All checks passed.")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="offline",
        description="OpenRoot offline-first toolkit CLI",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    sub.add_parser("init", help="Bootstrap local toolkit")
    sub.add_parser("status", help="Show queue, dedup, storage, and pressure state")

    wp = sub.add_parser("work", help="Enqueue a local work item")
    wp.add_argument("--type", default="task", help="Operation type (default: task)")
    wp.add_argument("--payload", default="{}", help="JSON payload string")
    wp.add_argument("--urgency", default="1.0", help="Urgency 0-10 (default 1.0)")
    wp.add_argument("--impact", default="1.0", help="Impact 0-10 (default 1.0)")

    sub.add_parser("sync", help="Replay queued operations when online")

    pp = sub.add_parser("purge", help="Hard-purge eligible records")
    pp.add_argument("--confirm", action="store_true", help="Actually execute the purge")

    sub.add_parser("doctor", help="Validate local environment and config")

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_config()

    dispatch = {
        "init": cmd_init,
        "status": cmd_status,
        "work": cmd_work,
        "sync": cmd_sync,
        "purge": cmd_purge,
        "doctor": cmd_doctor,
    }
    dispatch[args.command](cfg, args)


if __name__ == "__main__":
    main()
