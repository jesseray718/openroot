#!/usr/bin/env python3
"""
UNEClient v0.2 — agape-une governance interface for OpenRoot
Resolves entities, checks axiom conflicts, gates ACRE claims.
Termux/A15 + kai9000 native. Logs to stdout for Shizuku capture.
"""

import os
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [UNE] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class UNEConfig:
    base_url: str = field(default_factory=lambda: os.getenv('UNE_BASE_URL', 'http://127.0.0.1:5001/api/v1'))
    timeout: int = field(default_factory=lambda: int(os.getenv('UNE_TIMEOUT', '10')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('UNE_RETRIES', '3')))

class UNEError(Exception):
    """Base exception for UNE layer failures."""
    pass

class UNEClient:
    def __init__(self, config: Optional[UNEConfig] = None):
        self.config = config or UNEConfig()
        self.session = requests.Session()
        retries = Retry(
            total=self.config.max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        logger.info(f"UNEClient initialized -> {self.config.base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        url = f"{self.config.base_url}{endpoint}"
        try:
            resp = self.session.request(method, url, timeout=self.config.timeout, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 404:
                logger.warning(f"Entity not found: {endpoint}")
                return None
            else:
                logger.error(f"UNE API error {resp.status_code}: {resp.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network/UNE failure: {e}")
            raise UNEError(f"Request failed: {e}") from e

    def resolve_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Resolve UNE entity by ID (e.g. une:001, H003-thermal-node-01)."""
        return self._request('GET', f'/resolve/{entity_id}')

    def check_conflict(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Check for axiom conflicts (AX-039 shield, nomenclature clashes)."""
        return self._request('GET', f'/conflict/{entity_id}')

    def get_health(self) -> bool:
        """Service health gate."""
        try:
            status = self._request('GET', '/health')
            return status is not None and status.get('status') == 'healthy'
        except Exception:
            return False

    def create_entity(self, entity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create/register new UNE entity (POST stub for nomenclature extension)."""
        return self._request('POST', '/entities', json=entity_data)

    def validate_for_acre_claim(self, entity_id: str, claim_type: str = "physical_work") -> Dict[str, Any]:
        """
        ACRE gate: resolve + conflict check before mint claim.
        Returns dict with 'approved', 'reason', 'entity'.
        Ties directly to tokens/src/acre_validator.py flow.
        """
        if not self.get_health():
            return {"approved": False, "reason": "UNE service unhealthy", "entity": None}

        entity = self.resolve_entity(entity_id)
        if not entity:
            return {"approved": False, "reason": f"Entity {entity_id} not resolved in UNE", "entity": None}

        conflict = self.check_conflict(entity_id)
        if conflict and conflict.get('has_conflict', False):
            return {
                "approved": False,
                "reason": f"AXIOM CONFLICT: {conflict.get('details', 'Unknown')}",
                "entity": entity
            }

        logger.info(f"ACRE claim gate PASSED for {entity_id} ({claim_type})")
        return {"approved": True, "reason": "No conflicts, entity resolved", "entity": entity}

    def batch_resolve(self, entity_ids: List[str]) -> Dict[str, Any]:
        """Batch resolve for multi-entity PoPW verification."""
        results = {}
        for eid in entity_ids:
            results[eid] = self.resolve_entity(eid)
        return results

if __name__ == '__main__':
    client = UNEClient()
    print("=== UNEClient v0.2 SELF-TEST ===")
    print("Health:", client.get_health())
    print("Resolve une:001:", client.resolve_entity('une:001'))
    print("Conflict une:001:", client.check_conflict('une:001'))
    print("ACRE gate test (H003-thermal-01):", client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work'))
    print("Batch test:", client.batch_resolve(['une:001', 'H003-thermal-node-01']))
