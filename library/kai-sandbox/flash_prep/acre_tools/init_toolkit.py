#!/usr/bin/env python3
"""
Initialize ACRE Toolkit
Set up workspace and tools
"""

from pathlib import Path
import os

def main():
    print("ACRE Toolkit Initialization")
    print("=" * 40)
    
    # Create workspace
    workspace = Path('~/acre_workspace').expanduser()
    workspace.mkdir(exist_ok=True)
    
    print(f"Workspace: {workspace}")
    
    # Create directories
    (workspace / 'data').mkdir(exist_ok=True)
    (workspace / 'logs').mkdir(exist_ok=True)
    (workspace / 'results').mkdir(exist_ok=True)
    
    print("Directories created:")
    print("  - data/")
    print("  - logs/")
    print("  - results/")
    
    # Copy tools
    tools_dir = Path('~/flash_prep/acre_tools').expanduser()
    if tools_dir.exists():
        for tool in ['mesh_tester.py', 'vector_explorer.py', 'acre_simulator.py', 'physics_engine.py']:
            src = tools_dir / tool
            dst = workspace / tool
            if src.exists():
                with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                    f_dst.write(f_src.read())
                print(f"Copied: {tool}")
    
    # Create README
    readme = workspace / 'README.md'
    with open(readme, 'w') as f:
        f.write("""
# ACRE Workspace

## Tools Available

- `mesh_tester.py` - Test mesh sync between devices
- `vector_explorer.py` - Explore knowledge vectors
- `acre_simulator.py` - Simulate ACRE coin economy
- `physics_engine.py` - Test physical principles

## Quick Start

```bash
# Test mesh sync
python3 mesh_tester.py node-001

# Explore vectors
python3 vector_explorer.py

# Simulate ACRE
python3 acre_simulator.py

# Test physics
python3 physics_engine.py
```

## Results

Store test results in the `results/` directory.

## Notes

- All tools are self-contained
- No internet required for basic operation
- Modify tools as needed for your experiments
""")
    
    print("\nInitialization complete!")
    print(f"\nNext steps:")
    print(f"  cd {workspace}")
    print(f"  python3 mesh_tester.py node-001")
    print(f"  python3 vector_explorer.py")
    print(f"  python3 acre_simulator.py")
    print(f"  python3 physics_engine.py")

if __name__ == '__main__':
    main()
