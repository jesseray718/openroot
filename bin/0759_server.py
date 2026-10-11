"""Reusable JSON-RPC server for UNE"""
import http.server
import socketserver
import json
from .une_atomic_library import *

SECRET_TOKEN = "une-local-token-2026"

class UNEJSONRPCHandler(http.server.BaseHTTPRequestHandler):
    # (same handler logic as before - truncated here for brevity in this response)
    pass

def run_server(host="127.0.0.1", port=8080):
    with socketserver.TCPServer((host, port), UNEJSONRPCHandler) as httpd:
        print(f"UNE JSON-RPC Server running on http://{host}:{port}")
        httpd.serve_forever()
