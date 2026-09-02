#!/usr/bin/env python3
"""
Vector Explorer
Explore knowledge vectors interactively
"""

import json
from pathlib import Path

class VectorExplorer:
    def __init__(self, master_file='/root/HUMAN_CONTINUITY_MASTER_v1.0.txt'):
        self.master_file = Path(master_file)
        self.vectors = self._parse_master_file()
        self.domains = self._extract_domains()
        
    def _parse_master_file(self):
        """Parse master file into vector structure"""
        vectors = {}
        current_file = None
        current_vector = None
        
        with open(self.master_file) as f:
            for line in f:
                line = line.strip()
                
                # File section
                if line.startswith('[FILE:'):
                    current_file = line.split('[')[1].split(']')[0].split(':')[1]
                    continue
                    
                # Vector tag
                if '[V:' in line and ']' in line:
                    parts = line.split(']')
                    vector_part = parts[0] + ']'
                    
                    if '[V:' in vector_part and ']' in vector_part:
                        vector_id = vector_part.split(':')[1].split(']')[0]
                        current_vector = vector_id
                        
                        # Extract node type
                        node_type = 'N:0'
                        if '[N:' in line:
                            node_type = line.split('[N:')[1].split(']')[0]
                            
                        vectors[vector_id] = {
                            'id': vector_id,
                            'type': node_type,
                            'file': current_file,
                            'content': line
                        }
                        
        return vectors
        
    def _extract_domains(self):
        """Extract domain information"""
        domains = {}
        for vid, vec in self.vectors.items():
            # Simple domain detection
            content = vec['content'].lower()
            if 'water' in content:
                domains.setdefault('WATER', []).append(vid)
            elif 'fire' in content:
                domains.setdefault('FIRE', []).append(vid)
            elif 'shelter' in content:
                domains.setdefault('SHELTER', []).append(vid)
            elif 'food' in content:
                domains.setdefault('FOOD', []).append(vid)
            elif 'health' in content:
                domains.setdefault('HEALTH', []).append(vid)
                
        return domains
        
    def list_vectors(self, limit=20):
        """List vectors"""
        print(f"\nTotal vectors: {len(self.vectors)}")
        print("\nFirst vectors:")
        for i, (vid, vec) in enumerate(self.vectors.items()):
            if i >= limit:
                break
            print(f"  {vid}: {vec['type']} - {vec['content'][:60]}...")
            
    def get_vector(self, vector_id):
        """Get specific vector"""
        if vector_id not in self.vectors:
            print(f"Vector {vector_id} not found")
            return
            
        vec = self.vectors[vector_id]
        print(f"\nVector {vector_id}:")
        print(f"  Type: {vec['type']}")
        print(f"  File: {vec['file']}")
        print(f"  Content: {vec['content']}")
        
    def list_domain(self, domain):
        """List vectors in domain"""
        domain = domain.upper()
        if domain not in self.domains:
            print(f"Domain {domain} not found")
            return
            
        print(f"\nDomain {domain} ({len(self.domains[domain])} vectors):")
        for vid in self.domains[domain][:10]:  # Show first 10
            vec = self.vectors[vid]
            print(f"  {vid}: {vec['content'][:60]}...")
            
    def search(self, keyword):
        """Search for keyword"""
        keyword = keyword.lower()
        results = []
        
        for vid, vec in self.vectors.items():
            if keyword in vec['content'].lower():
                results.append((vid, vec))
                
        print(f"\nSearch results for '{keyword}' ({len(results)} found):")
        for vid, vec in results[:10]:  # Show first 10
            print(f"  {vid}: {vec['content'][:60]}...")
            
    def interactive(self):
        """Interactive mode"""
        print("\nVector Explorer - Interactive Mode")
        print("Commands: list, get <id>, domain <name>, search <term>, exit")
        
        while True:
            try:
                cmd = input("> ").strip().lower()
                
                if not cmd:
                    continue
                    
                if cmd == 'exit':
                    break
                    
                elif cmd == 'list':
                    self.list_vectors()
                    
                elif cmd.startswith('get '):
                    vector_id = cmd[4:].upper()
                    self.get_vector(vector_id)
                    
                elif cmd.startswith('domain '):
                    domain = cmd[7:]
                    self.list_domain(domain)
                    
                elif cmd.startswith('search '):
                    keyword = cmd[7:]
                    self.search(keyword)
                    
                else:
                    print("Unknown command. Try: list, get <id>, domain <name>, search <term>, exit")
                    
            except KeyboardInterrupt:
                break
                
        print("\nExiting Vector Explorer")

# Main
if __name__ == '__main__':
    explorer = VectorExplorer()
    explorer.interactive()
