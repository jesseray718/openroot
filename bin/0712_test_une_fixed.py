#!/usr/bin/env python3
import sys
import os

# Add the openroot directory to Python path
sys.path.insert(0, '/data/data/com.termux/files/home/openroot')

try:
    from une_client import UNEClient
    print("=== UNE Client Test ===")
    c = UNEClient()
    print('Health:', c.get_health())
    print('Resolve H003:', c.resolve_entity('H003-thermal-node-01'))
    print('ACRE gate thermal_work:', c.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work'))
    print('Batch:', c.batch_resolve(['une:001', 'H003-thermal-node-01']))
except ImportError as e:
    print(f"Import error: {e}")
    print("Available files in openroot:")
    os.system("ls -la /data/data/com.termux/files/home/openroot/*.py")
except Exception as e:
    print(f"Runtime error: {e}")
