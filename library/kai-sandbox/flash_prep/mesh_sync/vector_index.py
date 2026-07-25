#!/usr/bin/env python3
"""
Vector Index Manager for Mesh Sync Protocol
Manages the knowledge graph and sync operations
"""

import json
import hashlib
import base64
from pathlib import Path

class VectorIndex:
    def __init__(self, index_file='vector_index.json'):
        self.index_file = Path(index_file)
        self.index = self._load_index()
        self.dirty = False
        
    def _load_index(self):
        """Load vector index from file"""
        if not self.index_file.exists():
            return {
                'version': '1.0',
                'updated': None,
                'vectors': {},
                'domains': {}
            }
        with open(self.index_file) as f:
            return json.load(f)
        
    def save(self):
        """Save vector index to file"""
        if not self.dirty:
            return
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
        self.dirty = False
        
    def add_vector(self, vector_id, node_type, domain, title, data):
        """Add or update a vector in the index"""
        data_hash = self._hash_data(data)
        data_size = len(data)
        
        self.index['vectors'][vector_id] = {
            'type': node_type,
            'domain': domain,
            'title': title,
            'size': data_size,
            'hash': data_hash,
            'access': 0  # Default access level
        }
        
        # Add to domain index
        if domain not in self.index['domains']:
            self.index['domains'][domain] = {'nodes': []}
        if vector_id not in self.index['domains'][domain]['nodes']:
            self.index['domains'][domain]['nodes'].append(vector_id)
            
        self.dirty = True
        return data_hash
        
    def get_vector(self, vector_id):
        """Get vector information"""
        return self.index['vectors'].get(vector_id)
        
    def have_vector(self, vector_id):
        """Check if vector exists in index"""
        return vector_id in self.index['vectors']
        
    def get_domain_vectors(self, domain):
        """Get all vectors for a domain"""
        if domain not in self.index['domains']:
            return []
        return self.index['domains'][domain]['nodes']
        
    def get_range(self, start_id, end_id):
        """Get all vectors in a range"""
        vectors = []
        for vid in sorted(self.index['vectors'].keys()):
            if start_id <= vid <= end_id:
                vectors.append(vid)
        return vectors
        
    def _hash_data(self, data):
        """Create SHA-256 hash of data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
        
    def verify_data(self, vector_id, data):
        """Verify data matches index hash"""
        vec = self.get_vector(vector_id)
        if not vec:
            return False
        return self._hash_data(data) == vec['hash']
        
    def get_sync_offer(self, request_range='0001-0678', domains=None):
        """Generate sync offer based on request"""
        offer = {
            'ranges': [],
            'domains': domains or []
        }
        
        # Handle range request
        if request_range:
            start, end = request_range.split('-')
            available = self.get_range(start, end)
            if available:
                offer['ranges'].append(f"{available[0]}-{available[-1]}")
                
        # Handle domain request
        if domains:
            offer['domains'] = []
            for domain in domains:
                if domain in self.index['domains']:
                    offer['domains'].append(domain)
                    
        return offer

# Example usage
if __name__ == '__main__':
    # Create index
    vi = VectorIndex()
    
    # Add some vectors
    vi.add_vector('0001', 'N:1', 'ROOT', 'Human Resilience Library', 'Content...')
    vi.add_vector('0002', 'N:2', 'ROOT', 'Purpose', 'To preserve...')
    
    # Save index
    vi.save()
    
    print(f"Index created with {len(vi.index['vectors'])} vectors")
