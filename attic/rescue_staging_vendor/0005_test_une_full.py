#!/usr/bin/env python3
import threading
import time
import subprocess
import sys
sys.path.insert(0, '/home/workdir')  # adjust if needed
from une_server import app
from une_client import UNEClient, UNEConfig

def run_server():
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)  # allow Flask boot
    
    client = UNEClient(UNEConfig(base_url='http://127.0.0.1:5001/api/v1'))
    print("Health:", client.get_health())
    print("Resolve:", client.resolve_entity('H003-thermal-node-01'))
    print("ACRE gate:", client.validate_for_acre_claim('H003-thermal-node-01', 'thermal_work'))
    print("Full test complete. Server stub ready for une_protocol/ migration.")
