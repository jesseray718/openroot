#!/usr/bin/env python3
"""
Mock UNE Server for testing UNEClient
Provides minimal endpoints for development/testing
"""

from flask import Flask, jsonify, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock database
mock_entities = {
    'une:001': {
        'id': 'une:001',
        'name': 'Test Entity 1',
        'type': 'test',
        'status': 'active'
    },
    'H003-thermal-node-01': {
        'id': 'H003-thermal-node-01',
        'name': 'Thermal Node 1',
        'type': 'thermal',
        'status': 'operational',
        'temperature': 25.5
    }
}

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'UNE Mock Server'})

@app.route('/api/v1/resolve/<entity_id>', methods=['GET'])
def resolve_entity(entity_id):
    entity = mock_entities.get(entity_id)
    if entity:
        return jsonify(entity)
    return jsonify({'error': 'Entity not found'}), 404

@app.route('/api/v1/conflict/<entity_id>', methods=['GET'])
def check_conflict(entity_id):
    # Mock conflict check - no conflicts for known entities
    if entity_id in mock_entities:
        return jsonify({'has_conflict': False, 'details': 'No conflicts detected'})
    return jsonify({'has_conflict': True, 'details': 'Unknown entity'}), 404

@app.route('/api/v1/entities', methods=['POST'])
def create_entity():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Invalid entity data'}), 400
    
    entity_id = data['id']
    mock_entities[entity_id] = data
    logger.info(f"Created mock entity: {entity_id}")
    return jsonify({'status': 'created', 'entity': data}), 201

if __name__ == '__main__':
    logger.info("Starting Mock UNE Server on http://127.0.0.1:5001")
    # Disable debug mode to avoid /dev/shm issues
    app.run(host='127.0.0.1', port=5001, debug=False)
