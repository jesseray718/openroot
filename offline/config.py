"""Configuration loader for the offline toolkit.

Reads from environment variables (or .env file if python-dotenv is available)
with safe, offline-friendly defaults.
"""
import os
import json
from pathlib import Path

# Attempt to load .env; silently skip if dotenv not installed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), ".openroot", "offline")


def load_config() -> dict:
    """Return the merged offline-toolkit configuration dict."""
    data_dir = os.environ.get("OFFLINE_DATA_DIR", DEFAULT_DATA_DIR)
    cfg = {
        # Storage
        "data_dir": data_dir,
        "queue_file": os.path.join(data_dir, "queue.jsonl"),
        "dedup_index_file": os.path.join(data_dir, "dedup_index.json"),
        "lifecycle_file": os.path.join(data_dir, "lifecycle.jsonl"),
        # Retention (days)
        "soft_delete_retention_days": int(
            os.environ.get("OFFLINE_SOFT_DELETE_RETENTION_DAYS", "30")
        ),
        # Priority scoring weights: score = urgency^2 * impact * weight_u * weight_i
        "priority_weight_urgency": float(
            os.environ.get("OFFLINE_PRIORITY_WEIGHT_URGENCY", "1.0")
        ),
        "priority_weight_impact": float(
            os.environ.get("OFFLINE_PRIORITY_WEIGHT_IMPACT", "1.0")
        ),
        # Thermal / resource regulation
        "thermal_cpu_high_threshold": float(
            os.environ.get("OFFLINE_THERMAL_CPU_HIGH", "80.0")
        ),
        "thermal_cpu_low_threshold": float(
            os.environ.get("OFFLINE_THERMAL_CPU_LOW", "40.0")
        ),
        "thermal_max_concurrency": int(
            os.environ.get("OFFLINE_THERMAL_MAX_CONCURRENCY", "4")
        ),
        # Sync
        "sync_endpoint": os.environ.get("OFFLINE_SYNC_ENDPOINT", ""),
    }

    # Allow a local JSON override file
    override_file = os.path.join(data_dir, "config.json")
    if os.path.exists(override_file):
        with open(override_file) as fh:
            overrides = json.load(fh)
        cfg.update(overrides)

    # Ensure data_dir exists
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return cfg
