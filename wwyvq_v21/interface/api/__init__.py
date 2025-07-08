#!/usr/bin/env python3
"""
🔌 WWYVQ Framework v2.1 - REST API Interface
Ultra-Organized Architecture - Professional REST API

Features:
- RESTful API endpoints
- Authentication and authorization
- Auto-generated documentation
- Rate limiting and monitoring
- Professional API design
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from aiohttp import web
import aiohttp_cors
import jwt
import hashlib


class WWYVQRestAPI:
    """
    Professional REST API for WWYVQ v2.1
    
    Features:
    - RESTful endpoints
    - Authentication
    - Rate limiting
    - Auto documentation
    """
    
    def __init__(self, engine):
        """Initialize REST API"""
        self.engine = engine
        self.app = None
        
        # API configuration
        self.api_key = "wwyvq_api_key_v2.1"  # Should be configurable
        self.rate_limits = {}
        
    async def run(self, host: str = "0.0.0.0", port: int = 8081):
        """Run REST API server"""
        # Create web application
        self.app = web.Application(middlewares=[
            self.auth_middleware,
            self.rate_limit_middleware
        ])
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # API Routes
        self.setup_routes()
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
        
        print(f"🔌 Starting REST API on http://{host}:{port}")
        
        # Start server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(3600)  # Keep alive
        except KeyboardInterrupt:
            await runner.cleanup()
    
    def setup_routes(self):
        """Setup API routes"""
        # Documentation
        self.app.router.add_get('/', self.api_docs)
        self.app.router.add_get('/docs', self.api_docs)
        
        # Status and Health
        self.app.router.add_get('/api/v1/health', self.health_check)
        self.app.router.add_get('/api/v1/status', self.get_status)
        self.app.router.add_get('/api/v1/stats', self.get_statistics)
        
        # Operations
        self.app.router.add_post('/api/v1/operations/scan', self.start_scan)
        self.app.router.add_post('/api/v1/operations/exploit', self.start_exploit)
        self.app.router.add_post('/api/v1/operations/scrape', self.start_scrape)
        self.app.router.add_post('/api/v1/operations/validate', self.start_validate)
        
        # Operations Management
        self.app.router.add_get('/api/v1/operations', self.list_operations)
        self.app.router.add_get('/api/v1/operations/{operation_id}', self.get_operation)
        self.app.router.add_delete('/api/v1/operations/{operation_id}', self.cancel_operation)
        
        # Sessions
        self.app.router.add_get('/api/v1/sessions', self.list_sessions)
        self.app.router.add_post('/api/v1/sessions', self.create_session)
        self.app.router.add_get('/api/v1/sessions/{session_id}', self.get_session)
        self.app.router.add_delete('/api/v1/sessions/{session_id}', self.close_session)
        
        # Data Export
        self.app.router.add_post('/api/v1/export', self.export_data)
        
        # Configuration
        self.app.router.add_get('/api/v1/config', self.get_config)
        self.app.router.add_put('/api/v1/config', self.update_config)
    
    @web.middleware
    async def auth_middleware(self, request, handler):
        """Authentication middleware"""
        # Skip auth for docs and health
        if request.path in ['/', '/docs', '/api/v1/health']:
            return await handler(request)
        
        # Check API key
        auth_header = request.headers.get('Authorization', '')
        api_key = request.headers.get('X-API-Key', '')
        
        if not (auth_header.startswith('Bearer ') or api_key):
            return web.json_response(
                {'error': 'Authentication required'}, 
                status=401
            )
        
        # Validate API key (simplified)
        provided_key = auth_header.replace('Bearer ', '') if auth_header else api_key
        if provided_key != self.api_key:
            return web.json_response(
                {'error': 'Invalid API key'}, 
                status=401
            )
        
        return await handler(request)
    
    @web.middleware
    async def rate_limit_middleware(self, request, handler):
        """Rate limiting middleware"""
        client_ip = request.remote
        current_time = datetime.utcnow().timestamp()
        
        # Simple rate limiting (10 requests per minute)
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Clean old requests
        self.rate_limits[client_ip] = [
            timestamp for timestamp in self.rate_limits[client_ip]
            if current_time - timestamp < 60
        ]
        
        # Check rate limit
        if len(self.rate_limits[client_ip]) >= 10:
            return web.json_response(
                {'error': 'Rate limit exceeded'}, 
                status=429
            )
        
        # Add current request
        self.rate_limits[client_ip].append(current_time)
        
        return await handler(request)
    
    async def api_docs(self, request):
        """Serve API documentation"""
        docs_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WWYVQ v2.1 - API Documentation</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 40px; 
            background: #f5f5f5;
            color: #333;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        h1 { color: #667eea; text-align: center; margin-bottom: 30px; }
        h2 { color: #444; border-bottom: 2px solid #667eea; padding-bottom: 5px; }
        .endpoint { 
            background: #f8f9fa; 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 6px; 
            border-left: 4px solid #667eea;
        }
        .method { 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 4px; 
            color: white; 
            font-weight: bold; 
            margin-right: 10px;
        }
        .get { background: #28a745; }
        .post { background: #007bff; }
        .put { background: #ffc107; color: #333; }
        .delete { background: #dc3545; }
        pre { background: #f1f1f1; padding: 10px; border-radius: 4px; overflow-x: auto; }
        .auth-note { 
            background: #fff3cd; 
            padding: 15px; 
            border-radius: 6px; 
            border-left: 4px solid #ffc107; 
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 WWYVQ Framework v2.1 - API Documentation</h1>
        
        <div class="auth-note">
            <strong>🔐 Authentication Required:</strong> All endpoints (except /health and /docs) require authentication.
            Include API key in header: <code>X-API-Key: your_api_key</code> or <code>Authorization: Bearer your_api_key</code>
        </div>
        
        <h2>🏥 Health & Status</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/health</strong>
            <p>Check API health status</p>
            <pre>Response: {"status": "healthy", "timestamp": "..."}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/status</strong>
            <p>Get engine status and metrics</p>
            <pre>Response: {"engine_id": "...", "uptime_seconds": 123, ...}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/stats</strong>
            <p>Get detailed statistics</p>
            <pre>Response: {"operations_total": 10, "credentials_found": 5, ...}</pre>
        </div>
        
        <h2>🎯 Operations</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/v1/operations/scan</strong>
            <p>Start scan operation</p>
            <pre>Request: {"targets": ["192.168.1.1", "example.com"], "mode": "standard"}
Response: {"operation_id": "...", "status": "started"}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/v1/operations/exploit</strong>
            <p>Start exploitation operation</p>
            <pre>Request: {"targets": ["kubernetes.local:6443"], "mode": "aggressive"}
Response: {"operation_id": "...", "status": "started"}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/v1/operations/scrape</strong>
            <p>Start credential scraping operation</p>
            <pre>Request: {"targets": ["https://target.com"], "paths": ["/.env", "/config.js"]}
Response: {"operation_id": "...", "status": "started"}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/operations</strong>
            <p>List all operations</p>
            <pre>Response: {"operations": [{"id": "...", "type": "scan", "status": "running"}]}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/operations/{operation_id}</strong>
            <p>Get specific operation details</p>
            <pre>Response: {"operation_id": "...", "status": "completed", "results": {...}}</pre>
        </div>
        
        <h2>📝 Sessions</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/sessions</strong>
            <p>List all sessions</p>
            <pre>Response: {"sessions": [{"id": "...", "type": "scan", "status": "active"}]}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/v1/sessions</strong>
            <p>Create new session</p>
            <pre>Request: {"operation_type": "scan", "metadata": {...}}
Response: {"session_id": "...", "status": "created"}</pre>
        </div>
        
        <h2>📊 Data Export</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/v1/export</strong>
            <p>Export data in various formats</p>
            <pre>Request: {"format": "json", "data_type": "results", "session_id": "..."}
Response: {"export_id": "...", "download_url": "...", "expires_at": "..."}</pre>
        </div>
        
        <h2>⚙️ Configuration</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/v1/config</strong>
            <p>Get current configuration</p>
            <pre>Response: {"core": {...}, "targets": {...}, ...}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method put">PUT</span> <strong>/api/v1/config</strong>
            <p>Update configuration</p>
            <pre>Request: {"core": {"max_concurrent": 50}, ...}
Response: {"status": "updated", "changes": {...}}</pre>
        </div>
        
        <hr style="margin: 40px 0;">
        <p style="text-align: center; color: #666;">
            <strong>WWYVQ Framework v2.1</strong> - Professional Red Team Automation<br>
            Rate Limited: 10 requests per minute per IP
        </p>
    </div>
</body>
</html>
        """
        return web.Response(text=docs_html, content_type='text/html')
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.1'
        })
    
    async def get_status(self, request):
        """Get engine status"""
        try:
            stats = self.engine.get_engine_stats()
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_statistics(self, request):
        """Get detailed statistics"""
        try:
            stats = self.engine.get_engine_stats()
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_scan(self, request):
        """Start scan operation"""
        try:
            data = await request.json()
            targets = data.get('targets', [])
            mode = data.get('mode', 'standard')
            
            if not targets:
                return web.json_response({'error': 'No targets provided'}, status=400)
            
            # Execute scan (simplified)
            result = await self.engine.execute_operation(
                operation_type='scan',
                targets=targets
            )
            
            return web.json_response({
                'operation_id': result.operation_id,
                'status': result.status.value,
                'targets_count': len(targets)
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_exploit(self, request):
        """Start exploitation operation"""
        try:
            data = await request.json()
            targets = data.get('targets', [])
            mode = data.get('mode', 'standard')
            
            if not targets:
                return web.json_response({'error': 'No targets provided'}, status=400)
            
            result = await self.engine.execute_operation(
                operation_type='exploit',
                targets=targets
            )
            
            return web.json_response({
                'operation_id': result.operation_id,
                'status': result.status.value,
                'targets_count': len(targets)
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_scrape(self, request):
        """Start scraping operation"""
        try:
            data = await request.json()
            targets = data.get('targets', [])
            
            if not targets:
                return web.json_response({'error': 'No targets provided'}, status=400)
            
            result = await self.engine.execute_operation(
                operation_type='scrape',
                targets=targets
            )
            
            return web.json_response({
                'operation_id': result.operation_id,
                'status': result.status.value,
                'targets_count': len(targets)
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_validate(self, request):
        """Start validation operation"""
        try:
            data = await request.json()
            credentials = data.get('credentials', [])
            
            if not credentials:
                return web.json_response({'error': 'No credentials provided'}, status=400)
            
            result = await self.engine.execute_operation(
                operation_type='validate',
                targets=[],
                credentials=credentials
            )
            
            return web.json_response({
                'operation_id': result.operation_id,
                'status': result.status.value,
                'credentials_count': len(credentials)
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def list_operations(self, request):
        """List all operations"""
        try:
            active_ops = self.engine.get_active_operations()
            
            operations = []
            for op_id, op_data in active_ops.items():
                operations.append({
                    'id': op_id,
                    'type': op_data.get('operation_type', 'unknown'),
                    'status': 'running',
                    'targets_count': len(op_data.get('targets', [])),
                    'start_time': op_data.get('start_time', 0)
                })
            
            return web.json_response({'operations': operations})
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_operation(self, request):
        """Get specific operation"""
        operation_id = request.match_info['operation_id']
        
        try:
            active_ops = self.engine.get_active_operations()
            
            if operation_id in active_ops:
                op_data = active_ops[operation_id]
                return web.json_response({
                    'operation_id': operation_id,
                    'type': op_data.get('operation_type', 'unknown'),
                    'status': 'running',
                    'targets': op_data.get('targets', []),
                    'start_time': op_data.get('start_time', 0)
                })
            else:
                return web.json_response({'error': 'Operation not found'}, status=404)
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def cancel_operation(self, request):
        """Cancel operation"""
        operation_id = request.match_info['operation_id']
        
        # This would implement operation cancellation
        return web.json_response({
            'operation_id': operation_id,
            'status': 'cancelled'
        })
    
    async def list_sessions(self, request):
        """List sessions"""
        try:
            sessions = await self.engine.session_manager.list_sessions()
            
            session_list = []
            for session in sessions[:20]:  # Limit to 20
                session_list.append({
                    'id': session.session_id,
                    'type': session.operation_type,
                    'status': session.status.value,
                    'created_at': session.created_at.isoformat(),
                    'targets_count': session.targets_count,
                    'results_count': session.results_count
                })
            
            return web.json_response({'sessions': session_list})
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def create_session(self, request):
        """Create new session"""
        try:
            data = await request.json()
            operation_type = data.get('operation_type', 'general')
            metadata = data.get('metadata', {})
            
            session_id = await self.engine.session_manager.create_session(
                operation_type, metadata
            )
            
            return web.json_response({
                'session_id': session_id,
                'status': 'created'
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_session(self, request):
        """Get session details"""
        session_id = request.match_info['session_id']
        
        try:
            session = await self.engine.session_manager.get_session(session_id)
            
            if session:
                return web.json_response({
                    'session_id': session.session_id,
                    'type': session.operation_type,
                    'status': session.status.value,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'targets_count': session.targets_count,
                    'results_count': session.results_count,
                    'errors_count': session.errors_count
                })
            else:
                return web.json_response({'error': 'Session not found'}, status=404)
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def close_session(self, request):
        """Close session"""
        session_id = request.match_info['session_id']
        
        try:
            await self.engine.session_manager.close_session(session_id)
            
            return web.json_response({
                'session_id': session_id,
                'status': 'closed'
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def export_data(self, request):
        """Export data"""
        try:
            data = await request.json()
            export_format = data.get('format', 'json')
            data_type = data.get('data_type', 'results')
            
            # This would integrate with exporter module
            export_id = hashlib.md5(f"{export_format}{data_type}{datetime.utcnow()}".encode()).hexdigest()[:8]
            
            return web.json_response({
                'export_id': export_id,
                'status': 'processing',
                'format': export_format,
                'estimated_completion': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_config(self, request):
        """Get configuration"""
        try:
            config = self.engine.config_manager.get_config()
            
            # Convert to dict (simplified)
            config_dict = {
                'core': {
                    'max_concurrent': config.core.max_concurrent,
                    'timeout': config.core.timeout,
                    'debug_mode': config.core.debug_mode
                },
                'targets': {
                    'default_ports': config.targets.default_ports,
                    'max_targets': config.targets.max_targets
                }
            }
            
            return web.json_response(config_dict)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_config(self, request):
        """Update configuration"""
        try:
            data = await request.json()
            
            # This would update configuration
            self.engine.config_manager.update_config(data)
            
            return web.json_response({
                'status': 'updated',
                'changes': data
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)


class APIModule:
    """REST API module wrapper"""
    
    def __init__(self, config_manager, logger, engine):
        """Initialize API module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        self.api = WWYVQRestAPI(engine)
        
        self.logger.info("🔌 REST API Interface initialized")
    
    async def run(self, host: str = "0.0.0.0", port: int = 8081):
        """Run REST API"""
        await self.api.run(host, port)
    
    async def shutdown(self):
        """Shutdown API module"""
        self.logger.info("🛑 REST API Interface shutdown completed")