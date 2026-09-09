#!/usr/bin/env python3
import json, os, socket, sys, time
from datetime import datetime, timezone
from pathlib import Path
LEDGER = Path("/home/jesse/openroot/closed-loop/ledger/eta-ledger.jsonl")
PERIOD = float(os.environ.get("OPENROOT_OBSERVER_PERIOD", "300"))
ONCE = "--once" in sys.argv
def rapl():
    p = Path("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj")
    try:
        return int(p.read_text().strip()) / 1e6
    except Exception:
        return None
def row():
    j = rapl()
    load = Path("/proc/loadavg").read_text().split()[:3]
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "observer_heartbeat",
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "loadavg": [float(x) for x in load],
        "rapl_j": j,
        "energy_grade": "MEASURED" if j is not None else "UNAVAILABLE",
        "argv": sys.argv[1:],
    }
def main():
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    while True:
        r = row()
        LEDGER.open("a", encoding="utf-8").write(json.dumps(r, separators=(",", ":")) + chr(10))
        print(json.dumps(r), flush=True)
        if ONCE:
            return 0
        time.sleep(PERIOD)
if __name__ == "__main__":
    raise SystemExit(main())
