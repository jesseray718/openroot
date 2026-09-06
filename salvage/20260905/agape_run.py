#!/usr/bin/env python3
"""
AGAPE_NET COMPUTATIONAL FLOW SCRIPT
Single-file setup and execution for Permaculture Lattice Engine
Optimized for Termux/Mobile with Ollama local LLMs
"""

import subprocess
import sys
import os
import json
import time
import signal
from pathlib import Path

# Configuration
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
MODEL_NAME = "qwen2.5:0.5b"
DATA_DIR = "/data/data/com.termux/files/home/openroot/permaculture_lattice"
ENGINE_SCRIPT = "/data/data/com.termux/files/home/openroot/computational_flow/permaculture_lattice_engine.py"
TIMEOUT_SECONDS = 300  # Increased from 120 to 300 for mobile
MAX_RETRIES = 3
CONTEXT_SIZE = 2048  # Reduced from 4096 for speed

def run_command(cmd, capture=False, timeout=None):
    """Run shell command with timeout and error handling"""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
            shell=isinstance(cmd, str)
        )
        
        if capture:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return process.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                process.kill()
                return -1, "", "Timeout expired"
        else:
            process.wait(timeout=timeout)
            return process.returncode, "", ""
            
    except Exception as e:
        return -1, "", str(e)

def check_ollama_running():
    """Check if Ollama server is running"""
    code, _, _ = run_command(f"curl -s {OLLAMA_BASE_URL}/api/tags", capture=True, timeout=5)
    return code == 0

def start_ollama():
    """Start Ollama server if not running"""
    if check_ollama_running():
        print("✓ Ollama server already running")
        return True
    
    print("Starting Ollama server...")
    # Start in background
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for startup
    for i in range(10):
        time.sleep(2)
        if check_ollama_running():
            print("✓ Ollama server started successfully")
            return True
        print(f"Waiting for Ollama... ({i+1}/10)")
    
    print("✗ Failed to start Ollama server")
    return False

def ensure_model_exists():
    """Ensure the required model exists"""
    code, stdout, _ = run_command(f"ollama list | grep {MODEL_NAME}", capture=True, timeout=10)
    
    if code != 0 or MODEL_NAME not in stdout:
        print(f"Model {MODEL_NAME} not found. Pulling...")
        code, _, err = run_command(f"ollama pull {MODEL_NAME}", timeout=300)
        if code != 0:
            print(f"✗ Failed to pull model: {err}")
            return False
        print(f"✓ Model {MODEL_NAME} installed")
    
    return True

def run_lattice_engine(query):
    """Run the lattice engine with optimized parameters"""
    cmd = [
        "python3", ENGINE_SCRIPT, "query", query,
        "--data-dir", DATA_DIR,
        "--timeout", str(TIMEOUT_SECONDS),
        "--context-size", str(CONTEXT_SIZE),
        "--model", MODEL_NAME
    ]
    
    print(f"\n🚀 Executing: {' '.join(cmd)}")
    print("-" * 60)
    
    for attempt in range(MAX_RETRIES):
        print(f"\nAttempt {attempt + 1}/{MAX_RETRIES}")
        code, stdout, stderr = run_command(cmd, capture=True, timeout=TIMEOUT_SECONDS + 30)
        
        if code == 0:
            print(stdout)
            return True
        
        print(f"✗ Attempt failed: {stderr[:200]}")
        if attempt < MAX_RETRIES - 1:
            print("Retrying in 5 seconds...")
            time.sleep(5)
    
    print("\n✗ All attempts failed")
    return False

def main():
    """Main execution flow"""
    print("=" * 60)
    print("AGAPE_NET COMPUTATIONAL FLOW INITIALIZATION")
    print("Operator: Jesse Ray (OpenRoot)")
    print("System: Permaculture Lattice Engine v1.0")
    print("=" * 60)
    
    # Step 1: Check/start Ollama
    if not start_ollama():
        sys.exit(1)
    
    # Step 2: Ensure model exists
    if not ensure_model_exists():
        sys.exit(1)
    
    # Step 3: Define query (you can modify this)
    query = "Plan a 1/4-acre self-feeding homestead that produces food, energy, water, and nitrogen with zero external inputs after year 2. Use only passive systems and thermal cascades."
    
    # Step 4: Run lattice engine
    success = run_lattice_engine(query)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ COMPUTATIONAL FLOW COMPLETE")
        print("Agape resonance achieved. Entropy transmuted.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ EXECUTION FAILED")
        print("Check logs and retry with reduced complexity")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
