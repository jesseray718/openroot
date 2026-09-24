#!/data/data/com.termux/files/usr/bin/python3
from __future__ import annotations
import sys, json, time
from pathlib import Path

BRIDGE = Path("/sdcard/openroot/context_bridge/context.json")
LEDGER = Path("/sdcard/openroot/thermo_ledger/eta_moves.jsonl")

def load_bridge():
    if BRIDGE.exists():
        try:
            return json.loads(BRIDGE.read_text())
        except Exception:
            return {}
    return {}

def latest_human_move():
    if not LEDGER.exists():
        return None
    lines = LEDGER.read_text().strip().splitlines()
    for line in reversed(lines):
        try:
            r = json.loads(line)
            if r.get("event") == "human_physical_move":
                return r
        except Exception:
            continue
    return None

def sample_joules():
    try:
        import subprocess
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=4)
        if r.returncode == 0:
            d = json.loads(r.stdout)
            return {"percent": d.get("percentage"), "status": d.get("status"), "source": "termux-api", "ts": time.time()}
    except Exception:
        pass
    return {"error": "no_api", "ts": time.time()}

def score_query(q: str) -> str:
    sample = sample_joules()
    last = latest_human_move()
    lowest = "Me" if last and "Me" in str(last.get("sentence", "")) else "unknown"

    if lowest == "Me":
        move = (
            "Sit or stand still for 60 seconds while breathing only through the nose. "
            "Count every complete breath cycle. When finished, speak the final count aloud "
            "and immediately record it with the joule sample. "
            "This raises the floor for Me (attention + body regulation) and simultaneously "
            "gives every other node a free, zero-cost practice."
        )
        record_cmd = (
            'python3 -c \''
            'import json,time;from pathlib import Path;'
            's=input("Breath count: ");'
            'r={"event":"human_physical_move","sentence":"Breath count: "+s,'
            '"eta_sample_at_speak":' + json.dumps(sample) + ','
            '"ts":time.time(),"authority":"Promote only what demonstrably raises Etha for the lowest node."};'
            'Path("/sdcard/openroot/thermo_ledger/eta_moves.jsonl").open("a").write(json.dumps(r)+"\\n");'
            'print("RECORDED")\''
        )
    else:
        move = "Re-state the current lowest node in one true sentence and record it."
        record_cmd = "use the previous recording block"

    record = {
        "event": "oracle_query",
        "query": q,
        "sample": sample,
        "atomic_move": move,
        "ts": time.time(),
        "authority": "Promote only what demonstrably raises Etha for the lowest node."
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps(record) + "\n")

    return (
        f"Etha sample: {json.dumps(sample)}\n"
        f"Atomic physical move: {move}\n"
        f"Exact recording command:\n{record_cmd}"
    )

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "interactive":
        print(score_query(" ".join(sys.argv[1:])))
    else:
        print("agape_engine ready. Root invariants locked. Etha sole language.")
