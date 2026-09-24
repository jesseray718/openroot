#!/data/data/com.termux/files/usr/bin/env python3
import time, csv, os
from datetime import datetime

LOG_FILE = os.path.expanduser("${HOME}/volumetric-project/pilot/sensor_log.csv")

def log_reading(t_hot, t_cold, rh_in, rh_out, flow, water_level, note=""):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), t_hot, t_cold, rh_in, rh_out, flow, water_level, note])
    print(f"Logged: {t_hot}°C hot, {t_cold}°C cold... Note: {note}")

if __name__ == "__main__":
    print("Example logger. For elevated data, run kai-mission-tools/example_elevated_telemetry.sh in aShell (Shizuku).")
    for i in range(3):
        log_reading(65.0 + i, 12.0, 45, 12, 0.018, 87, "phone proxy via Shizuku possible")
        time.sleep(2)
