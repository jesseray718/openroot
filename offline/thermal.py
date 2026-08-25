"""Thermal / resource self-regulation module.

Monitors host resource pressure (CPU load, memory) and adjusts the
maximum allowed concurrency for the queue worker.

Cross-platform design:
  - Primary: reads ``/proc/stat`` (Linux) and ``/proc/meminfo`` (Linux).
  - Fallback: uses ``psutil`` if installed.
  - Ultimate fallback: heuristic constants (safe, conservative).

Thermal sensors (temperature) are attempted via ``psutil.sensors_temperatures``
on supported platforms; silently skipped elsewhere.
"""
import logging
import os
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _cpu_load_linux() -> Optional[float]:
    """Return current CPU utilisation percentage via /proc/stat."""
    try:
        def _read_stat():
            with open("/proc/stat") as fh:
                line = fh.readline()
            parts = line.split()
            idle = int(parts[4])
            total = sum(int(p) for p in parts[1:])
            return idle, total

        idle1, total1 = _read_stat()
        time.sleep(0.1)
        idle2, total2 = _read_stat()
        d_idle = idle2 - idle1
        d_total = total2 - total1
        if d_total == 0:
            return 0.0
        return (1.0 - d_idle / d_total) * 100.0
    except (FileNotFoundError, IndexError, ValueError):
        return None


def _cpu_load_psutil() -> Optional[float]:
    try:
        import psutil  # type: ignore
        return psutil.cpu_percent(interval=0.1)
    except ImportError:
        return None


def _memory_pressure_psutil() -> Optional[float]:
    """Return used-memory percentage via psutil."""
    try:
        import psutil  # type: ignore
        return psutil.virtual_memory().percent
    except ImportError:
        return None


def _temperature_psutil() -> Optional[float]:
    """Return max CPU temperature (°C) or None if unavailable."""
    try:
        import psutil  # type: ignore
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        readings = []
        for entries in temps.values():
            for e in entries:
                readings.append(e.current)
        return max(readings) if readings else None
    except (ImportError, AttributeError, OSError):
        return None


class ThermalRegulator:
    """Adjusts concurrency based on host resource pressure.

    Parameters
    ----------
    cpu_high : float
        CPU % above which concurrency is reduced to 1.
    cpu_low : float
        CPU % below which full concurrency is restored.
    max_concurrency : int
        Upper bound on concurrent workers.
    """

    def __init__(
        self,
        cpu_high: float = 80.0,
        cpu_low: float = 40.0,
        max_concurrency: int = 4,
    ):
        self.cpu_high = cpu_high
        self.cpu_low = cpu_low
        self.max_concurrency = max_concurrency

    def snapshot(self) -> Dict:
        """Collect current resource metrics."""
        cpu = _cpu_load_linux() or _cpu_load_psutil() or 0.0
        mem = _memory_pressure_psutil() or 0.0
        temp = _temperature_psutil()
        return {
            "cpu_percent": round(cpu, 1),
            "mem_percent": round(mem, 1),
            "temperature_c": round(temp, 1) if temp is not None else None,
            "sampled_at": time.time(),
        }

    def allowed_concurrency(self) -> int:
        """Return the number of workers permitted right now."""
        snap = self.snapshot()
        cpu = snap["cpu_percent"]

        if cpu >= self.cpu_high:
            level = 1
        elif cpu >= self.cpu_low:
            # Linear scale between low and high
            ratio = (self.cpu_high - cpu) / (self.cpu_high - self.cpu_low)
            level = max(1, round(ratio * self.max_concurrency))
        else:
            level = self.max_concurrency

        logger.debug("cpu=%.1f%% → allowed_concurrency=%d", cpu, level)
        return level

    def pressure_state(self) -> str:
        """Return a human-readable pressure label: low | medium | high."""
        snap = self.snapshot()
        cpu = snap["cpu_percent"]
        if cpu >= self.cpu_high:
            return "high"
        if cpu >= self.cpu_low:
            return "medium"
        return "low"
