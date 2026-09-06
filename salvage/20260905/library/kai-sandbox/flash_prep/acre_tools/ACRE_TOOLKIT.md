# ACRE COIN TOOLKIT
*Tools for testing mesh sync and ACRE integration*

## Quick Start

### 1. Install Toolkit
```bash
# On any Linux system (including Ubuntu on Dell 3040)
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git curl wget -y
pip3 install cryptography qrcode[pil] numpy
```

### 2. Set Up Environment
```bash
# Create workspace
mkdir -p ~/acre_workspace
cd ~/acre_workspace

# Copy tools from flash drive
cp -r /media/flash_drive/acre_tools/* .

# Initialize
python3 init_toolkit.py
```

## Core Tools

### 1. Mesh Sync Tester
```bash
# Start mesh node
python3 mesh_tester.py node-001

# On second device:
python3 mesh_tester.py node-002

# Devices will automatically discover and sync
```

### 2. Vector Explorer
```bash
# Explore knowledge vectors
python3 vector_explorer.py

# Commands:
# - list: Show all vectors
# - get V0001: Get specific vector
# - domain WATER: Show domain vectors
# - search fire: Search content
```

### 3. ACRE Coin Simulator
```bash
# Start ACRE simulator
python3 acre_simulator.py

# Commands:
# - mint 100: Mint 100 ACRE
# - transfer node-002 50: Transfer 50 ACRE
# - balance: Show balance
# - ledger: Show transaction history
```

### 4. Physics Engine
```bash
# Run physics simulations
python3 physics_engine.py

# Commands:
# - gravity: Test gravitational models
# - energy: Test energy systems
# - materials: Test material properties
```

## Tool Descriptions

### 1. Mesh Sync Tester
- Tests peer discovery
- Simulates knowledge transfer
- Measures sync performance
- Validates data integrity

### 2. Vector Explorer
- Browse all 632 knowledge vectors
- Search by domain or keyword
- Extract specific knowledge nodes
- Export to various formats

### 3. ACRE Coin Simulator
- Mint and transfer ACRE coins
- View transaction ledger
- Test economic models
- Simulate governance

### 4. Physics Engine
- Test gravitational physics
- Simulate energy systems
- Model material properties
- Validate scientific principles

## Testing Workflow

### Step 1: Mesh Sync Test
1. Start two nodes
2. Verify discovery
3. Test knowledge transfer
4. Measure sync speed

### Step 2: Knowledge Exploration
1. List all vectors
2. Extract key domains
3. Search for specific topics
4. Export useful knowledge

### Step 3: ACRE Integration
1. Mint initial ACRE coins
2. Transfer between nodes
3. Test governance models
4. Simulate economic scenarios

### Step 4: Physics Validation
1. Test gravitational models
2. Validate energy systems
3. Model material properties
4. Document results

## ACRE Coin Integration

### Economic Model
```
ACRE Coin = Knowledge + Energy + Governance

Value derived from:
- Knowledge preservation
- Energy production
- Community governance
- Scientific validation
```

### Governance Model
```
1. Knowledge Stewards - Preserve wisdom
2. Energy Producers - Generate power
3. Physics Validators - Ensure accuracy
4. Community Members - Participate equally
```

### Integration Plan
```
Phase 1: Knowledge Preservation
- Document all primitive and modern knowledge
- Create vector index
- Establish mesh sync network

Phase 2: Energy Systems
- Build renewable energy sources
- Create energy credits
- Link to ACRE coin

Phase 3: Governance
- Establish community rules
- Create decision making process
- Implement ACRE voting

Phase 4: Physics Validation
- Test scientific principles
- Validate energy systems
- Document results
- Share with community
```

## Quick Reference

### Common Commands
```bash
# Start mesh node
python3 mesh_tester.py my-node-id

# Explore vectors
python3 vector_explorer.py

# Run ACRE simulator
python3 acre_simulator.py

# Test physics
python3 physics_engine.py
```

### File Locations
```
~/acre_workspace/
├── mesh_tester.py        # Mesh sync testing
├── vector_explorer.py    # Knowledge exploration
├── acre_simulator.py     # ACRE coin simulation
├── physics_engine.py    # Physics validation
├── data/                # Local data storage
└── logs/                # Activity logs
```

## Next Steps

1. **Test mesh sync** between devices
2. **Explore knowledge** vectors
3. **Simulate ACRE** economy
4. **Validate physics** models
5. **Document results**
6. **Share with community**

**The tools are ready. The knowledge is available. The future is yours to build.**
