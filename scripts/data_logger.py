#!/usr/bin/env python3
"""H-003 Thermal Cascade Data Logger -- 30-day JSONL collection for v1.0 validation."""
import json, time, datetime, os, csv
from pathlib import Path

LOG_DIR = Path.home() / ".local" / "share" / "openroot" / "h003-logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
JSONL_FILE = LOG_DIR / "h003-30day.jsonl"
CSV_FILE = LOG_DIR / "h003-30day.csv"

# Sensor channel config -- replace mock with real sensors when hardware arrives
CHANNELS = {
    "panel_surface": {"unit": "C", "min": -20, "max": 120},
    "labyrinth_inlet": {"unit": "C", "min": -20, "max": 80},
    "labyrinth_outlet": {"unit": "C", "min": -20, "max": 80},
    "hot_battery": {"unit": "C", "min": -20, "max": 95},
    "cold_battery": {"unit": "C", "min": -20, "max": 60},
    "ambient_air": {"unit": "C", "min": -40, "max": 60},
    "teg_hot_junction": {"unit": "C", "min": -20, "max": 150},
    "teg_cold_junction": {"unit": "C", "min": -40, "max": 60},
    "teg_output_mv": {"unit": "mV", "min": 0, "max": 5000},
    "airflow_cfm": {"unit": "CFM", "min": 0, "max": 200},
}

def mock_reading(channel):
    """Simulate realistic values for testing. Replace with sensor reads."""
    import random
    cfg = CHANNELS[channel]
    mid = (cfg["min"] + cfg["max"]) / 2
    span = (cfg["max"] - cfg["min"]) / 6
    return round(mid + random.gauss(0, span), 2)

def take_reading(use_mock=True):
    ts = datetime.datetime.now().isoformat()
    reading = {"timestamp": ts, "day": None, "channels": {}}
    for ch in CHANNELS:
        reading["channels"][ch] = mock_reading(ch) if use_mock else None
    return reading

def calc_metrics(reading):
    """Derive key thermal cascade metrics from raw readings."""
    ch = reading["channels"]
    delta_t_panel_ambient = ch["panel_surface"] - ch["ambient_air"]
    delta_t_labyrinth = ch["labyrinth_inlet"] - ch["labyrinth_outlet"]
    delta_t_battery = ch["hot_battery"] - ch["cold_battery"]
    delta_t_teg = ch["teg_hot_junction"] - ch["teg_cold_junction"]
    teg_power_w = (ch["teg_output_mv"] / 1000) ** 2 / 10  # Assume 10 ohm load
    reading["metrics"] = {
        "delta_t_panel_ambient": round(delta_t_panel_ambient, 2),
        "delta_t_labyrinth": round(delta_t_labyrinth, 2),
        "delta_t_battery": round(delta_t_battery, 2),
        "delta_t_teg": round(delta_t_teg, 2),
        "teg_power_w": round(teg_power_w, 4),
        "energy_collected_wh": 0,  # Calculated in aggregation
    }
    return reading

def log_reading(reading):
    with open(JSONL_FILE, "a") as f:
        f.write(json.dumps(reading) + "\n")
    with open(CSV_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if f.tell() == 0:
            header = ["timestamp"] + list(CHANNELS.keys()) + \
                     ["delta_t_panel_ambient", "delta_t_labyrinth", "delta_t_battery", "delta_t_teg", "teg_power_w"]
            w.writerow(header)
        row = [reading["timestamp"]] + [reading["channels"][c] for c in CHANNELS] + \
              [reading["metrics"]["delta_t_panel_ambient"], reading["metrics"]["delta_t_labyrinth"],
               reading["metrics"]["delta_t_battery"], reading["metrics"]["delta_t_teg"],
               reading["metrics"]["teg_power_w"]]
        w.writerow(row)

def daily_summary(day_num):
    """Aggregate the last 24h of readings into a daily summary."""
    readings = []
    if not JSONL_FILE.exists():
        return None
    with open(JSONL_FILE) as f:
        for line in f:
            readings.append(json.loads(line.strip()))
    if not readings:
        return None
    today = datetime.date.today().isoformat()
    today_readings = [r for r in readings if r["timestamp"][:10] == today]
    if not today_readings:
        return None
    summary = {"date": today, "day": day_num, "count": len(today_readings)}
    for ch in CHANNELS:
        vals = [r["channels"][ch] for r in today_readings]
        summary[f"{ch}_avg"] = round(sum(vals) / len(vals), 2)
        summary[f"{ch}_max"] = max(vals)
        summary[f"{ch}_min"] = min(vals)
    # Energy estimate: sum of TEG power * hours
    total_teg_wh = sum(r["metrics"]["teg_power_w"] for r in today_readings) * (24 / max(len(today_readings), 1))
    summary["estimated_teg_energy_wh"] = round(total_teg_wh, 2)
    summary_file = LOG_DIR / f"day-{day_num:02d}-summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    return summary

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="H-003 Thermal Cascade Data Logger")
    p.add_argument("command", choices=["log", "summary", "status", "export"])
    p.add_argument("--day", type=int, default=1, help="Day number for summary")
    p.add_argument("--interval", type=int, default=300, help="Seconds between readings (default 300)")
    args = p.parse_args()

    if args.command == "log":
        print(f"H-003 Data Logger: starting (interval={args.interval}s)")
        print(f"Logging to: {JSONL_FILE}")
        print("Press Ctrl+C to stop")
        day_count = 1
        while True:
            reading = take_reading(use_mock=True)
            reading["day"] = day_count
            reading = calc_metrics(reading)
            log_reading(reading)
            print(f"[{reading['timestamp']}] T_panel={reading['channels']['panel_surface']}C "
                  f"dT_teg={reading['metrics']['delta_t_teg']}C "
                  f"P_teg={reading['metrics']['teg_power_w']}W")
            time.sleep(args.interval)

    elif args.command == "summary":
        s = daily_summary(args.day)
        if s:
            print(json.dumps(s, indent=2))
        else:
            print("No data for that day yet")

    elif args.command == "status":
        count = 0
        if JSONL_FILE.exists():
            with open(JSONL_FILE) as f:
                count = sum(1 for _ in f)
        print(f"Total readings logged: {count}")
        print(f"Log file: {JSONL_FILE}")
        print(f"CSV file: {CSV_FILE}")
        print(f"Days elapsed: {count // 288 if count else 0}")

    elif args.command == "export":
        print(f"CSV export at: {CSV_FILE}")
        print(f"JSONL export at: {JSONL_FILE}")
        print("These files are ready for IPFS/Zenodo publication")
