#!/usr/bin/env python3
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client_updated import UNEClient

print("=== Full UNE Client-Server Integration Test ===")

client = UNEClient()

# Test 1: Health Check
print("\n1. Health Check:")
health = client.get_health()
print(f"   Healthy: {health}")

# Test 2: Entity Resolution
print("\n2. Entity Resolution:")
entities_to_test = ['H003-thermal-node-01', 'une:001', 'nonexistent-entity']
for entity_id in entities_to_test:
    entity = client.resolve_entity(entity_id)
    print(f"   {entity_id}: {'Found' if entity else 'Not Found'}")

# Test 3: Conflict Checking
print("\n3. Conflict Checking:")
conflict = client.check_conflict('H003-thermal-node-01')
print(f"   H003 conflict: {conflict}")

# Test 4: ACRE Claim Validation
print("\n4. ACRE Claim Validation:")
validation = client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work')
print(f"   Approved: {validation.get('approved')}")
print(f"   Reason: {validation.get('reason')}")
if validation.get('entity'):
    print(f"   Entity: {validation['entity']['id']}")

# Test 5: Batch Resolution
print("\n5. Batch Resolution:")
batch = client.batch_resolve(['H003-thermal-node-01', 'une:001', 'missing-entity'])
for entity_id, result in batch.items():
    print(f"   {entity_id}: {'Found' if result else 'Not Found'}")

print("\n=== Integration Test Complete ===")
