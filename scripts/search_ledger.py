import sqlite3
import json

class LedgerIndexer:
    def __init__(self, db_path="data/une_ledger.db"):
        self.db_path = db_path
        self._init_fts()

    def _init_fts(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS blocks_fts USING fts5(
                block_hash UNINDEXED,
                title,
                payload_text,
                artifact_type
            )
        ''')
        conn.commit()
        conn.close()

    def index_ledger(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT block_hash, title, payload, artifact_type FROM blocks")
        rows = cursor.fetchall()
        
        for row in rows:
            b_hash, title, payload_json, artifact_type = row
            try:
                payload_data = json.loads(payload_json)
                text_content = payload_data.get("content", "") + " " + json.dumps(payload_data.get("specs", {}))
            except:
                text_content = payload_json

            cursor.execute('''
                INSERT OR REPLACE INTO blocks_fts(block_hash, title, payload_text, artifact_type)
                VALUES (?, ?, ?, ?)
            ''', (b_hash, title, text_content, artifact_type))
        
        conn.commit()
        conn.close()

    def search_keyword(self, query: str, limit: int = 20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.block_hash, b.artifact_type, b.title, b.tier 
            FROM blocks_fts f
            JOIN blocks b ON f.block_hash = b.block_hash
            WHERE blocks_fts MATCH ? 
            ORDER BY rank 
            LIMIT ?
        ''', (query, limit))
        results = cursor.fetchall()
        conn.close()
        return results
