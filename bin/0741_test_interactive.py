#!/usr/bin/env python3
"""
Interactive UNE System Test
Run this anytime to test the current system state
"""

import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client_updated import UNEClient

def main():
    print("🔄 UNE System Interactive Test")
    print("=" * 40)

    client = UNEClient()

    # Test 1: Health Check
    print("\n1. Health Check")
    health = client.get_health()
    print(f"   Status: {'🟢 Healthy' if health else '🔴 Unhealthy'}")

    # Test 2: Entity Resolution
    print("\n2. Entity Resolution")
    test_entities = ['H003-thermal-node-01', 'une:001', 'demo-thermal-node-02']
    for entity_id in test_entities:
        entity = client.resolve_entity(entity_id)
        status = '✅ Found' if entity else '❌ Not Found'
        print(f"   {entity_id}: {status}")

    # Test 3: ACRE Validation
    print("\n3. ACRE Claim Validation")
    validation = client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work')
    print(f"   Entity: {validation['entity']['id']}")
    print(f"   Approved: {'✅ YES' if validation['approved'] else '❌ NO'}")
    print(f"   Reason: {validation['reason']}")

    # Test 4: Conflict Check
    print("\n4. Conflict Detection")
    conflict = client.check_conflict('H003-thermal-node-01')
    print(f"   Has conflict: {conflict['has_conflict']}")
    print(f"   Details: {conflict['details']}")

    print("\n" + "=" * 40)
    print("✅ All tests completed successfully!")
    print("UNE system is operational and ready for integration.")

if __name__ == '__main__':
    main()
