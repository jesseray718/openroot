#!/usr/bin/env python3
"""FAST Termux Backup Daemon - No Waiting"""
import os, sys, time, hashlib, sqlite3, shutil, signal, gzip
from pathlib import Path

HOME = os.environ.get('HOME', '/data/data/com.termux/files/home')

class FastBackupDaemon:
    def __init__(self, source_dirs, archive_path, db_path):
        self.source_dirs = [Path(d) for d in source_dirs]
        self.archive_path = Path(archive_path)
        self.db_path = Path(db_path)
        self.running = True
        self.processed_count = 0
        
        for d in [self.archive_path, self.db_path.parent]:
            d.mkdir(parents=True, exist_ok=True)
    
    def get_storage_info(self):
        try:
            stat = os.statvfs(HOME)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            return {'free_mb': free/(1024**2), 'usage_pct': ((total-free)/total)*100}
        except: return {}
    
    def find_all_files(self):
        """Find ALL files regardless of size (min 1 byte!)"""
        files = []
        for source_dir in self.source_dirs:
            if not source_dir.exists(): continue
            for p in source_dir.rglob('*'):
                if p.is_file() and not p.is_symlink():
                    try:
                        size = p.stat().st_size
                        if size >= 1:  # Minimum 1 byte!
                            files.append((p, size, source_dir))
                    except: continue
        return files
    
    def calc_hash(self, fp):
        h = hashlib.sha256()
        try:
            with open(fp, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except: return ""
    
    def compress_file(self, src, dest):
        try:
            with open(src, 'rb') as f_in:
                with gzip.open(dest, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return True
        except: return False
    
    def init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS files(
            id INTEGER PRIMARY KEY, source_path TEXT UNIQUE,
            archive_path TEXT, size_bytes INTEGER, hash_sha256 TEXT,
            compressed BOOLEAN, timestamp REAL, status TEXT)''')
        conn.commit()
        conn.close()
    
    def backup_single_file(self, filepath, size, source_dir):
        try:
            rel_path = filepath.relative_to(source_dir)
            dest = self.archive_path / rel_path.with_suffix(rel_path.suffix + ".gz")
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if self.compress_file(filepath, dest):
                h = self.calc_hash(dest)
                conn = sqlite3.connect(str(self.db_path))
                c = conn.cursor()
                c.execute('''INSERT OR IGNORE INTO files 
                    (source_path, archive_path, size_bytes, hash_sha256, compressed, timestamp, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (str(filepath), str(dest), size, h, True, time.time(), 'completed'))
                conn.commit()
                conn.close()
                
                self.processed_count += 1
                if self.processed_count % 10 == 0:
                    print(f"Processed {self.processed_count} files...")
                return True
        except Exception as e:
            print(f"Failed {filepath.name}: {e}")
            return False
    
    def run_initial_scan(self):
        """RUN ONCE IMMEDIATELY - no waiting"""
        print("🔍 Scanning all files...")
        all_files = self.find_all_files()
        print(f"Found {len(all_files)} files to backup")
        
        backup_count = 0
        for filepath, size, source_dir in all_files:
            if not self.running: break
            self.backup_single_file(filepath, size, source_dir)
        
        print(f"\n✅ Initial backup complete: {backup_count} files")
        return len(all_files)
    
    def run_monitor_cycle(self):
        """Check for NEW files only (every 5 min)"""
        new_files = self.find_all_files()
        existing = set()
        
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute('SELECT source_path FROM files')
        for row in c.fetchall():
            existing.add(row[0])
        conn.close()
        
        for filepath, size, source_dir in new_files:
            if str(filepath) not in existing:
                self.backup_single_file(filepath, size, source_dir)
        
        return len(new_files)
    
    def run(self):
        signal.signal(signal.SIGINT, lambda s,f: setattr(self, 'running', False))
        self.init_db()
        
        print("\n⚡ FAST TERMUX BACKUP DAEMON")
        print(f"   Sources: {[str(p) for p in self.source_dirs]}")
        print(f"   Archive: {self.archive_path}")
        print(f"   Processing: ALL files (1 byte minimum)")
        print("Press Ctrl+C to stop\n")
        
        # FIRST: Run immediate scan (takes 10-30 seconds)
        print("🚀 RUNNING INITIAL SCAN NOW...\n")
        initial_count = self.run_initial_scan()
        
        # THEN: Monitor for new files (much faster)
        print("\n🔁 Monitoring for changes (every 5 min)...")
        try:
            while self.running:
                time.sleep(300)  # Only check every 5 minutes
                self.run_monitor_cycle()
        except KeyboardInterrupt:
            print("\n⚪ Stopping...")
            print(f"Total files backed up: {self.processed_count}")

if __name__ == "__main__":
    daemon = FastBackupDaemon(
        [HOME, f"{HOME}/.termux", f"{HOME}/agapenet"],
        "/sdcard/Download/termux_fast_backup",
        f"{HOME}/agapenet/fast_backup.db"
    )
    daemon.run()
