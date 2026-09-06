#!/usr/bin/env python3
"""
Final UNE System Demonstration
Shows complete workflow from entity creation to ACRE validation
"""

import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client_updated import UNEClient
import requests

print("=== UNE System Final Demonstration ===\n")

# Initialize client
client = UNEClient()
print(f"✅ Client initialized: {client.base_url}\n")

# 1. Check system health
health = client.get_health()
print(f"1. System Health: {'🟢 Healthy' if health else '🔴 Unhealthy'}\n")

# 2. Create a new entity
new_entity = {
    "id": "demo-thermal-node-02",
    "type": "thermal_node",
    "status": "active",
    "location": "demo_site",
    "capabilities": ["temperature", "humidity"]
}

print("2. Creating new entity:")
response = requests.post(f"{client.base_url}/entities", json=new_entity)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# 3. Resolve the new entity
entity = client.resolve_entity("demo-thermal-node-02")
print("3. Resolved new entity:")
print(f"   ID: {entity['id']}")
print(f"   Type: {entity['type']}")
print(f"   Status: {entity['status']}\n")

# 4. Check for conflicts
conflict = client.check_conflict("demo-thermal-node-02")
print("4. Conflict check:")
print(f"   Has conflict: {conflict['has_conflict']}")
print(f"   Details: {conflict['details']}\n")

# 5. Validate ACRE claim
validation = client.validate_for_acre_claim("demo-thermal-node-02", "thermal_work")
print("5. ACRE Claim Validation:")
print(f"   Entity: {validation['entity']['id']}")
print(f"   Approved: {'✅ YES' if validation['approved'] else '❌ NO'}")
print(f"   Reason: {validation['reason']}\n")

# 6. Batch operation
print("6. Batch Resolution:")
batch = client.batch_resolve([
    "demo-thermal-node-02",
    "H003-thermal-node-01",
    "nonexistent-entity"
])

for entity_id, result in batch.items():
    status = "✅ Found" if result else "❌ Not Found"
    print(f"   {entity_id}: {status}")

print("\n=== Demonstration Complete ===")
print("UNE system is fully operational and ready for OpenRoot integration!")
