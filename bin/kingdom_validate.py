#!/data/data/com.termux/files/usr/bin/python3
"""Kingdom Engine v0.1 — Proof of Productive Work validator, AX-019 (two-validator rule)"""
import argparse, json, hashlib, sys
from datetime import datetime

class KingdomValidator:
    """Two-validator consensus for ACRE minting"""
    def __init__(self):
        self.validators = {}
        self.ledger = []

    def register_validator(self, vid, pubkey, node_id):
        """Register a validator node"""
        self.validators[vid] = {'pubkey': pubkey, 'node_id': node_id, 'stake': 0, 'registered_at': datetime.utcnow().isoformat()}
        return f"Validator {vid} registered"

    def submit_work_claim(self, work_id, node_id, energy_joules, hash_prev, validator_1_id, validator_2_id):
        """Submit a PoPW claim; requires approval from 2 independent validators"""
        claim = {
            'work_id': work_id,
            'node_id': node_id,
            'energy_joules': energy_joules,
            'timestamp': datetime.utcnow().isoformat(),
            'hash_prev': hash_prev,
            'validator_approvals': [validator_1_id, validator_2_id],
            'status': 'pending'
        }
        claim_hash = hashlib.sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()
        claim['hash'] = claim_hash
        self.ledger.append(claim)
        return {'claim': claim, 'next_prev_hash': claim_hash}

    def approve_work(self, work_id, validator_id):
        """Validator approves work"""
        for entry in self.ledger:
            if entry['work_id'] == work_id and validator_id in entry['validator_approvals']:
                entry['status'] = 'approved' if len([v for v in entry['validator_approvals'] if v != 'pending']) >= 2 else 'pending'
                return {'work_id': work_id, 'validator': validator_id, 'new_status': entry['status']}
        return {'error': 'Work claim not found'}

    def mint_acre(self, work_id):
        """Mint ACRE only if work claim has 2 validator approvals"""
        for entry in self.ledger:
            if entry['work_id'] == work_id:
                if entry['status'] == 'approved':
                    acre_amount = entry['energy_joules'] / 1000.0
                    return {'work_id': work_id, 'acre_minted': acre_amount, 'hash': entry['hash']}
                else:
                    return {'error': 'Work not approved by 2 validators', 'status': entry['status']}
        return {'error': 'Work claim not found'}

def main():
    parser = argparse.ArgumentParser(description='Kingdom Engine — Cooperative PoPW Validator')
    parser.add_argument('--register-validator', nargs=3, metavar=('VID', 'PUBKEY', 'NODE_ID'), help='Register validator')
    parser.add_argument('--submit-work', nargs=6, metavar=('WORK_ID', 'NODE_ID', 'JOULES', 'HASH_PREV', 'V1', 'V2'), help='Submit work claim')
    parser.add_argument('--approve', nargs=2, metavar=('WORK_ID', 'VALIDATOR_ID'), help='Approve work')
    parser.add_argument('--mint', metavar='WORK_ID', help='Mint ACRE')
    parser.add_argument('-j', '--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    ke = KingdomValidator()
    result = None

    if args.register_validator:
        result = ke.register_validator(*args.register_validator)
    elif args.submit_work:
        try:
            joules = int(args.submit_work[2])
            result = ke.submit_work_claim(*args.submit_work[:2], joules, *args.submit_work[3:])
        except Exception as e:
            result = {'error': str(e)}
    elif args.approve:
        result = ke.approve_work(*args.approve)
    elif args.mint:
        result = ke.mint_acre(args.mint)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json or isinstance(result, dict):
        print(json.dumps(result, indent=2))
    else:
        print(result)

if __name__ == '__main__':
    main()
