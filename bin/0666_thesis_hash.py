#!/data/data/com.termux/files/usr/bin/env python3
import hashlib
from datetime import datetime
THESIS = """CIVILIZATION 2.0 - THE THESIS
MISSION: Decentralize survival. Trash-to-Treasure. Open Source everything.
PHILOSOPHY: No Patents. No Monopolies. No Hierarchy."""
hash_value = hashlib.sha256(THESIS.encode('utf-8')).hexdigest()
print("="*50)
print("SHA-256 FINGERPRINT")
print("="*50)
print(f"\n{hash_value}\n")
print("Copy this into Exodus memo field")
print("="*50)
