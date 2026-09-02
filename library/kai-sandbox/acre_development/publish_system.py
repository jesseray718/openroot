#!/usr/bin/env python3
"""
ACRE Multi-Platform Publishing System
Publishes to IPFS, Arweave, and Ethereum blockchain for maximum immutability
"""

import os
import json
import hashlib
import subprocess
from datetime import datetime
import base64

class ACREPublisher:
    def __init__(self):
        self.sources = {
            'ipfs': {'enabled': False, 'hash': None},
            'arweave': {'enabled': False, 'txid': None},
            'ethereum': {'enabled': False, 'txid': None},
            'filecoin': {'enabled': False, 'cid': None}
        }
        self.manifest = {}
        
    def check_dependencies(self):
        """Check if required tools are installed"""
        dependencies = {
            'ipfs': 'ipfs',
            'arweave': 'arweave',
            'ethereum': 'web3',
            'filecoin': 'lotus'
        }
        
        print("Checking dependencies...")
        for name, cmd in dependencies.items():
            try:
                if name == 'ethereum':
                    import web3
                    self.sources[name]['enabled'] = True
                else:
                    result = subprocess.run([cmd, '--version'],
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.sources[name]['enabled'] = True
            except:
                pass
        
        print(f"Available sources: {[k for k,v in self.sources.items() if v['enabled']]}")
        
    def create_manifest(self, content_path):
        """Create publication manifest"""
        with open(content_path, 'rb') as f:
            content = f.read()
        
        # Calculate hashes
        sha256_hash = hashlib.sha256(content).hexdigest()
        sha1_hash = hashlib.sha1(content).hexdigest()
        
        self.manifest = {
            'content_hash': sha256_hash,
            'content_size': len(content),
            'timestamp': datetime.utcnow().isoformat(),
            'sources': {},
            'metadata': {
                'type': 'ACRE Publication',
                'version': '1.0',
                'immutable': True
            }
        }
        
        return content
        
    def publish_to_ipfs(self, content):
        """Publish content to IPFS"""
        if not self.sources['ipfs']['enabled']:
            return None
            
        try:
            print("Publishing to IPFS...")
            result = subprocess.run(['ipfs', 'add', '-Q'],
                                 input=content,
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                cid = result.stdout.strip()
                self.sources['ipfs']['hash'] = cid
                self.manifest['sources']['ipfs'] = {
                    'cid': cid,
                    'url': f'https://ipfs.io/ipfs/{cid}',
                    'gateway': f'https://cloudflare-ipfs.com/ipfs/{cid}'
                }
                print(f"✅ IPFS Published: {cid}")
                return cid
        except Exception as e:
            print(f"❌ IPFS Error: {e}")
        
        return None
        
    def publish_to_arweave(self, content):
        """Publish content to Arweave"""
        if not self.sources['arweave']['enabled']:
            return None
            
        try:
            print("Publishing to Arweave...")
            # Save content to temp file
            with open('/tmp/acre_content.json', 'wb') as f:
                f.write(content)
            
            result = subprocess.run(['arweave', 'deploy', '/tmp/acre_content.json'],
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                txid = data.get('id')
                self.sources['arweave']['txid'] = txid
                self.manifest['sources']['arweave'] = {
                    'txid': txid,
                    'url': f'https://arweave.net/{txid}',
                    'viewblock': f'https://viewblock.io/arweave/tx/{txid}'
                }
                print(f"✅ Arweave Published: {txid}")
                return txid
        except Exception as e:
            print(f"❌ Arweave Error: {e}")
        
        return None
        
    def publish_to_ethereum(self, content_hash):
        """Publish content hash to Ethereum blockchain"""
        if not self.sources['ethereum']['enabled']:
            return None
            
        try:
            print("Publishing to Ethereum...")
            from web3 import Web3
            
            # Connect to Ethereum (using Infura or local node)
            w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_PROJECT_ID'))
            
            # Load account (in production, use proper key management)
            account = w3.eth.account.from_key('YOUR_PRIVATE_KEY')
            
            # Create transaction to store hash
            tx = {
                'to': '0x0000000000000000000000000000000000000000',  # Burn address
                'value': 0,
                'gas': 21000,
                'gasPrice': w3.to_wei('50', 'gwei'),
                'nonce': w3.eth.get_transaction_count(account.address),
                'data': content_hash.encode()
            }
            
            # Sign and send transaction
            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.sources['ethereum']['txid'] = tx_hash.hex()
            self.manifest['sources']['ethereum'] = {
                'txid': tx_hash.hex(),
                'url': f'https://etherscan.io/tx/{tx_hash.hex()}',
                'explorer': f'https://blockchain.com/eth/tx/{tx_hash.hex()}'
            }
            
            print(f"✅ Ethereum Published: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"❌ Ethereum Error: {e}")
        
        return None
        
    def publish_to_filecoin(self, content):
        """Publish content to Filecoin"""
        if not self.sources['filecoin']['enabled']:
            return None
            
        try:
            print("Publishing to Filecoin...")
            result = subprocess.run(['lotus', 'client', 'import', '/tmp/acre_content.json'],
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                cid = result.stdout.strip()
                self.sources['filecoin']['cid'] = cid
                self.manifest['sources']['filecoin'] = {
                    'cid': cid,
                    'url': f'https://filfox.io/ipfs/{cid}',
                    'explorer': f'https://filscan.io/tipset/cid/{cid}'
                }
                print(f"✅ Filecoin Published: {cid}")
                return cid
        except Exception as e:
            print(f"❌ Filecoin Error: {e}")
        
        return None
        
    def save_manifest(self):
        """Save publication manifest"""
        manifest_path = f"acre_publication_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        print(f"✅ Manifest saved: {manifest_path}")
        return manifest_path
        
    def publish_all(self, content_path):
        """Publish content to all available sources"""
        print("=== ACRE Multi-Platform Publisher ===")
        self.check_dependencies()
        
        # Create manifest and get content
        content = self.create_manifest(content_path)
        
        # Publish to all available sources
        self.publish_to_ipfs(content)
        self.publish_to_arweave(content)
        self.publish_to_ethereum(self.manifest['content_hash'])
        self.publish_to_filecoin(content)
        
        # Save final manifest
        self.save_manifest()
        
        print("\n=== Publication Complete ===")
        print(f"Content Hash: {self.manifest['content_hash']}")
        print(f"Published to: {[k for k,v in self.sources.items() if v.get('hash') or v.get('txid') or v.get('cid')]}")
        
        return self.manifest

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 publish_system.py <content_file>")
        sys.exit(1)
    
    publisher = ACREPublisher()
    publisher.publish_all(sys.argv[1])
