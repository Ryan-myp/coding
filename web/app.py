#!/usr/bin/env python3
"""
Code Quality Guard Web UI
Simple web interface for managing patterns and viewing reports
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))
from features.enhanced_pattern_library import EnhancedPatternLibrary
from features.skill_absorber import SkillAbsorber

class QGuardHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_html(self._get_index_html())
        elif self.path == '/api/patterns':
            self.send_json(self._get_patterns())
        elif self.path == '/api/stats':
            self.send_json(self._get_stats())
        elif self.path == '/api/skills':
            self.send_json(self._get_skills())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/patterns':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self.send_json(self._add_pattern(data))
        elif self.path == '/api/skills/absorb':
            self.send_json(self._absorb_skills())
        else:
            self.send_error(404)
    
    def send_html(self, html: str):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_json(self, data: dict):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error(self, code: int):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f'Error {code}'.encode())
    
    def _get_index_html(self) -> str:
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Guard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 32px; font-weight: bold; color: #007aff; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f5f5f5; }
        .btn { background: #007aff; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🛡️ Code Quality Guard</h1>
    <p>Agent Code Generation Guide & Quality System</p>
    
    <div class="stats" id="stats">
        <div class="stat-card"><div class="stat-value" id="total-patterns">-</div><div class="stat-label">Total Patterns</div></div>
        <div class="stat-card"><div class="stat-value" id="total-skills">-</div><div class="stat-label">Skills Absorbed</div></div>
        <div class="stat-card"><div class="stat-value" id="total-usages">-</div><div class="stat-label">Total Usages</div></div>
        <div class="stat-card"><div class="stat-value" id="avg-score">-</div><div class="stat-label">Avg Score</div></div>
    </div>
    
    <h2>Patterns</h2>
    <table>
        <thead><tr><th>Name</th><th>Category</th><th>Language</th><th>Score</th><th>Usage</th></tr></thead>
        <tbody id="patterns-table"></tbody>
    </table>
    
    <h2>Skills Absorbed</h2>
    <table>
        <thead><tr><th>Name</th><th>Category</th><th>Source</th><th>Score</th></tr></thead>
        <tbody id="skills-table"></tbody>
    </table>
    
    <button class="btn" onclick="loadData()">Refresh</button>
    <button class="btn" onclick="absorbSkills()">Absorb New Skills</button>
    
    <script>
        async function loadData() {
            const [patternsRes, statsRes, skillsRes] = await Promise.all([
                fetch('/api/patterns'),
                fetch('/api/stats'),
                fetch('/api/skills')
            ]);
            
            const patterns = await patternsRes.json();
            const stats = await statsRes.json();
            const skills = await skillsRes.json();
            
            document.getElementById('total-patterns').textContent = stats.total_patterns || 0;
            document.getElementById('total-skills').textContent = skills.total_patterns || 0;
            document.getElementById('total-usages').textContent = stats.total_usages || 0;
            document.getElementById('avg-score').textContent = (stats.average_success_rate * 100 || 0).toFixed(0) + '%';
            
            const patternsTable = document.getElementById('patterns-table');
            patternsTable.innerHTML = patterns.map(p => `
                <tr>
                    <td>${p.name}</td>
                    <td>${p.category}</td>
                    <td>${p.language}</td>
                    <td>${(p.quality_score || 0).toFixed(0)}</td>
                    <td>${p.usage_count || 0}</td>
                </tr>
            `).join('');
            
            const skillsTable = document.getElementById('skills-table');
            skillsTable.innerHTML = (skills.patterns || []).map(p => `
                <tr>
                    <td>${p.name}</td>
                    <td>${p.category}</td>
                    <td>${p.source}</td>
                    <td>${(p.quality_score || 0).toFixed(0)}</td>
                </tr>
            `).join('');
        }
        
        async function absorbSkills() {
            const res = await fetch('/api/skills/absorb', { method: 'POST' });
            const data = await res.json();
            alert('Absorbed ' + data.absorbed + ' new patterns');
            loadData();
        }
        
        loadData();
    </script>
</body>
</html>'''
    
    def _get_patterns(self) -> dict:
        library = EnhancedPatternLibrary('.')
        return library.patterns
    
    def _get_stats(self) -> dict:
        library = EnhancedPatternLibrary('.')
        return library.get_statistics()
    
    def _get_skills(self) -> dict:
        absorber = SkillAbsorber('.')
        return absorber.get_absorbed_stats()
    
    def _add_pattern(self, data: dict) -> dict:
        from features.enhanced_pattern_library import Pattern
        library = EnhancedPatternLibrary('.')
        pattern = Pattern(
            name=data.get('name', 'Unknown'),
            category=data.get('category', 'general'),
            language=data.get('language', 'python'),
            description=data.get('description', ''),
            code_example=data.get('code_example', ''),
            tags=data.get('tags', []),
            source='web-ui'
        )
        pattern_id = library.add_pattern(pattern)
        return {"id": pattern_id, "status": "created"}
    
    def _absorb_skills(self) -> dict:
        absorber = SkillAbsorber('.')
        patterns = absorber.absorb_common_patterns()
        return {"absorbed": len(patterns)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Code Quality Guard Web UI')
    parser.add_argument('--port', type=int, default=8080, help='Port to serve on')
    args = parser.parse_args()
    
    server = HTTPServer(('localhost', args.port), QGuardHandler)
    print(f"🛡️  Code Quality Guard Web UI running at http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()


if __name__ == "__main__":
    main()
