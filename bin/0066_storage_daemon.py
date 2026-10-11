#!/usr/bin/env python3
"""AgapeNet Storage Optimizer - VERIFIED FIX"""
import os, sys, time, hashlib, sqlite3, shutil, signal
from pathlib import Path

HOME = os.environ.get('HOME', '/data/data/com.termux/files/home')

class Daemon:
    def __init__(self, wd, sp, dp):
        self.wd = Path(wd)
        self.sp = Path(sp)
        self.dp = Path(dp)
        self.running = True
        for d in [str(self.wd), str(self.sp), str(self.dp).rsplit('/',1)[0]]:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def get_storage_info(self):
        try:
            stat = os.statvfs(self.wd)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            pct = ((total-free)/total)*100 if total > 0 else 0
            return {'usage_pct': pct, 'free_mb': free/(1024**2)}
        except Exception as e:
            return {'error': str(e)}
    
    def find_large_files(self, max_count=50, min_size=1024*1024):
        files = []
        for p in self.wd.rglob('*'):
            if p.is_file():
                try:
                    size = p.stat().st_size
                    if size >= min_size:
                        files.append((p, size))
                except: continue
        files.sort(key=lambda x: x[1], reverse=True)
        return [(f[0], f[1]) for f in files[:max_count]]
    
    def calc_hash(self, fp):
        h = hashlib.sha256()
        try:
            with open(fp, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    h.update(chunk)
            return h.hexdigest()
        except: return ""
    
    def compress_file(self, src, dest):
        try:
            import gzip
            with open(src, 'rb') as f_in:
                with gzip.open(dest, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return True
        except: return False
    
    def text_to_vector(self, text, vocab_size=100):
        words = text.lower().split()
        freq = {}
        for w in words:
            clean = ''.join(c for c in w if c.isalnum())
            if clean: freq[clean] = freq.get(clean, 0) + 1
        total = len(words) or 1
        top = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:vocab_size]
        return [freq.get(w, 0)/total for w in top]
    
    def init_db(self):
        conn = sqlite3.connect(str(self.dp))
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS files(
            id INTEGER PRIMARY KEY, original_path TEXT UNIQUE,
            sd_path TEXT, size_bytes INTEGER, hash_sha256 TEXT,
            compressed BOOLEAN, timestamp REAL, sync_status TEXT DEFAULT 'pending',
            vector_embedded BOOLEAN)''')
        conn.commit()
        conn.close()
    
    def add_record(self, orig, sd, size, hsh, comp, vec):
        conn = sqlite3.connect(str(self.dp))
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO files 
            (original_path, sd_path, size_bytes, hash_sha256, compressed, timestamp, sync_status, vector_embedded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (orig, sd, size, hsh, comp, time.time(), 'pending', vec))
        conn.commit()
        conn.close()
    
    def update_status(self, orig, status):
        conn = sqlite3.connect(str(self.dp))
        c = conn.cursor()
        c.execute('UPDATE files SET sync_status=? WHERE original_path=?', (status, orig))
        conn.commit()
        conn.close()
    
    def run_cycle(self):
        print(f"[{time.strftime('%H:%M:%S')}] Cycle starting...")
        info = self.get_storage_info()
        
        if 'error' in info:
            print(f"Storage check error: {info['error']}")
            return 0
        
        print(f"Storage: {info['usage_pct']:.1f}% used | Free: {info['free_mb']:.1f}MB")
        
        if info.get('usage_pct', 0) <= 98:
            print("✅ Storage OK, skipping")
            return 0
        
        files = self.find_large_files(20)
        if not files:
            print("⚠️ No files ≥1MB found")
            return 0
        
        print(f"Found {len(files)} files to process...")
        processed = 0
        
        for fp, size in files:
            try:
                file_hash = self.calc_hash(fp)
                if not file_hash: continue
                
                rel = fp.relative_to(self.wd)
                sd_raw = self.sp / "raw" / rel
                sd_gz = self.sp / "compressed" / (rel.stem + ".gz")
                
                sd_raw.parent.mkdir(parents=True, exist_ok=True)
                sd_gz.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(fp, sd_raw)
                print(f"📁 Copied: {fp.name}")
                
                comp = self.compress_file(fp, sd_gz)
                final = sd_gz if comp else sd_raw
                
                vec = False
                if fp.suffix.lower() in ['.txt','.md','.py','.json','.sql']:
                    try:
                        with open(fp, 'r', errors='ignore') as f:
                            v = self.text_to_vector(f.read(5000))
                        vec = True
                        print(f"🧮 Vector: {len(v)} dims")
                    except: pass
                
                self.add_record(str(fp), str(final), size, file_hash, comp, vec)
                self.update_status(str(fp), 'archived')
                processed += 1
                print(f"✅ Archived: {fp.name}")
                
            except Exception as e:
                print(f"❌ FAILED {fp.name}: {e}")
                continue
        
        print(f"\n🎯 Complete: {processed}/{len(files)} files")
        return processed
    
    def run(self):
        signal.signal(signal.SIGINT, lambda s,f: setattr(self, 'running', False))
        self.init_db()
        
        print("\n🔴 AgapeNet Storage Daemon Running")
        print(f"   Watch: {self.wd}")
        print(f"   Archive: {self.sp}")
        print(f"   Database: {self.dp}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n⚪ Stopping...")

if __name__ == "__main__":
    print("=== AgapeNet Storage Daemon ===\n")
    daemon = Daemon(f"{HOME}/agapenet/raw", "/sdcard/Download/agapenet_archive", f"{HOME}/agapenet/storage.db")
    daemon.run()
