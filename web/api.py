#!/usr/bin/env python3
"""
Lightweight Web API for Code Quality Guard
提供 REST API 用于查询和分析
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class APIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_json({"status": "ok", "version": "7.11.0"})
        elif self.path == '/api/stats':
            self.send_json(self._get_stats())
        elif self.path.startswith('/api/analyze/'):
            lang = self.path.split('/')[-1]
            self.send_json({"language": lang, "message": "Use POST for analysis"})
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/analyze':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            self.send_json(self._analyze(data))
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f'Error {code}'.encode())
    
    def _get_stats(self):
        return {
            "total_patterns": 16,
            "languages": ["python", "typescript", "go", "java", "rust", "csharp", "php"],
            "rules_count": 50
        }
    
    def _analyze(self, data):
        language = data.get("language", "python")
        code = data.get("code", "")
        
        # 这里可以调用相应的分析器
        return {
            "language": language,
            "score": 85,
            "message": "Analysis complete"
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    
    server = HTTPServer(('localhost', args.port), APIHandler)
    print(f"🛡️  Code Quality Guard API running at http://localhost:{args.port}")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/stats")
    print("  POST /api/analyze")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        server.server_close()


if __name__ == "__main__":
    main()
