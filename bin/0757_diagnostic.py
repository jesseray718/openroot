#!/data/data/com.termux/files/usr/bin/env python3
import os
from datetime import datetime

PROJECT_ROOT = os.path.expanduser("~/AERO_ROOT")
PHOTO_DIR = os.path.join(PROJECT_ROOT, "04-PHYSICAL", "photos")
DOC_DIR = os.path.join(PROJECT_ROOT, "99-INBOX", "downloads")

print("🚀 STARTING AEROCENT SYSTEM DIAGNOSTIC...")
print(f"📍 Project Root: {PROJECT_ROOT}")
print("-" * 40)

# Check Photos
files = os.listdir(PHOTO_DIR) if os.path.exists(PHOTO_DIR) else []
print(f"📸 Photos Found: {len(files)}")
for f in files[:5]: print(f"   - {f}")

# Check Documents
docs = [f for f in os.listdir(DOC_DIR) if f.endswith(('.txt', '.md', '.pdf'))] if os.path.exists(DOC_DIR) else []
print(f"📄 Documents Found: {len(docs)}")
for d in docs[:5]: print(f"   - {d}")

# Generate Report
report_path = os.path.join(PROJECT_ROOT, "06-ARCHIVE", "daily_log.txt")
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "a") as log:
    log.write(f"\n=== LOG ENTRY: {datetime.now()} ===\n")
    log.write(f"Photos: {len(files)}\n")
    log.write(f"Docs: {len(docs)}\n")
    log.write("Status: System Organized. Ready for coding.\n")

print(f"✅ Log updated: {report_path}")
print("\n🏁 DIAGNOSTIC COMPLETE. You are ready to build!")
