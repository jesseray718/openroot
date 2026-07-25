#!/usr/bin/env python3
"""
Mesh Sync Tester
Test peer discovery and knowledge transfer
"""

import socket
import threading
import time
import json
import random
from pathlib import Path

class MeshTester:
    MULTICAST_GROUP = '224.1.1.1'
    MULTICAST_PORT = 5004
    
    def __init__(self, node_id):
        self.node_id = node_id
        self.peers = {}
        self.knowledge = self._load_knowledge()
        self.running = False
        
        # Create multicast socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.socket.bind(('', self.MULTICAST_PORT))
        
        # Join multicast group
        mreq = socket.inet_aton(self.MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
    def _load_knowledge(self):
        """Load test knowledge"""
        return {
            'V0001': 'Human Resilience Library',
            'V0002': 'Primitive Survival Fundamentals',
            'V0003': 'Modern Technology Pillars',
            'V0004': 'Fusion Protocol',
            'V0005': 'Complete Resilience System'
        }
        
    def start(self):
        """Start mesh tester"""
        self.running = True
        
        # Start listener
        listener = threading.Thread(target=self._listen, daemon=True)
        listener.start()
        
        # Start broadcaster
        broadcaster = threading.Thread(target=self._broadcast, daemon=True)
        broadcaster.start()
        
        print(f"Mesh tester {self.node_id} started")
        print(f"Knowledge available: {len(self.knowledge)} nodes")
        
    def stop(self):
        """Stop mesh tester"""
        self.running = False
        self.socket.close()
        
    def _listen(self):
        """Listen for messages"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                self._handle_message(data, addr)
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(1)
                
    def _broadcast(self):
        """Broadcast discovery messages"""
        while self.running:
            try:
                message = self._create_discovery()
                self.socket.sendto(message, (self.MULTICAST_GROUP, self.MULTICAST_PORT))
                time.sleep(5)
            except Exception as e:
                print(f"Broadcast error: {e}")
                time.sleep(2)
                
    def _create_discovery(self):
        """Create discovery message"""
        return json.dumps({
            'type': 'DISCOVERY',
            'from': self.node_id,
            'knowledge': len(self.knowledge),
            'timestamp': int(time.time())
        }).encode('utf-8')
        
    def _handle_message(self, data, addr):
        """Handle incoming message"""
        try:
            message = json.loads(data.decode('utf-8'))
            
            if message['type'] == 'DISCOVERY':
                peer_id = message['from']
                if peer_id != self.node_id:
                    self.peers[peer_id] = {
                        'addr': addr,
                        'last_seen': time.time(),
                        'knowledge': message['knowledge']
                    }
                    print(f"Discovered peer: {peer_id} with {message['knowledge']} knowledge nodes")
                    
                    # Simulate knowledge transfer
                    if random.random() < 0.3:  # 30% chance of transfer
                        self._transfer_knowledge(peer_id, addr)
                        
        except Exception as e:
            print(f"Message error: {e}")
            
    def _transfer_knowledge(self, peer_id, addr):
        """Simulate knowledge transfer"""
        # Select random knowledge node
        vector_id = random.choice(list(self.knowledge.keys()))
        knowledge = self.knowledge[vector_id]
        
        # Send knowledge
        message = json.dumps({
            'type': 'KNOWLEDGE',
            'from': self.node_id,
            'to': peer_id,
            'vector': vector_id,
            'data': knowledge,
            'timestamp': int(time.time())
        }).encode('utf-8')
        
        self.socket.sendto(message, addr)
        print(f"Transferred knowledge {vector_id} to {peer_id}")
        
    def status(self):
        """Show current status"""
        print(f"\nNode: {self.node_id}")
        print(f"Peers discovered: {len(self.peers)}")
        print(f"Knowledge nodes: {len(self.knowledge)}")
        print("\nDiscovered peers:")
        for peer_id, info in self.peers.items():
            print(f"  {peer_id}: {info['knowledge']} nodes, last seen {time.time() - info['last_seen']:.0f}s ago")

# Main
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 mesh_tester.py <node_id>")
        sys.exit(1)
        
    node_id = sys.argv[1]
    tester = MeshTester(node_id)
    
    try:
        tester.start()
        
        # Show status periodically
        while True:
            time.sleep(10)
            tester.status()
            
    except KeyboardInterrupt:
        tester.stop()
        print("\nMesh tester stopped")
