#!/usr/bin/env python3
"""
ACRE Coin Simulator
Simulate ACRE coin economy
"""

import json
import time
from pathlib import Path

class ACRESimulator:
    def __init__(self, node_id='node-001'):
        self.node_id = node_id
        self.ledger_file = Path(f'acre_ledger_{node_id}.json')
        self.ledger = self._load_ledger()
        
    def _load_ledger(self):
        """Load transaction ledger"""
        if not self.ledger_file.exists():
            return {
                'node_id': self.node_id,
                'balance': 1000,  # Initial balance
                'transactions': [],
                'timestamp': int(time.time())
            }
        
        with open(self.ledger_file) as f:
            return json.load(f)
            
    def save(self):
        """Save ledger to file"""
        self.ledger['timestamp'] = int(time.time())
        with open(self.ledger_file, 'w') as f:
            json.dump(self.ledger, f, indent=2)
            
    def mint(self, amount):
        """Mint new ACRE coins"""
        amount = int(amount)
        self.ledger['balance'] += amount
        
        transaction = {
            'type': 'mint',
            'amount': amount,
            'timestamp': int(time.time()),
            'notes': 'New ACRE minted'
        }
        
        self.ledger['transactions'].append(transaction)
        self.save()
        
        print(f"Minted {amount} ACRE. New balance: {self.ledger['balance']}")
        
    def transfer(self, to_node, amount):
        """Transfer ACRE to another node"""
        amount = int(amount)
        
        if amount > self.ledger['balance']:
            print(f"Insufficient balance. Current: {self.ledger['balance']}, needed: {amount}")
            return
            
        self.ledger['balance'] -= amount
        
        transaction = {
            'type': 'transfer',
            'to': to_node,
            'amount': amount,
            'timestamp': int(time.time()),
            'notes': f'Transfer to {to_node}'
        }
        
        self.ledger['transactions'].append(transaction)
        self.save()
        
        print(f"Transferred {amount} ACRE to {to_node}. New balance: {self.ledger['balance']}")
        
    def balance(self):
        """Show current balance"""
        print(f"Current balance: {self.ledger['balance']} ACRE")
        
    def ledger(self):
        """Show transaction history"""
        print(f"\nTransaction history for {self.node_id}:")
        for tx in self.ledger['transactions']:
            print(f"  {tx['timestamp']}: {tx['type']} {tx.get('amount', 0)} ACRE")
            if tx['type'] == 'transfer':
                print(f"    -> to {tx['to']}")
                
    def interactive(self):
        """Interactive mode"""
        print(f"\nACRE Simulator - Node {self.node_id}")
        print("Commands: mint <amount>, transfer <node> <amount>, balance, ledger, exit")
        
        while True:
            try:
                cmd = input("> ").strip().lower()
                
                if not cmd:
                    continue
                    
                if cmd == 'exit':
                    break
                    
                elif cmd == 'balance':
                    self.balance()
                    
                elif cmd == 'ledger':
                    self.ledger()
                    
                elif cmd.startswith('mint '):
                    amount = cmd[5:]
                    self.mint(amount)
                    
                elif cmd.startswith('transfer '):
                    parts = cmd[9:].split()
                    if len(parts) == 2:
                        to_node, amount = parts
                        self.transfer(to_node, amount)
                    else:
                        print("Usage: transfer <node_id> <amount>")
                        
                else:
                    print("Unknown command. Try: mint <amount>, transfer <node> <amount>, balance, ledger, exit")
                    
            except KeyboardInterrupt:
                break
                
        print("\nExiting ACRE Simulator")
        self.save()

# Main
if __name__ == '__main__':
    import sys
    
    node_id = sys.argv[1] if len(sys.argv) > 1 else 'node-001'
    simulator = ACRESimulator(node_id)
    simulator.interactive()
