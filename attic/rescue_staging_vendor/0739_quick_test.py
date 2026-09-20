#!/usr/bin/env python3
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

from une_client_updated import UNEClient

client = UNEClient()

print("=== Quick UNE Client Test ===")
print("Health check:", client.get_health())
print("Resolve H003:", client.resolve_entity('H003-thermal-node-01'))
print("ACRE validation:", client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work'))
print("Batch resolve:", client.batch_resolve(['H003-thermal-node-01', 'une:001']))
