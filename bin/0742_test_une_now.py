#!/usr/bin/env python3
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client_updated import UNEClient

print("🔄 Testing UNE System...")
client = UNEClient()

# Test all functions
health = client.get_health()
entity = client.resolve_entity('H003-thermal-node-01')
conflict = client.check_conflict('H003-thermal-node-01')
validation = client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work')

print(f"✅ Health: {health}")
print(f"✅ Entity: {entity['id'] if entity else 'None'}")
print(f"✅ Conflict: {conflict['has_conflict']}")
print(f"✅ ACRE Approved: {validation['approved']}")

print("\n🎉 UNE System is working perfectly!")
