#!/usr/bin/env python3
"""
🌐 WWYVQ Framework v2.1 - Web Dashboard Interface
Ultra-Organized Architecture - Real-time Web Dashboard

Features:
- Real-time monitoring dashboard
- Live operation tracking
- Interactive charts and graphs
- Professional web interface
- WebSocket for real-time updates
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors


class WWYVQWebDashboard:
    """
    Real-time web dashboard for WWYVQ v2.1
    
    Features:
    - Live monitoring
    - Interactive interface
    - Real-time updates
    - Professional design
    """
    
    def __init__(self, engine):
        """Initialize web dashboard"""
        self.engine = engine
        self.app = None
        self.websockets = set()
        
    async def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run web dashboard server"""
        # Create web application
        self.app = web.Application()
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Routes
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/api/status', self.api_status)
        self.app.router.add_get('/api/stats', self.api_stats)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
        
        # Static files (would serve CSS/JS)
        # self.app.router.add_static('/', path='static', name='static')
        
        print(f"🌐 Starting web dashboard on http://{host}:{port}")
        
        # Start server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
                # Broadcast updates to connected clients
                await self.broadcast_updates()
        except KeyboardInterrupt:
            await runner.cleanup()
    
    async def index(self, request):
        """Serve main dashboard page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WWYVQ v2.1 - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header h1 { color: #667eea; text-align: center; margin-bottom: 10px; }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }
        .status-card { 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .status-card h3 { color: #667eea; margin-bottom: 10px; }
        .status-card .value { font-size: 2em; font-weight: bold; color: #333; }
        .operations { 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .operations h2 { color: #667eea; margin-bottom: 15px; }
        .operation-item { 
            background: #f8f9fa; 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 6px; 
            border-left: 4px solid #667eea;
        }
        .status-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 8px;
        }
        .status-running { background: #28a745; }
        .status-pending { background: #ffc107; }
        .status-failed { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 WWYVQ Framework v2.1 - Dashboard</h1>
            <p style="text-align: center; color: #666;">Real-time Monitoring & Control</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🎯 Operations</h3>
                <div class="value" id="operations-total">0</div>
            </div>
            <div class="status-card">
                <h3>📊 Targets</h3>
                <div class="value" id="targets-processed">0</div>
            </div>
            <div class="status-card">
                <h3>🔑 Credentials</h3>
                <div class="value" id="credentials-found">0</div>
            </div>
            <div class="status-card">
                <h3>⏱️ Uptime</h3>
                <div class="value" id="uptime">0h 0m</div>
            </div>
        </div>
        
        <div class="operations">
            <h2>🔄 Active Operations</h2>
            <div id="active-operations">
                <p style="color: #888; text-align: center;">No active operations</p>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'stats') {
                updateStats(data.stats);
            } else if (data.type === 'operations') {
                updateOperations(data.operations);
            }
        };
        
        function updateStats(stats) {
            document.getElementById('operations-total').textContent = stats.operations_total || 0;
            document.getElementById('targets-processed').textContent = stats.targets_processed || 0;
            document.getElementById('credentials-found').textContent = stats.credentials_found || 0;
            
            const uptime = stats.uptime_seconds || 0;
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            document.getElementById('uptime').textContent = `${hours}h ${minutes}m`;
        }
        
        function updateOperations(operations) {
            const container = document.getElementById('active-operations');
            
            if (Object.keys(operations).length === 0) {
                container.innerHTML = '<p style="color: #888; text-align: center;">No active operations</p>';
                return;
            }
            
            let html = '';
            for (const [opId, opData] of Object.entries(operations)) {
                html += `
                    <div class="operation-item">
                        <span class="status-indicator status-running"></span>
                        <strong>${opId}</strong> - ${opData.operation_type || 'unknown'}
                        <small style="float: right; color: #666;">${opData.targets?.length || 0} targets</small>
                    </div>
                `;
            }
            container.innerHTML = html;
        }
        
        // Initial load
        fetch('/api/stats')
            .then(response => response.json())
            .then(stats => updateStats(stats))
            .catch(console.error);
        
        ws.onopen = function() {
            console.log('Connected to WWYVQ Dashboard');
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def api_status(self, request):
        """API endpoint for engine status"""
        try:
            stats = self.engine.get_engine_stats()
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def api_stats(self, request):
        """API endpoint for statistics"""
        try:
            stats = self.engine.get_engine_stats()
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle incoming messages if needed
                    pass
                elif msg.type == WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            print(f'WebSocket error: {e}')
        finally:
            self.websockets.discard(ws)
        
        return ws
    
    async def broadcast_updates(self):
        """Broadcast updates to all connected WebSocket clients"""
        if not self.websockets:
            return
        
        try:
            # Get current stats
            stats = self.engine.get_engine_stats()
            active_ops = self.engine.get_active_operations()
            
            # Prepare update messages
            stats_msg = json.dumps({
                'type': 'stats',
                'stats': stats
            })
            
            ops_msg = json.dumps({
                'type': 'operations',
                'operations': active_ops
            })
            
            # Send to all connected clients
            disconnected = set()
            for ws in self.websockets:
                try:
                    await ws.send_str(stats_msg)
                    await ws.send_str(ops_msg)
                except Exception:
                    disconnected.add(ws)
            
            # Remove disconnected clients
            self.websockets -= disconnected
            
        except Exception as e:
            print(f'Broadcast error: {e}')


class WebModule:
    """Web dashboard module wrapper"""
    
    def __init__(self, config_manager, logger, engine):
        """Initialize web module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        self.dashboard = WWYVQWebDashboard(engine)
        
        self.logger.info("🌐 Web Dashboard Interface initialized")
    
    async def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run web dashboard"""
        await self.dashboard.run(host, port)
    
    async def shutdown(self):
        """Shutdown web module"""
        self.logger.info("🛑 Web Dashboard Interface shutdown completed")