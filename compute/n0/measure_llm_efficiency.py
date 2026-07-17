#!/data/data/com.termux/files/usr/bin/env python3
"""
measure_llm_efficiency.py — OpenRoot n0 unit
CONTRACT
  Wraps any command and emits structured metrics (wall time, CPU time, tokens, energy).
"""
import os, sys, json, time, subprocess, threading, argparse
from datetime import datetime

SYS_CUR = "/sys/class/power_supply/battery/current_now"
SYS_VOL = "/sys/class/power_supply/battery/voltage_now"

CURRENT_SIGN = -1
CUR_UNIT = 1e-6
VOL_UNIT = 1e-6

class PowerSampler(threading.Thread):
    def __init__(self, interval=0.2):
        super().__init__(daemon=True)
        self.interval = interval
        self.samples = []
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            t = time.monotonic()
            try:
                cur = int(open(SYS_CUR).read().strip())
                vol = int(open(SYS_VOL).read().strip())
                amps = CURRENT_SIGN * cur * CUR_UNIT
                volts = vol * VOL_UNIT
                self.samples.append((t, amps * volts))
            except Exception:
                pass
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()

    def energy_joules(self):
        if len(self.samples) < 2:
            return None
        e = 0.0
        for (t0, p0), (t1, p1) in zip(self.samples, self.samples[1:]):
            e += 0.5 * (p0 + p1) * (t1 - t0)
        return e

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-class", default="unknown")
    ap.add_argument("--model", default="unknown")
    ap.add_argument("--quant", default="Q4_K_M")
    ap.add_argument("--n-threads", type=int, default=2)
    ap.add_argument("--temp", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cold", action="store_true")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        print(json.dumps({"error": "No command provided"}))
        sys.exit(2)

    sampler = PowerSampler()
    sampler.start()

    t0 = time.monotonic()
    c0 = os.times()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    c1 = os.times()
    t1 = time.monotonic()
    sampler.stop()
    sampler.join(timeout=1)

    tok_in = tok_out = prefill_ms = decode_ms = None
    try:
        last_line = proc.stdout.strip().splitlines()[-1]
        payload = json.loads(last_line)
        tok_in = payload.get("prompt_eval_count")
        tok_out = payload.get("eval_count")
        prefill_ms = payload.get("prompt_eval_duration", 0) / 1e6
        decode_ms = payload.get("eval_duration", 0) / 1e6
    except Exception:
        pass

    wall_s = t1 - t0
    cpu_s = (c1.children_user - c0.children_user) + (c1.children_system - c0.children_system)
    energy_j = sampler.energy_joules()

    row = {
        "timestamp": datetime.now().isoformat(),
        "task_class": args.task_class,
        "model": args.model,
        "quant": args.quant,
        "n_threads": args.n_threads,
        "temp": args.temp,
        "seed": args.seed,
        "cold_load": args.cold,
        "wall_s": round(wall_s, 4),
        "cpu_s": round(cpu_s, 4),
        "energy_j": round(energy_j, 4) if energy_j else None,
        "tokens_in": tok_in,
        "tokens_out": tok_out,
        "prefill_ms": round(prefill_ms, 2) if prefill_ms else None,
        "decode_ms": round(decode_ms, 2) if decode_ms else None,
        "tok_per_s_decode": round(tok_out / (decode_ms / 1000), 2) if tok_out and decode_ms else None,
        "tok_per_joule": round(tok_out / energy_j, 2) if tok_out and energy_j else None,
        "returncode": proc.returncode,
        "node": "N0_measure_llm_efficiency"
    }
    print(json.dumps(row))

if __name__ == "__main__":
    main()
