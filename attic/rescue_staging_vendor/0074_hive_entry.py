#!/usr/bin/env python3
# OpenRoot A15 hive — delegate + health + budget + continuous + dual ledger
import os, sys, json, time, subprocess, signal, socket
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
OPENROOT = Path("/sdcard/openroot")
UNE_STAMPS = HOME / "une" / "stamps"
LEDGER = OPENROOT / "thermo_ledger.jsonl"
UNE_LEDGER = UNE_STAMPS / "thermo_ledger.jsonl"
ARTIFACTS = OPENROOT / "artifacts"
PIDFILE = OPENROOT / "hive_logger.pid"
BUDGET_FILE = OPENROOT / "session_budget.json"

# Spoke
SPOKE_HOST = os.environ.get("OPENROOT_SPOKE", "optiplex")
SPOKE_PORT = 8080
SPOKE_URL = f"http://{SPOKE_HOST}:{SPOKE_PORT}/v1/chat/completions"
MODEL_ALIAS = "qwen2.5-coder-7b"

for d in (OPENROOT, ARTIFACTS, UNE_STAMPS):
    d.mkdir(parents=True, exist_ok=True)

_current_tier = "fallback"
_rish_ok = False

def rish(cmd, timeout=6):
    try:
        r = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "RISH_PRESERVE_ENV": "0"})
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def probe_tier():
    global _current_tier, _rish_ok
    if rish("whoami") == "shell":
        _rish_ok = True
        _current_tier = "shell-uid"
    else:
        _rish_ok = False
        try:
            subprocess.run(["termux-wake-lock"], capture_output=True, timeout=3)
            _current_tier = "termux-native"
        except Exception:
            _current_tier = "fallback"

def termux_battery():
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return json.loads(r.stdout)
    except Exception:
        pass
    return None

def _now():
    return datetime.now(timezone.utc).isoformat()

def ledger_append(rec, also_une=True):
    rec = dict(rec)
    rec["ts"] = _now()
    rec["tier"] = _current_tier
    line = json.dumps(rec, separators=(",", ":")) + "\n"
    with open(LEDGER, "a") as f:
        f.write(line)
    if also_une:
        with open(UNE_LEDGER, "a") as f:
            f.write(line)

def say(msg, **extra):
    print(msg, flush=True)
    ledger_append({"event": "say", "msg": msg, **extra})

def sample_once():
    tb = termux_battery() or {}
    t = time.time()
    v = tb.get("voltage")
    i = tb.get("current")
    power = (v / 1000.0) * (abs(i) / 1_000_000.0) if v is not None and i is not None else None
    return {
        "t": t, "voltage_mV": v, "current_uA": i,
        "percentage": tb.get("percentage"), "charge_counter_uAh": tb.get("charge_counter"),
        "status": tb.get("status"), "plugged": tb.get("plugged"), "power_W": power,
    }

# ------------------------------------------------------------------
# Spoke health
# ------------------------------------------------------------------
def spoke_alive(timeout=0.5):
    try:
        with socket.create_connection((SPOKE_HOST, SPOKE_PORT), timeout=timeout):
            return True
    except Exception:
        return False

# ------------------------------------------------------------------
# Budget gate
# ------------------------------------------------------------------
def load_budget():
    if BUDGET_FILE.exists():
        try:
            return json.loads(BUDGET_FILE.read_text())
        except Exception:
            pass
    return {"ceiling_J": None, "spent_J": 0.0}

def save_budget(b):
    BUDGET_FILE.write_text(json.dumps(b, indent=2))

def budget_check(extra_J=0.0):
    b = load_budget()
    if b.get("ceiling_J") is None:
        return True
    if b["spent_J"] + extra_J > b["ceiling_J"]:
        ledger_append({"event": "BUDGET_EXCEEDED", "spent_J": b["spent_J"], "ceiling_J": b["ceiling_J"]})
        say(f"BUDGET_EXCEEDED spent={b['spent_J']:.2f}J ceiling={b['ceiling_J']}J")
        return False
    return True

def budget_add(joules):
    b = load_budget()
    b["spent_J"] = b.get("spent_J", 0.0) + (joules or 0.0)
    save_budget(b)

