#!/data/data/com.termux/files/usr/bin/python3
"""First H-003 PoPW demo — Kingdom Engine (AX-019) + ACRE mint"""
import json, hashlib, sys
from datetime import datetime

class KingdomValidator:
    def __init__(self):
        self.validators = {}
        self.ledger = []

    def register_validator(self, vid, pubkey, node_id):
        self.validators[vid] = {'pubkey': pubkey, 'node_id': node_id, 'registered_at': datetime.utcnow().isoformat()}
        return f"Validator {vid} registered"

    def submit_work_claim(self, work_id, node_id, energy_joules, hash_prev, v1, v2):
        claim = {
            'work_id': work_id,
            'node_id': node_id,
            'energy_joules': energy_joules,
            'timestamp': datetime.utcnow().isoformat(),
            'hash_prev': hash_prev,
            'validator_approvals': [v1, v2],
            'status': 'pending'
        }
        claim['hash'] = hashlib.sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()
        self.ledger.append(claim)
        return claim

    def approve_work(self, work_id, validator_id):
        for entry in self.ledger:
            if entry['work_id'] == work_id:
                if validator_id in entry['validator_approvals']:
                    approved = [v for v in entry['validator_approvals'] if v != 'pending']
                    if len(approved) >= 2:
                        entry['status'] = 'approved'
                    return {'work_id': work_id, 'validator': validator_id, 'new_status': entry['status']}
        return {'error': 'not found'}

    def mint_acre(self, work_id):
        for entry in self.ledger:
            if entry['work_id'] == work_id and entry['status'] == 'approved':
                acre = entry['energy_joules'] / 1000.0
                return {'work_id': work_id, 'acre_minted': acre, 'hash': entry['hash'], 'joules': entry['energy_joules']}
        return {'error': 'not approved or not found'}

ke = KingdomValidator()

# Demo values (H-003 12m² nightly theoretical)
work_id = "h003_night_20260717_001"
node_id = "DV.MSH.VP.ND00"
joules = 46476000  # \~12.91 kWh * 3.6e6 J
hash_prev = "0000000000000000"
v1, v2 = "ND00", "ND01"

print(ke.register_validator("ND00", "pubkey_nd00", node_id))
print(ke.register_validator("ND01", "pubkey_nd01", "DV.MSH.VP.ND01"))

claim = ke.submit_work_claim(work_id, node_id, joules, hash_prev, v1, v2)
print("SUBMITTED:", json.dumps(claim, indent=2))

print(ke.approve_work(work_id, "ND00"))
print(ke.approve_work(work_id, "ND01"))

minted = ke.mint_acre(work_id)
print("MINTED:", json.dumps(minted, indent=2))

result = {
    'deployment': 'agape_v0.1.0',
    'work_id': work_id,
    'une_code': node_id,
    'joules': joules,
    'acre_minted': minted.get('acre_minted'),
    'status': minted.get('error') or 'success',
    'timestamp': datetime.utcnow().isoformat(),
    'axioms': ['AX-019', 'AX-032']
}

with open('$HOME/projects/openroot/research/first_pypw_claim.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\nResult saved to research/first_pypw_claim.json")
print(json.dumps(result, indent=2))
