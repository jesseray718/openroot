#!/usr/bin/env python3
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client_updated import UNEClient

print("=== ACRE Validation Workflow Tests ===")

client = UNEClient()

# Test 1: Valid entity
print("\n1. Valid Entity (H003-thermal-node-01):")
result = client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work')
print(f"   Approved: {result['approved']}")
print(f"   Reason: {result['reason']}")

# Test 2: Non-existent entity
print("\n2. Non-existent Entity:")
result = client.validate_for_acre_claim('nonexistent-entity', 'physical_work')
print(f"   Approved: {result['approved']}")
print(f"   Reason: {result['reason']}")

# Test 3: Different claim types
print("\n3. Different Claim Types:")
for claim_type in ['thermal_work', 'physical_work', 'documentation', 'software']:
    result = client.validate_for_acre_claim('H003-thermal-node-01', claim_type)
    print(f"   {claim_type}: {result['approved']} ({result['reason']})")

print("\n=== ACRE Workflow Tests Complete ===")
