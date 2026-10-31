import sys
import requests

OPTIPLEX_URL = "http://100.122.169.43:8000/search"

def query_node(prompt):
    try:
        response = requests.get(OPTIPLEX_URL, params={"q": prompt, "top_k": 5}, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n--- Search Results for: '{data.get('query', prompt)}' ---")
        for res in data.get("results", []):
            print(f"[{res.get('distance', 0):.4f}] {res.get('path', 'N/A')}")
    except Exception as e:
        print(f"Error querying OptiPlex search node: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_text = " ".join(sys.argv[1:])
    else:
        query_text = input("Enter search query: ")
    
    query_node(query_text)
