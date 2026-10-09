#!/usr/bin/env python3
"""openai_relay_9999.py — transparent HTTP relay 0.0.0.0:9999 -> 127.0.0.1:11434.
Gives kai9000 an OpenAI-compatible endpoint (/v1/chat/completions, /v1/models) served by
Ollama natively. Stdlib-only, threaded, streams chunked responses."""
import http.client, socketserver, sys
from http.server import BaseHTTPRequestHandler

UP_HOST, UP_PORT = "127.0.0.1", 11434

class Relay(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def _relay(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            conn = http.client.HTTPConnection(UP_HOST, UP_PORT, timeout=600)
            hdrs = {k: v for k, v in self.headers.items() if k.lower() != "host"}
            conn.request(self.command, self.path, body=body, headers=hdrs)
            resp = conn.getresponse()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() in ("transfer-encoding", "connection"): continue
                self.send_header(k, v)
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            while True:
                chunk = resp.read(65536)
                if not chunk: break
                self.wfile.write(chunk)
                self.wfile.flush()
            conn.close()
        except BrokenPipeError:
            pass
    do_GET = do_POST = do_PUT = do_DELETE = _relay
    def log_message(self, fmt, *args):
        sys.stderr.write("[relay] %s %s\n" % (self.address_string(), fmt % args))

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    srv = Server(("0.0.0.0", 9999), Relay)
    print("[relay] listening 0.0.0.0:9999 -> 127.0.0.1:11434", flush=True)
    srv.serve_forever()
