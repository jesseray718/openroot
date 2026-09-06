"""Data lifecycle management: soft-delete, retention policy, and hard-purge.

Lifecycle events are recorded to an append-only JSONL ledger so that
purge operations are auditable.
"""
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DataLifecycle:
    """Manages soft-delete, retention windows, and hard-purge for local data."""

    def __init__(self, lifecycle_file: str, soft_delete_retention_days: int = 30):
        self._path = Path(lifecycle_file)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()
        self.retention_days = soft_delete_retention_days

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def soft_delete(self, record_id: str, reason: str = "") -> None:
        """Mark a record as deleted; data is retained until retention window expires."""
        self._append_event(
            {
                "event": "soft_delete",
                "record_id": record_id,
                "reason": reason,
                "deleted_at": time.time(),
                "purge_after": (
                    datetime.now(timezone.utc) + timedelta(days=self.retention_days)
                ).timestamp(),
            }
        )
        logger.info("Soft-deleted record_id=%s reason=%s", record_id, reason)

    def purge_eligible(self) -> List[Dict]:
        """Return records whose retention window has expired."""
        now = time.time()
        seen: Dict[str, Dict] = {}
        for event in self._load_events():
            rid = event.get("record_id", "")
            if event["event"] == "soft_delete":
                seen[rid] = event
            elif event["event"] in ("hard_purge", "restore"):
                seen.pop(rid, None)
        return [e for e in seen.values() if e.get("purge_after", 0) <= now]

    def hard_purge(self, record_id: str, confirmed: bool = False) -> bool:
        """Permanently remove a record from the lifecycle ledger.

        ``confirmed`` must be True to actually execute; this acts as a
        safety gate for non-interactive callers.
        """
        if not confirmed:
            logger.warning(
                "hard_purge called without confirmed=True for record_id=%s – skipped",
                record_id,
            )
            return False
        self._append_event(
            {
                "event": "hard_purge",
                "record_id": record_id,
                "purged_at": time.time(),
            }
        )
        logger.info("Hard-purged record_id=%s", record_id)
        return True

    def restore(self, record_id: str) -> None:
        """Cancel a soft-delete before retention expires."""
        self._append_event({"event": "restore", "record_id": record_id, "restored_at": time.time()})
        logger.info("Restored record_id=%s", record_id)

    def stats(self) -> Dict:
        eligible = self.purge_eligible()
        events = self._load_events()
        soft_count = sum(1 for e in events if e["event"] == "soft_delete")
        purge_count = sum(1 for e in events if e["event"] == "hard_purge")
        return {
            "total_events": len(events),
            "soft_deleted": soft_count,
            "hard_purged": purge_count,
            "eligible_for_purge": len(eligible),
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _append_event(self, event: Dict) -> None:
        with self._path.open("a") as fh:
            fh.write(json.dumps(event) + "\n")

    def _load_events(self) -> List[Dict]:
        events = []
        with self._path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.warning("Skipping malformed lifecycle line")
        return events
