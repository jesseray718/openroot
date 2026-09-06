"""Local persistent operation queue for the offline toolkit.

Operations are stored as newline-delimited JSON (JSONL) for simplicity,
durability, and human readability. Each entry carries an idempotency key
(idem_key) to prevent double-apply during sync replay.
"""
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OperationQueue:
    """Append-only, file-backed queue with idempotency and ordering."""

    def __init__(self, queue_file: str):
        self._path = Path(queue_file)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()

    # ------------------------------------------------------------------
    # Write side
    # ------------------------------------------------------------------

    def enqueue(
        self,
        op_type: str,
        payload: Any,
        urgency: float = 1.0,
        impact: float = 1.0,
        idem_key: Optional[str] = None,
    ) -> str:
        """Add an operation to the queue.  Returns the idem_key."""
        if idem_key is None:
            idem_key = str(uuid.uuid4())

        # Prevent re-queue of already-known idem_keys
        existing = {e["idem_key"] for e in self._load_all()}
        if idem_key in existing:
            logger.debug("Skipping duplicate idem_key=%s", idem_key)
            return idem_key

        entry = {
            "idem_key": idem_key,
            "op_type": op_type,
            "payload": payload,
            "urgency": urgency,
            "impact": impact,
            "status": "pending",
            "enqueued_at": time.time(),
        }
        with self._path.open("a") as fh:
            fh.write(json.dumps(entry) + "\n")
        logger.info("Enqueued op_type=%s idem_key=%s", op_type, idem_key)
        return idem_key

    # ------------------------------------------------------------------
    # Read side
    # ------------------------------------------------------------------

    def pending(self) -> List[Dict]:
        """Return pending entries ordered by priority (highest first)."""
        entries = [e for e in self._load_all() if e["status"] == "pending"]
        return sorted(entries, key=lambda e: e.get("_score", 0), reverse=True)

    def all_entries(self) -> List[Dict]:
        return self._load_all()

    def stats(self) -> Dict:
        entries = self._load_all()
        counts: Dict[str, int] = {}
        for e in entries:
            counts[e["status"]] = counts.get(e["status"], 0) + 1
        return {"total": len(entries), "by_status": counts}

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def mark_applied(self, idem_key: str) -> None:
        self._update_status(idem_key, "applied")

    def mark_failed(self, idem_key: str, reason: str = "") -> None:
        self._update_status(idem_key, "failed", extra={"fail_reason": reason})

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_all(self) -> List[Dict]:
        entries = []
        with self._path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.warning("Skipping malformed queue line")
        return entries

    def _update_status(self, idem_key: str, status: str, extra: Optional[Dict] = None) -> None:
        entries = self._load_all()
        updated = False
        for e in entries:
            if e["idem_key"] == idem_key:
                e["status"] = status
                if extra:
                    e.update(extra)
                updated = True
                break
        if not updated:
            logger.warning("idem_key=%s not found in queue", idem_key)
            return
        with self._path.open("w") as fh:
            for e in entries:
                fh.write(json.dumps(e) + "\n")
