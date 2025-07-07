
import http.server
import socketserver
import json
from pathlib import Path

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Read current stats
            stats_file = Path('hunt_results_20250703_231818/live_stats.json')
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {"status": "running", "message": "Hunt in progress"}
            
            self.wfile.write(json.dumps(stats).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 wKayaa 6H Hunt Monitor</title>
    <style>
        body { background: #000; color: #00ff00; font-family: monospace; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; border: 2px solid #00ff00; padding: 20px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-card { border: 1px solid #00ff00; padding: 15px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; }
    </style>
    <script>
        function updateStats() {
            fetch('/stats').then(r => r.json()).then(data => {
                console.log('Stats updated:', data);
            });
        }
        setInterval(updateStats, 5000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 wKayaa 6-Hour Intensive Hunt</h1>
            <p>Session: wKayaa_6H_Hunt_1751584698</p>
            <p>Started: 2025-07-03 23:18:18 UTC</p>
        </div>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="scanned">0</div>
                <div>Clusters Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="compromised">0</div>
                <div>Compromised</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="hits">0</div>
                <div>Perfect Hits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="secrets">0</div>
                <div>Secrets Found</div>
            </div>
        </div>
    </div>
</body>
</html>
            '''
            self.wfile.write(html.encode())

PORT = 5000
with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
    httpd.serve_forever()
            