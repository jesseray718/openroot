#!/usr/bin/env python3
import sys
import time
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client import UNEClient

# Wait a moment for server to be ready
time.sleep(1)

print("=== Testing UNE Client with Server ===")
client = UNEClient()

# Test health
health = client.get_health()
print(f"Health check: {health}")

if health:
    # Test entity resolution
    print("\nTesting entity resolution:")
    entity = client.resolve_entity('H003-thermal-node-01')
    print(f"H003-thermal-node-01: {entity}")

    # Test conflict check
    conflict = client.check_conflict('H003-thermal-node-01')
    print(f"Conflict check: {conflict}")

    # Test ACRE validation
    validation = client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work')
    print(f"ACRE validation: {validation}")

    # Test batch
    batch = client.batch_resolve(['une:001', 'H003-thermal-node-01'])
    print(f"Batch resolve: {batch}")
else:
    print("Server not healthy - check server logs")
