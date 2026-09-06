# OpenRoot Hardware Handbook
## Local AI Infrastructure + Permaculture Systems

### 1. System Overview
- **Hardware**: Samsung Galaxy A15 + Termux
- **Core Stack**: Ollama + FAISS + Nomic Embeddings
- **Applications**: PoPW verification, thermal cascade queries, UNE nomenclature

### 2. Setup Guide

#### 2.1 Install Dependencies
```bash
pkg update && pkg upgrade
pkg install python git curl jq
pip install numpy faiss-cpu
```

#### 2.2 Configure Ollama
```bash
# Install Ollama (if not available)
curl -fsSL https://ollama.com/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Start server
ollama serve
```

### 3. Embedding Pipeline

#### 3.1 Batch Processing Script
```python
#!/usr/bin/env python3
import json
import subprocess
import glob
from pathlib import Path
import numpy as np

# Configuration
INPUT_DIR = "/root/openroot"
OUTPUT_FILE = f"nomic_embeddings_{Path.home().name}.jsonl"

# Process markdown files
def generate_embeddings():
    md_files = sorted(glob.glob(f"{INPUT_DIR}/*.md"))
    records = []
    
    for md_path in md_files:
        with open(md_path, "r") as f:
            content = f.read()
        
        # Generate embedding
        payload = {
            "model": "nomic-embed-text",
            "input": content[:4096]
        }
        
        response = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/embed",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True
        )
        
        embedding = json.loads(response.stdout)["embedding"]
        records.append({
            "file": md_path,
            "preview": content[:200],
            "embedding": embedding
        })
    
    # Save to JSONL
    with open(OUTPUT_FILE, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    
    return len(records)
```

#### 3.2 Run Pipeline
```bash
python3 batch_nomic_embed.py
```

### 4. Vector Search Implementation

#### 4.1 FAISS Index Types
- **IndexFlatIP**: Exact search, simple implementation
- **IndexHNSWFlat**: Approximate but fast for large datasets
- **IndexIVFPQ**: Compressed vectors for memory efficiency

#### 4.2 Search Script
```python
import faiss
import numpy as np

# Load embeddings
embeddings = np.array([r["embedding"] for r in records])
faiss.normalize_L2(embeddings)

# Build index
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# Search function
def search(query_emb, k=5):
    q = np.array([query_emb])
    faiss.normalize_L2(q)
    D, I = index.search(q, k)
    return list(zip(D[0], I[0]))
```

### 5. Permaculture Applications

#### 5.1 Thermal Cascade Queries
```python
# Query for H-003 Stirling engine efficiency
query = "H-003 thermal cascade efficiency Stirling PoPW"
results = search(get_embedding(query))

for score, idx in results:
    print(f"{records[idx]['file']}: {score:.4f}")
```

#### 5.2 PoPW Verification
```python
# Verify Proof-of-Permaculture-Work claims
def verify_popw(claim_text):
    embedding = get_embedding(claim_text)
    results = search(embedding)
    
    # Check if top results support the claim
    supporting_docs = [records[i] for _, i in results if score > 0.7]
    return len(supporting_docs) > 0
```

### 6. Appropriate Technology Integration

#### 6.1 AeroCement Formulations
```python
# Query for specific cement mix designs
query = "AeroCement H-003 mix ratio thermal properties"
results = search(get_embedding(query))

# Extract relevant formulations
formulations = []
for score, idx in results:
    if "AeroCement" in records[idx]["preview"]:
        formulations.append(records[idx])
```

#### 6.2 UNE Nomenclature System
```python
# Cross-reference UNE codes with technical specs
def get_une_specs(une_code):
    query = f"{une_code} technical specifications"
    results = search(get_embedding(query))
    
    specs = []
    for score, idx in results:
        if une_code in records[idx]["preview"]:
            specs.append(records[idx])
    return specs
```

### 7. Maintenance & Optimization

#### 7.1 Model Updates
```bash
# Update embedding model
ollama pull nomic-embed-text:latest

# Rebuild index
python3 rebuild_index.py
```

#### 7.2 Performance Monitoring
```python
import time

# Benchmark search performance
start = time.time()
results = search(query_embedding)
print(f"Search time: {time.time()-start:.4f}s")
```

### 8. Troubleshooting

#### 8.1 Common Issues
- **Ollama not found**: Ensure Ollama is installed and in PATH
- **Empty embeddings**: Verify markdown files exist in input directory
- **FAISS import error**: Install faiss-cpu package

#### 8.2 Debug Commands
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Verify embeddings
jq '.embedding | length' nomic_embeddings_*.jsonl

# Test FAISS index
python3 test_search.py "test query"
```

### 9. Future Enhancements

#### 9.1 Planned Features
- Real-time PoPW validation
- Thermal efficiency optimization
- UNE code cross-referencing
- Mobile-optimized interface

#### 9.2 Research Directions
- Quantum-resistant hashing for PoPW
- Bioregional material databases
- Decentralized governance protocols

### 10. References

#### 10.1 Key Documents
- OpenRoot README
- AeroCement specifications
- UNE nomenclature guide
- Permaculture design principles

#### 10.2 External Resources
- FAISS documentation
- Ollama model hub
- Nomic embedding papers
- Termux user guide
