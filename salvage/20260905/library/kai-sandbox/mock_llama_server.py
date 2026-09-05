"""Mock llama.cpp llama-server on :9999 mimicking /v1/chat/completions OpenAI schema."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length).decode('utf-8'))
        user_msg = ""
        for m in body.get('messages', []):
            if m['role'] == 'user':
                user_msg = m['content']
        reply = (
            "## ALIGN\nLocal llama.cpp node served this yield (no Groq needed).\n\n"
            "## ASSESS\nEcho test. Received %d chars. Model: %s. Local-first path verified.\n\n"
            "## ACT\nWire $HOME/models/ Qwen2.5 with llama-server -m model.gguf --port 9999.\n\n"
            "## AMPLIFY\nOffline-capable cognition loop live. Antifragile: Groq optional, local always."
        ) % (len(user_msg), body.get('model', 'local'))
        out = {"choices": [{"message": {"role": "assistant", "content": reply}}]}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(out).encode('utf-8'))
    def log_message(self, *a):
        pass

HTTPServer(('127.0.0.1', 9999), H).serve_forever()
