import subprocess
import time
import json

def query_edge_model(model_name, prompt):
    cmd = ["ollama", "run", model_name, prompt]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

if __name__ == "__main__":
    print("[A15-EDGE] Edge neural team active (0.5B + 1.5B). Waiting for local tidbits...")
    while True:
        # Simulate micro-task filtering and rapid tidbit summarization
        status = {"node": "a15_edge", "status": "active", "alignment": "R=1, c=0"}
        with open("workareas/agape_pods/edge_heartbeat.json", "w") as f:
            json.dump(status, f)
        time.sleep(30)
