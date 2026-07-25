#!/usr/bin/env python3
import time, math, json
from datetime import datetime

class RatchetDutyCycle:
    def __init__(self, period=1.5, duty=0.38, asymmetry=0.72):
        self.period = period
        self.duty = max(0.12, min(0.55, duty))
        self.asymmetry = asymmetry
        self.state = "OFF"
        self.cycle_start = time.time()
        self.total_on = 0.0
        self.total_off = 0.0
        self._last_trans = time.time()

    def update(self):
        now = time.time()
        elapsed = (now - self.cycle_start) % self.period
        on_time = self.period * self.duty
        new_state = "ON" if elapsed < on_time else "OFF"
        if new_state != self.state:
            if new_state == "ON":
                self.total_off += now - self._last_trans
            else:
                self.total_on += now - self._last_trans
            self._last_trans = now
            self.state = new_state
        return self.state

    def report(self):
        total = self.total_on + self.total_off
        actual = self.total_on / total if total > 0 else 0
        return {
            "state": self.state,
            "target_duty": round(self.duty, 3),
            "actual_duty": round(actual, 3),
            "ts": datetime.now().isoformat(timespec="seconds")
        }

if __name__ == "__main__":
    r = RatchetDutyCycle()
    try:
        for _ in range(30):
            print(r.update(), r.report())
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped")
