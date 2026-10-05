import hashlib
import json
import sqlite3
import time
from enum import IntEnum

class ValidationTier(IntEnum):
    TIER_1_THEORETICAL = 1
    TIER_2_EMPIRICAL = 2
    TIER_3_PRODUCTION = 3

class KnowledgeBlockSchema:
    def __init__(self, artifact_type: str, title: str, author_id: str, payload: dict, dependencies: list = None):
        self.artifact_type = artifact_type  # code, bom, document, dataset, blueprint
        self.title = title
        self.author_id = author_id
        self.timestamp = time.time()
        self.payload = payload
        self.dependencies = dependencies or []
        self.tier = ValidationTier.TIER_1_THEORETICAL

    def compute_hash(self, prev_hash: str) -> str:
        block_data = {
            "prev_hash": prev_hash,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "author_id": self.author_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "dependencies": self.dependencies,
            "tier": int(self.tier)
        }
        raw_str = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

class KnowledgeLedger:
    def __init__(self, db_path="data/une_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_hash TEXT PRIMARY KEY,
                prev_hash TEXT,
                artifact_type TEXT,
                title TEXT,
                author_id TEXT,
                timestamp REAL,
                tier INTEGER,
                payload TEXT,
                dependencies TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_latest_hash(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT block_hash FROM blocks ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "0" * 64

    def append_block(self, block: KnowledgeBlockSchema) -> str:
        prev_hash = self.get_latest_hash()
        block_hash = block.compute_hash(prev_hash)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO blocks (block_hash, prev_hash, artifact_type, title, author_id, timestamp, tier, payload, dependencies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            block_hash,
            prev_hash,
            block.artifact_type,
            block.title,
            block.author_id,
            block.timestamp,
            int(block.tier),
            json.dumps(block.payload),
            json.dumps(block.dependencies)
        ))
        conn.commit()
        conn.close()
        return block_hash
