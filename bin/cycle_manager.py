#!/usr/bin/env python3
"""
OpenRoot Cycle Manager v20260922
Handles save/resume cycles with REPO_NAME auto-detection
Path: /home/jesse/openroot/bin/cycle_manager.py
"""

import os
import sys
import json
import sqlite3
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

class CycleManager:
    def __init__(self, repo_name=None, base_path="/home/jesse/openroot"):
        # Auto-detect REPO_NAME if not provided
        self.REPO_NAME = repo_name or os.path.basename(os.getcwd())
        self.base_path = Path(base_path)
        self.data_dir = self.base_path / "data"
        self.context_bridge = self.base_path / "context_bridge"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.context_bridge.mkdir(parents=True, exist_ok=True)
        
        # Database path
        self.db_path = self.data_dir / "cycle_state.db"
        
        # Initialize database
        self._init_db()
        
        # Canary marker
        self.CANARY = f"CYCLEMGMT_V2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"[CYCLE] {self.CANARY}")
        print(f"[CYCLE] REPO_NAME={self.REPO_NAME}")
        print(f"[CYCLE] Base path: {self.base_path}")
    
    def _init_db(self):
        """Initialize SQLite database for cycle tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT UNIQUE,
                timestamp TEXT,
                state_data TEXT,
                checkpoint_pos TEXT,
                merkle_hash TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycle_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT,
                artifact_path TEXT,
                artifact_type TEXT,
                sha256 TEXT,
                FOREIGN KEY(cycle_id) REFERENCES cycles(cycle_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_cycle(self, cycle_id, state_data, checkpoint_pos="5,1"):
        """Save current cycle state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        merkle_hash = hashlib.sha256(
            f"{cycle_id}:{state_data}:{checkpoint_pos}".encode()
        ).hexdigest()
        
        timestamp = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO cycles 
                (cycle_id, timestamp, state_data, checkpoint_pos, merkle_hash, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            ''', (cycle_id, timestamp, state_data, checkpoint_pos, merkle_hash))
            
            conn.commit()
            
            # Log to context bridge
            log_file = self.context_bridge / f"cycle-{cycle_id}.md"
            with open(log_file, 'w') as f:
                f.write(f"# Cycle {cycle_id}\n")
                f.write(f"## Metadata\n")
                f.write(f"- Timestamp: {timestamp}\n")
                f.write(f"- Checkpoint Position: {checkpoint_pos}\n")
                f.write(f"- Merkle Hash: {merkle_hash}\n")
                f.write(f"\n## State Data\n{state_data}\n")
            
            print(f"[SAVE] Cycle {cycle_id} persisted")
            print(f"[SAVE] Checkpoint: {checkpoint_pos}")
            print(f"[exit=0]")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save cycle: {e}")
            return False
        finally:
            conn.close()
    
    def resume_cycle(self, cycle_id):
        """Resume from saved cycle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT state_data, checkpoint_pos, merkle_hash, status
            FROM cycles WHERE cycle_id = ?
        ''', (cycle_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            state_data, checkpoint_pos, merkle_hash, status = result
            print(f"[RESUME] Found cycle {cycle_id}")
            print(f"[RESUME] Checkpoint: {checkpoint_pos}")
            print(f"[RESUME] Status: {status}")
            return {
                'state_data': state_data,
                'checkpoint_pos': checkpoint_pos,
                'merkle_hash': merkle_hash,
                'status': status
            }
        else:
            print(f"[WARN] No saved cycle found for {cycle_id}")
            return None
    
    def list_cycles(self, status='active'):
        """List all cycles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cycle_id, timestamp, checkpoint_pos, status
            FROM cycles WHERE status = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (status,))
        
        results = cursor.fetchall()
        conn.close()
        
        print(f"[LIST] Active cycles ({len(results)} found):")
        for cycle_id, timestamp, checkpoint_pos, stat in results:
            print(f"  - {cycle_id}: {checkpoint_pos} ({timestamp[:19]})")
        
        return results
    
    def seal_cycle(self, cycle_id):
        """Mark cycle as complete/sealed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cycles SET status = 'sealed' WHERE cycle_id = ?
        ''', (cycle_id,))
        
        conn.commit()
        conn.close()
        
        print(f"[SEAL] Cycle {cycle_id} marked as sealed")
        return True

def main():
    """Main execution entry point"""
    manager = CycleManager()
    
    if len(sys.argv) < 2:
        print("[USAGE] cycle_manager.py <command> [args]")
        print("Commands: save, resume, list, seal")
        print(f"[exit=0]")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "save":
        cycle_id = sys.argv[2] if len(sys.argv) > 2 else f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state_data = sys.argv[3] if len(sys.argv) > 3 else "{}"
        checkpoint = sys.argv[4] if len(sys.argv) > 4 else "5,1"
        manager.save_cycle(cycle_id, state_data, checkpoint)
    
    elif command == "resume":
        cycle_id = sys.argv[2]
        result = manager.resume_cycle(cycle_id)
        if result:
            print(json.dumps(result, indent=2))
    
    elif command == "list":
        manager.list_cycles()
    
    elif command == "seal":
        cycle_id = sys.argv[2]
        manager.seal_cycle(cycle_id)
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)
    
    print(f"[exit=0]")

if __name__ == "__main__":
    main()
