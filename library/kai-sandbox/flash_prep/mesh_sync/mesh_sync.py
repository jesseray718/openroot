#!/usr/bin/env python3
"""
Mesh Sync Protocol Implementation
Decentralized knowledge synchronization
"""

import json
import socket
import threading
import time
from pathlib import Path
from .vector_index import VectorIndex

class MeshSyncNode:
    MULTICAST_GROUP = '224.1.1.1'
    MULTICAST_PORT = 5004
    DISCOVERY_INTERVAL = 15
    SYNC_INTERVAL = 60
    
    def __init__(self, device_id, data_dir='data'):
        self.device_id = device_id
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.vector_index = VectorIndex()
        self.peers = {}
        self.trust_scores = {}
        self.running = False
        
        # Create multicast socket
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        # Bind to port
        self.multicast_socket.bind(('', self.MULTICAST_PORT))
        
        # Join multicast group
        mreq = socket.inet_aton(self.MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
    def start(self):
        """Start mesh sync node"""
        self.running = True
        
        # Start listener thread
        listener_thread = threading.Thread(target=self._listen, daemon=True)
        listener_thread.start()
        
        # Start discovery thread
        discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        discovery_thread.start()
        
        # Start sync thread
        sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        sync_thread.start()
        
        print(f"Mesh sync node {self.device_id} started")
        
    def stop(self):
        """Stop mesh sync node"""
        self.running = False
        self.multicast_socket.close()
        self.vector_index.save()
        
    def _listen(self):
        """Listen for multicast messages"""
        while self.running:
            try:
                data, addr = self.multicast_socket.recvfrom(1024)
                self._handle_message(data, addr)
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(1)
                
    def _discovery_loop(self):
        """Periodically broadcast discovery messages"""
        while self.running:
            try:
                message = self._create_discovery_message()
                self._broadcast(message)
                time.sleep(self.DISCOVERY_INTERVAL)
            except Exception as e:
                print(f"Discovery error: {e}")
                time.sleep(5)
                
    def _sync_loop(self):
        """Periodically initiate sync with peers"""
        while self.running:
            try:
                if self.peers:
                    for peer_id, peer_info in list(self.peers.items()):
                        self._initiate_sync(peer_id)
                time.sleep(self.SYNC_INTERVAL)
            except Exception as e:
                print(f"Sync error: {e}")
                time.sleep(10)
                
    def _create_discovery_message(self):
        """Create discovery broadcast message"""
        return json.dumps({
            'type': 'DISCOVERY',
            'from': self.device_id,
            'timestamp': int(time.time()),
            'capabilities': {
                'vectors': len(self.vector_index.index['vectors']),
                'domains': list(self.vector_index.index['domains'].keys())
            }
        }).encode('utf-8')
        
    def _broadcast(self, message):
        """Broadcast message to multicast group"""
        self.multicast_socket.sendto(message, (self.MULTICAST_GROUP, self.MULTICAST_PORT))
        
    def _handle_message(self, data, addr):
        """Handle incoming message"""
        try:
            message = json.loads(data.decode('utf-8'))
            
            if message['type'] == 'DISCOVERY':
                self._handle_discovery(message, addr)
                
            elif message['type'] == 'SYNC_REQUEST':
                self._handle_sync_request(message, addr)
                
            elif message['type'] == 'SYNC_OFFER':
                self._handle_sync_offer(message, addr)
                
            elif message['type'] == 'CHUNK':
                self._handle_chunk(message, addr)
                
            elif message['type'] == 'ACK':
                self._handle_ack(message, addr)
                
        except Exception as e:
            print(f"Message handling error: {e}")
            
    def _handle_discovery(self, message, addr):
        """Handle discovery message from peer"""
        peer_id = message['from']
        
        # Update peer info
        self.peers[peer_id] = {
            'addr': addr,
            'last_seen': time.time(),
            'capabilities': message['capabilities']
        }
        
        print(f"Discovered peer: {peer_id} with {message['capabilities']['vectors']} vectors")
        
    def _initiate_sync(self, peer_id):
        """Initiate sync with peer"""
        if peer_id not in self.peers:
            return
            
        # Create sync request
        request = {
            'type': 'SYNC_REQUEST',
            'from': self.device_id,
            'timestamp': int(time.time()),
            'range': '0001-0678',  # Full range for now
            'domains': ['WATER', 'FIRE', 'SHELTER', 'FOOD', 'HEALTH']
        }
        
        peer_addr = self.peers[peer_id]['addr']
        self._send_direct(peer_addr, json.dumps(request).encode('utf-8'))
        
    def _handle_sync_request(self, request, addr):
        """Handle sync request from peer"""
        # Generate sync offer
        offer = self.vector_index.get_sync_offer(
            request_range=request.get('range'),
            domains=request.get('domains')
        )
        
        # Send offer
        response = {
            'type': 'SYNC_OFFER',
            'from': self.device_id,
            'to': request['from'],
            'timestamp': int(time.time()),
            'offer': offer
        }
        
        self._send_direct(addr, json.dumps(response).encode('utf-8'))
        
    def _handle_sync_offer(self, offer, addr):
        """Handle sync offer from peer"""
        # For now, accept all offered vectors
        needed = []
        for v_range in offer['offer'].get('ranges', []):
            start, end = v_range.split('-')
            for vid in self.vector_index.get_range(start, end):
                if not self.vector_index.have_vector(vid):
                    needed.append(vid)
                    
        # Request needed vectors
        if needed:
            request = {
                'type': 'GET',
                'from': self.device_id,
                'to': offer['from'],
                'vectors': needed
            }
            self._send_direct(addr, json.dumps(request).encode('utf-8'))
            
    def _send_direct(self, addr, message):
        """Send direct message to peer"""
        # For simplicity, use same socket for now
        # In production, would use separate socket
        self.multicast_socket.sendto(message, addr)
        
    def _handle_chunk(self, chunk, addr):
        """Handle data chunk from peer"""
        vector_id = chunk['vector']
        data = base64.b64decode(chunk['data'])
        
        # Verify hash
        if self.vector_index.verify_data(vector_id, data):
            # Save data
            self._save_vector_data(vector_id, data)
            
            # Send ACK
            ack = {
                'type': 'ACK',
                'from': self.device_id,
                'to': chunk['from'],
                'vector': vector_id,
                'hash': chunk['hash']
            }
            self._send_direct(addr, json.dumps(ack).encode('utf-8'))
            
    def _save_vector_data(self, vector_id, data):
        """Save vector data to file"""
        vec_file = self.data_dir / f"v_{vector_id}.dat"
        with open(vec_file, 'wb') as f:
            f.write(data)
            
        # Update index if needed
        vec_info = self.vector_index.get_vector(vector_id)
        if not vec_info:
            # Extract metadata from data
            # For now, just mark as present
            pass
            
    def _handle_ack(self, ack, addr):
        """Handle acknowledgment from peer"""
        # Update trust score
        peer_id = ack['from']
        self.trust_scores[peer_id] = self.trust_scores.get(peer_id, 0) + 1
        
        print(f"Received ACK from {peer_id} for vector {ack['vector']}")

# Example usage
if __name__ == '__main__':
    # Create node
    node = MeshSyncNode('node-001')
    
    # Start node
    node.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.stop()