# ------------------------------------------------------------------
# Continuous logger
# ------------------------------------------------------------------
def cmd_log(interval=30):
    probe_tier()
    if PIDFILE.exists():
        try:
            old = int(PIDFILE.read_text().strip())
            os.kill(old, 0)
            print(f"logger already running (pid {old}). stop: hive log-stop")
            return
        except (ProcessLookupError, ValueError):
            pass
    PIDFILE.write_text(str(os.getpid()))
    say(f"continuous logger start interval={interval}s pid={os.getpid()}")
    def _stop(signum, frame):
        say("continuous logger stop")
        PIDFILE.unlink(missing_ok=True)
        sys.exit(0)
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    prev = None
    while True:
        s = sample_once()
        energy = None
        if prev and s["power_W"] is not None and prev.get("power_W") is not None:
            energy = 0.5 * (s["power_W"] + prev["power_W"]) * (s["t"] - prev["t"])
        ledger_append({"event": "joule_sample", "source": "continuous", **s, "energy_delta_J": energy})
        prev = s
        time.sleep(interval)

def cmd_log_stop():
    if not PIDFILE.exists():
        print("no logger pidfile")
        return
    try:
        pid = int(PIDFILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        print(f"sent SIGTERM to {pid}")
    except Exception as e:
        print(f"stop failed: {e}")
    PIDFILE.unlink(missing_ok=True)

# ------------------------------------------------------------------
# Task η
# ------------------------------------------------------------------
def cmd_eta(*cmd_parts):
    if not cmd_parts:
        print("usage: hive eta <command...>")
        return
    if not budget_check(1.0):
        return
    probe_tier()
    before = sample_once()
    t0 = time.time()
    try:
        proc = subprocess.run(cmd_parts, capture_output=True, text=True)
        rc, out, err = proc.returncode, (proc.stdout or "")[:400], (proc.stderr or "")[:200]
    except Exception as e:
        rc, out, err = -1, "", str(e)
    t1 = time.time()
    after = sample_once()
    dt = t1 - t0
    energy = 0.5 * (before.get("power_W") or 0) * (after.get("power_W") or 0) * dt if before.get("power_W") and after.get("power_W") else None
    if energy is None and before.get("power_W") and after.get("power_W"):
        energy = 0.5 * (before["power_W"] + after["power_W"]) * dt
    rec = {
        "event": "task_eta", "cmd": " ".join(cmd_parts), "returncode": rc,
        "duration_s": round(dt, 4), "energy_J": round(energy, 6) if energy else None,
        "power_before_W": before.get("power_W"), "power_after_W": after.get("power_W"),
        "stdout_head": out, "stderr_head": err,
    }
    ledger_append(rec)
    if energy:
        budget_add(energy)
    print(json.dumps(rec, indent=2))
    say(f"η-task {rec['cmd'][:50]} → {rec['energy_J']} J in {rec['duration_s']} s")

# ------------------------------------------------------------------
# Delegate to OptiPlex Qwen
# ------------------------------------------------------------------
def cmd_delegate(*prompt_parts):
    if not prompt_parts:
        print("usage: hive delegate <prompt text>")
        return
    prompt = " ".join(prompt_parts)
    if not budget_check(3.0):
        return
    if not spoke_alive():
        ledger_append({"event": "SPOKE_DOWN", "host": SPOKE_HOST, "port": SPOKE_PORT})
        say(f"SPOKE_DOWN {SPOKE_HOST}:{SPOKE_PORT}")
        return

    probe_tier()
    before = sample_once()
    t0 = time.time()

    payload = {
        "model": MODEL_ALIAS,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 1024,
        "stream": False,
    }
    data = json.dumps(payload).encode()
    req = Request(SPOKE_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode())
        text = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = body.get("usage", {})
        ok = True
        err = ""
    except Exception as e:
        text, usage, ok, err = "", {}, False, str(e)

    t1 = time.time()
    after = sample_once()
    dt = t1 - t0
    energy = None
    if before.get("power_W") is not None and after.get("power_W") is not None:
        energy = 0.5 * (before["power_W"] + after["power_W"]) * dt

    rec = {
        "event": "delegate",
        "prompt_head": prompt[:120],
        "ok": ok,
        "duration_s": round(dt, 4),
        "energy_J_phone": round(energy, 6) if energy else None,
        "power_before_W": before.get("power_W"),
        "power_after_W": after.get("power_W"),
        "tokens_in": usage.get("prompt_tokens"),
        "tokens_out": usage.get("completion_tokens"),
        "model": MODEL_ALIAS,
        "response_head": text[:300] if text else "",
        "error": err,
    }
    ledger_append(rec)
    if energy:
        budget_add(energy)

    print(json.dumps({k: rec[k] for k in ("ok", "duration_s", "energy_J_phone", "tokens_in", "tokens_out", "response_head", "error")}, indent=2))
    if text:
        print("\n----- response -----")
        print(text)
    say(f"delegate {'ok' if ok else 'FAIL'} {dt:.2f}s phone={energy}J tokens={usage.get('completion_tokens')}")

# ------------------------------------------------------------------
# Status / joule / ledger / budget
# ------------------------------------------------------------------
def cmd_status():
    probe_tier()
    tb = termux_battery()
    b = load_budget()
    print(json.dumps({
        "tier": _current_tier, "rish": _rish_ok,
        "spoke_alive": spoke_alive(),
        "budget": b,
        "termux_battery": tb,
        "ledgers": {"openroot": str(LEDGER), "une": str(UNE_LEDGER)},
    }, indent=2))
    ledger_append({"event": "status", "termux_battery": tb, "spoke_alive": spoke_alive()})

def cmd_probe():
    probe_tier()
    say(f"tier now {_current_tier}")
    if _rish_ok:
        for c in [
            "pm grant com.termux.api android.permission.WRITE_SECURE_SETTINGS",
            "pm grant com.termux.api android.permission.READ_LOGS",
            "dumpsys deviceidle whitelist +com.termux",
            "dumpsys deviceidle whitelist +com.termux.api",
            "cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow",
            "cmd appops set com.termux.api RUN_ANY_IN_BACKGROUND allow",
        ]:
            rish(c)
    cmd_status()

def cmd_joule(n=10, interval=1.0):
    if not budget_check(2.0):
        return
    probe_tier()
    samples, prev, total = [], None, 0.0
    for i in range(n):
        s = sample_once()
        energy = None
        if prev and s["power_W"] is not None and prev.get("power_W") is not None:
            energy = 0.5 * (s["power_W"] + prev["power_W"]) * (s["t"] - prev["t"])
            total += energy
        rec = {"event": "joule_sample", "i": i, **s, "energy_delta_J": energy}
        samples.append(rec)
        ledger_append(rec)
        prev = s
        time.sleep(interval)
    summary = {
        "event": "joule_window", "n": n, "interval_s": interval,
        "total_joules_approx": round(total, 4),
        "mean_power_W": round(sum(s["power_W"] for s in samples if s.get("power_W")) / max(1, len([s for s in samples if s.get("power_W")])), 4),
    }
    ledger_append(summary)
    budget_add(total)
    out = ARTIFACTS / f"joule_sample_{int(time.time())}.json"
    out.write_text(json.dumps({"samples": samples, "summary": summary}, indent=2))
    say(f"wrote {out} | total ≈ {summary['total_joules_approx']} J | mean ≈ {summary['mean_power_W']} W")

def cmd_ledger(n=12):
    if not LEDGER.exists():
        print("ledger empty")
        return
    for line in LEDGER.read_text().strip().splitlines()[-n:]:
        print(line)

def cmd_budget(*args):
    b = load_budget()
    if not args:
        print(json.dumps(b, indent=2))
        return
    if args[0] == "set" and len(args) > 1:
        b["ceiling_J"] = float(args[1])
        save_budget(b)
        say(f"budget ceiling set to {b['ceiling_J']} J")
    elif args[0] == "reset":
        b["spent_J"] = 0.0
        save_budget(b)
        say("budget spent reset to 0")
    else:
        print("usage: hive budget [set <joules> | reset]")

DISPATCH = {
    "status": cmd_status,
    "probe": cmd_probe,
    "joule": cmd_joule,
    "log": lambda: cmd_log(30),
    "log-stop": cmd_log_stop,
    "eta": lambda: cmd_eta(*sys.argv[2:]),
    "delegate": lambda: cmd_delegate(*sys.argv[2:]),
    "ledger": lambda: cmd_ledger(),
    "budget": lambda: cmd_budget(*sys.argv[2:]),
    "wake": lambda: (subprocess.run(["termux-wake-lock"], check=False), say("wake-lock")),
}

def main():
    if len(sys.argv) < 2:
        print("usage: hive <status|probe|joule|log|log-stop|eta|delegate|ledger|budget|wake>")
        print("  hive delegate <prompt>     # send to OptiPlex Qwen + measure phone joules")
        print("  hive budget set 50         # set session ceiling in joules")
        print("  hive budget reset")
        return
    cmd = sys.argv[1]
    if cmd in DISPATCH:
        DISPATCH[cmd]()
    else:
        say(f"unknown: {cmd}")

if __name__ == "__main__":
    main()
