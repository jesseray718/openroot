"""Content-hash deduplication index.

Uses SHA-256 to fingerprint arbitrary payloads.  Duplicate payloads store
only a reference to the first-seen canonical entry instead of re-storing
the full data.
"""
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _sha256(data: Any) -> str:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


class DedupIndex:
    """Persistent hash → canonical record index (JSON file)."""

    def __init__(self, index_file: str):
        self._path = Path(index_file)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, Dict] = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def put(self, payload: Any, record_id: Optional[str] = None) -> Tuple[str, bool]:
        """Store a payload if not already seen.

        Returns (content_hash, is_duplicate).
        If is_duplicate is True, only a reference is retained; caller
        should not re-store the payload.
        """
        h = _sha256(payload)
        if h in self._index:
            # Record a reference hit
            self._index[h]["ref_count"] = self._index[h].get("ref_count", 1) + 1
            self._save()
            logger.debug("Duplicate detected hash=%s", h)
            return h, True

        entry: Dict = {
            "hash": h,
            "record_id": record_id or h[:16],
            "ref_count": 1,
            "first_seen": time.time(),
        }
        self._index[h] = entry
        self._save()
        logger.info("New record stored hash=%s", h)
        return h, False

    def get(self, content_hash: str) -> Optional[Dict]:
        """Return index metadata for a known hash, or None."""
        return self._index.get(content_hash)

    def contains(self, payload: Any) -> bool:
        return _sha256(payload) in self._index

    def stats(self) -> Dict:
        total = len(self._index)
        refs = sum(e.get("ref_count", 1) for e in self._index.values())
        deduped = refs - total
        return {"total_canonical": total, "total_references": refs, "deduped_savings": deduped}

    def remove(self, content_hash: str) -> bool:
        """Remove an entry from the index (used during purge)."""
        if content_hash in self._index:
            del self._index[content_hash]
            self._save()
            return True
        return False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self._path.exists() and self._path.stat().st_size > 0:
            try:
                with self._path.open() as fh:
                    self._index = json.load(fh)
            except (json.JSONDecodeError, OSError):
                logger.warning("Could not load dedup index – starting fresh")
                self._index = {}

    def _save(self) -> None:
        with self._path.open("w") as fh:
            json.dump(self._index, fh, indent=2)
