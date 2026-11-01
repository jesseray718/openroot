#!/usr/bin/env python3
"""OpenHuman background supervisor — single-flock model health + heartbeat receipts.

η-first: one process, one lock, one JSONL chain. No external deps.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import signal
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "data" / ".openhuman_supervisor.lock"
CHAIN = ROOT / "data" / "bot_heartbeats.jsonl"
GENESIS = "0" * 64
DEFAULT_INTERVAL = 60

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha(obj: dict) -> str:
    body = {k: v for k, v in obj.items() if k != "hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

def last_hash(path: Path) -> str:
    if not path.exists():
        return GENESIS
    last = GENESIS
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                last = json.loads(line).get("hash", last)
            except json.JSONDecodeError:
                continue
    return last

def probe(url: str, timeout: float = 2.5) -> dict:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(512)
            return {"ok": True, "status": resp.status, "bytes": len(data)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:120]}

def append_receipt(event: str, payload: dict) -> str:
    prev = last_hash(CHAIN)
    rec = {
        "block_id": None,  # filled after count
        "timestamp": utc_now(),
        "event": event,
        "host": socket.gethostname(),
        "payload": payload,
        "previous_hash": prev,
    }
    # count existing lines for block_id
    n = 0
    if CHAIN.exists():
        with CHAIN.open(encoding="utf-8") as fh:
            n = sum(1 for line in fh if line.strip())
    rec["block_id"] = n
    rec["hash"] = sha(rec)
    CHAIN.parent.mkdir(parents=True, exist_ok=True)
    with CHAIN.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return rec["hash"]

def run_loop(interval: int, ollama: str, llama: str) -> None:
    print(f"[openhuman] supervisor start  interval={interval}s  chain={CHAIN}")
    stop = False

    def _stop(signum, frame):  # noqa: ARG001
        nonlocal stop
        stop = True
        print("\n[openhuman] signal received, shutting down")

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    while not stop:
        ollama_r = probe(f"{ollama}/v1/models")
        llama_r = probe(f"{llama}/v1/models")
        healthy = ollama_r.get("ok") or llama_r.get("ok")
        event = "MODEL_HEALTH_OK" if healthy else "MODEL_HEALTH_DEGRADED"
        h = append_receipt(event, {
            "ollama": ollama_r,
            "llama_server": llama_r,
            "interval_s": interval,
        })
        status = "OK" if healthy else "DEGRADED"
        print(f"[{utc_now()}] {status}  hash={h[:12]}…  ollama={ollama_r.get('ok')}  llama={llama_r.get('ok')}")
        for _ in range(interval):
            if stop:
                break
            time.sleep(1)
    print("[openhuman] exit clean")

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    ap.add_argument("--ollama", default="http://127.0.0.1:11434")
    ap.add_argument("--llama", default="http://127.0.0.1:8080")
    ap.add_argument("--once", action="store_true", help="single probe then exit")
    args = ap.parse_args()

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = os.open(LOCK, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("[openhuman] another supervisor is already running (flock held)", file=sys.stderr)
        return 2

    if args.once:
        ollama_r = probe(f"{args.ollama}/v1/models")
        llama_r = probe(f"{args.llama}/v1/models")
        healthy = ollama_r.get("ok") or llama_r.get("ok")
        event = "MODEL_HEALTH_OK" if healthy else "MODEL_HEALTH_DEGRADED"
        h = append_receipt(event, {"ollama": ollama_r, "llama_server": llama_r, "once": True})
        print(json.dumps({"event": event, "hash": h, "ollama": ollama_r, "llama": llama_r}, indent=2))
        return 0 if healthy else 1

    run_loop(args.interval, args.ollama, args.llama)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
