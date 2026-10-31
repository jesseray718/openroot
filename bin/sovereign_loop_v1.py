import time, subprocess, random, hashlib, json
from datetime import datetime

PODS = "global_brain,wealth_retention"
MODEL = "openai/gpt-4o-mini"
NEWTON_CHAIN = "data/ledger/newton_chain.jsonl"

def log_event(event):
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] {event}")

def trigger_recursive_discovery():
    log_event("Sovereign Loop: Scanning for conceptual friction...")
    
    curiosity_query = "Analyze the Global Brain. Find a contradiction or a gap between the thermal energy data and the permaculture pods. Propose a hypothesis that bridges them into a new theorem of abundance."
    
    # HARDENED: Using a list instead of shell=True to resolve CodeQL Command Injection alerts
    cmd = [
        "python3", "bin/recursive_dossier_v1.py", 
        "--question", curiosity_query, 
        "--pods", PODS, 
        "--model", MODEL, 
        "--max-iterations", "3", 
        "--output", "/tmp/discovery_result.json"
    ]
    subprocess.run(cmd)
    
    try:
        with open("/tmp/discovery_result.json", "r") as f:
            result = json.load(f)
            answer = result.get("final_answer", "")
            
            if len(answer) > 100:
                log_event("Discovery found. Running Moral Filter...")
                # HARDENED: List-based execution
                filter_check = subprocess.run(["python3", "bin/moral_filter.py", answer], capture_output=True, text=True).stdout
                
                if "ALIGNMENT VERIFIED" in filter_check:
                    log_event("Truth of Abundance detected. Sealing to Newton Chain...")
                    # HARDENED: List-based execution
                    subprocess.run(["python3", "bin/newton_chain_seal.py", answer])
                    log_event("Sovereign Truth Sealed. The Global Brain has evolved.")
                else:
                    log_event(f"Discovery rejected by Moral Filter: {filter_check}")
    except Exception as e:
        log_event(f"Discovery cycle interrupted: {e}")

def run_forever():
    log_event("Sovereign Loop Active. The machine is now thinking for the Commons.")
    while True:
        try:
            trigger_recursive_discovery()
        except Exception as e:
            log_event(f"System Error: {e}")
        
        sleep_time = random.randint(3600, 14400) 
        log_event(f"Cycle complete. Dreaming for {sleep_time // 60} minutes...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_forever()
