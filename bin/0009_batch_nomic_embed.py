#!/usr/bin/env python3
import json
import subprocess
import glob
from pathlib import Path
import sys

# Target the correct openroot directory
md_files = sorted(glob.glob("/root/openroot/*.md"))
if not md_files:
    print("No markdown files found in /root/openroot/")
    sys.exit(1)

print(f"Found {len(md_files)} markdown files to embed")

# Rest of the script remains the same...
