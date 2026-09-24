#!/usr/bin/env python3
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client import UNEClient

print("=== Comprehensive UNE Client Test ===")

# Create client
client = UNEClient()

# Test all methods
print("\n1. Health Check:")
health = client.get_health()
print(f"   Result: {health} (False expected without server)")

print("\n2. Entity Resolution:")
entity = client.resolve_entity('H003-thermal-node-01')
print(f"   Result: {entity}")

print("\n3. Conflict Check:")
conflict = client.check_conflict('H003-thermal-node-01')
print(f"   Result: {conflict}")

print("\n4. ACRE Claim Validation:")
validation = client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work')
print(f"   Approved: {validation.get('approved')}")
print(f"   Reason: {validation.get('reason')}")

print("\n5. Batch Resolution:")
batch = client.batch_resolve(['une:001', 'H003-thermal-node-01'])
print(f"   Results: {batch}")

print("\n=== Test Complete ===")
