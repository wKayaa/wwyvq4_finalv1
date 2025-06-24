#!/usr/bin/env python3
"""
Web Interface Module - Flask Web UI Wrapper
Author: wKayaa
Date: 2025-06-24 17:02:05 UTC

Wraps the existing Flask application in a framework-compatible interface.
"""

import sys
import logging
import threading
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class WebInterface:
    """Web interface wrapper for the existing Flask app"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger('framework.web')
        self.app = None
        self.socketio = None
        self.running = False
        self.thread = None
        
        self.port = orchestrator.config['network']['web_interface_port']
        self.host = orchestrator.config['network']['bind_address']
        
        self.logger.info(f"🌐 WebInterface initialized on {self.host}:{self.port}")
        
        # Try to initialize the Flask app
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize the Flask application"""
        try:
            # Import the existing Flask app
            from app import app, socketio, ExploitationManager
            
            self.app = app
            self.socketio = socketio
            
            # Set up the exploitation manager with our orchestrator
            if not hasattr(app, 'exploitation_manager'):
                app.exploitation_manager = ExploitationManager()
            
            # Add our orchestrator as a reference
            app.orchestrator = self.orchestrator
            
            self.logger.info("✅ Flask app initialized successfully")
            
        except ImportError as e:
            self.logger.error(f"❌ Failed to import Flask app: {e}")
            self._create_minimal_app()
    
    def _create_minimal_app(self):
        """Create a minimal Flask app if the main one is not available"""
        try:
            from flask import Flask, jsonify, render_template_string
            
            self.app = Flask(__name__)
            self.app.config['SECRET_KEY'] = 'framework-web-interface'
            
            @self.app.route('/')
            def index():
                return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>AIO Exploit Framework</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
                        .container { max-width: 800px; margin: 0 auto; }
                        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
                        .status-card { background: #2a2a2a; padding: 20px; margin: 20px 0; border-radius: 8px; }
                        .success { color: #4CAF50; }
                        .warning { color: #FF9800; }
                        .error { color: #F44336; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🚀 AIO Exploit Framework</h1>
                            <p>Web Interface - Framework Mode</p>
                        </div>
                        
                        <div class="status-card">
                            <h3>Framework Status</h3>
                            <p class="success">✅ Web interface is running</p>
                            <p class="warning">⚠️ Limited functionality - Basic web interface</p>
                            <p>Session: {{ session_id }}</p>
                            <p>Uptime: {{ uptime }}</p>
                        </div>
                        
                        <div class="status-card">
                            <h3>Available Modules</h3>
                            {% for module, available in modules.items() %}
                                <p class="{{ 'success' if available else 'error' }}">
                                    {{ '✅' if available else '❌' }} {{ module }}
                                </p>
                            {% endfor %}
                        </div>
                        
                        <div class="status-card">
                            <h3>API Endpoints</h3>
                            <p><a href="/api/status" style="color: #4CAF50;">/api/status</a> - Framework status</p>
                            <p><a href="/api/config" style="color: #4CAF50;">/api/config</a> - Configuration</p>
                        </div>
                    </div>
                </body>
                </html>
                ''', 
                session_id=self.orchestrator.session_id,
                uptime=str(self.orchestrator.start_time),
                modules=self.orchestrator.get_status()['modules']
                )
            
            @self.app.route('/api/status')
            def api_status():
                return jsonify(self.orchestrator.get_status())
            
            @self.app.route('/api/config')
            def api_config():
                return jsonify(self.orchestrator.config)
            
            self.logger.info("✅ Minimal Flask app created")
            
        except ImportError as e:
            self.logger.error(f"❌ Failed to create minimal Flask app: {e}")
    
    def run(self):
        """Run the web interface"""
        if not self.app:
            self.logger.error("❌ No Flask app available")
            return
        
        try:
            self.running = True
            self.logger.info(f"🌐 Starting web interface on {self.host}:{self.port}")
            
            if self.socketio:
                # Run with SocketIO if available
                self.socketio.run(
                    self.app,
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    log_output=False
                )
            else:
                # Run basic Flask app
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False
                )
                
        except Exception as e:
            self.logger.error(f"❌ Web interface failed: {e}")
            self.running = False
        finally:
            self.running = False
    
    def start_async(self):
        """Start web interface in a separate thread"""
        if self.running:
            self.logger.warning("⚠️ Web interface already running")
            return
        
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.logger.info("🌐 Web interface started in background thread")
    
    def stop(self):
        """Stop the web interface"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.logger.info("⏹️ Stopping web interface...")
            # Note: Flask/SocketIO doesn't have a clean shutdown method
            # This is a limitation we'll accept for now
    
    def is_running(self) -> bool:
        """Check if web interface is running"""
        return self.running and (self.thread is None or self.thread.is_alive())
    
    def get_url(self) -> str:
        """Get the web interface URL"""
        return f"http://{self.host}:{self.port}"