#!/usr/bin/env python3
"""
API Server Module - REST API Interface
Author: wKayaa
Date: 2025-06-24 17:02:05 UTC

Provides a REST API interface for the framework.
"""

import asyncio
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, List
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response, json_response


class APIServer:
    """REST API server for the framework"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger('framework.api')
        self.app = None
        self.runner = None
        self.site = None
        self.running = False
        
        self.port = orchestrator.config['network']['api_server_port']
        self.host = orchestrator.config['network']['bind_address']
        
        self.logger.info(f"🔌 APIServer initialized on {self.host}:{self.port}")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        self.app = web.Application()
        
        # Health and status endpoints
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/health', self.health)
        self.app.router.add_get('/status', self.status)
        self.app.router.add_get('/config', self.get_config)
        self.app.router.add_post('/config', self.update_config)
        
        # Exploitation endpoints
        self.app.router.add_post('/exploit/k8s', self.exploit_k8s)
        self.app.router.add_post('/exploit/mail', self.exploit_mail)
        self.app.router.add_post('/exploit/full', self.exploit_full)
        
        # Target management
        self.app.router.add_post('/targets/load', self.load_targets)
        self.app.router.add_get('/targets/expand', self.expand_targets)
        
        # Session management
        self.app.router.add_get('/session/info', self.session_info)
        
        # Add CORS headers
        self.app.middlewares.append(self._cors_handler)
    
    @web.middleware
    async def _cors_handler(self, request: Request, handler):
        """Handle CORS headers"""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    async def index(self, request: Request) -> Response:
        """API root endpoint"""
        return json_response({
            "name": "AIO Exploit Framework API",
            "version": "1.0.0",
            "author": "wKayaa",
            "session_id": self.orchestrator.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "config": "/config",
                "exploit": {
                    "k8s": "/exploit/k8s",
                    "mail": "/exploit/mail", 
                    "full": "/exploit/full"
                },
                "targets": {
                    "load": "/targets/load",
                    "expand": "/targets/expand"
                },
                "session": "/session/info"
            }
        })
    
    async def health(self, request: Request) -> Response:
        """Health check endpoint"""
        return json_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": str(datetime.utcnow() - self.orchestrator.start_time)
        })
    
    async def status(self, request: Request) -> Response:
        """Framework status endpoint"""
        return json_response(self.orchestrator.get_status())
    
    async def get_config(self, request: Request) -> Response:
        """Get framework configuration"""
        return json_response(self.orchestrator.config)
    
    async def update_config(self, request: Request) -> Response:
        """Update framework configuration"""
        try:
            data = await request.json()
            success = self.orchestrator.config_manager.update(data)
            
            if success:
                return json_response({
                    "success": True,
                    "message": "Configuration updated successfully",
                    "config": self.orchestrator.config
                })
            else:
                return json_response({
                    "success": False,
                    "error": "Failed to save configuration"
                }, status=500)
                
        except Exception as e:
            self.logger.error(f"Config update error: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=400)
    
    async def exploit_k8s(self, request: Request) -> Response:
        """Start K8s exploitation"""
        try:
            data = await request.json()
            targets = data.get('targets', [])
            
            if not targets:
                return json_response({
                    "success": False,
                    "error": "No targets provided"
                }, status=400)
            
            self.logger.info(f"🔌 API: Starting K8s exploitation on {len(targets)} targets")
            results = await self.orchestrator.run_k8s_exploitation(targets)
            
            return json_response({
                "success": True,
                "results": results
            })
            
        except Exception as e:
            self.logger.error(f"K8s exploitation API error: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def exploit_mail(self, request: Request) -> Response:
        """Start mail hunting"""
        try:
            data = await request.json()
            targets = data.get('targets', [])
            
            if not targets:
                return json_response({
                    "success": False,
                    "error": "No targets provided"
                }, status=400)
            
            self.logger.info(f"🔌 API: Starting mail hunting on {len(targets)} targets")
            results = await self.orchestrator.run_mail_hunting(targets)
            
            return json_response({
                "success": True,
                "results": results
            })
            
        except Exception as e:
            self.logger.error(f"Mail hunting API error: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def exploit_full(self, request: Request) -> Response:
        """Start full exploitation pipeline"""
        try:
            data = await request.json()
            targets = data.get('targets', [])
            mode = data.get('mode', 'all')
            
            if not targets:
                return json_response({
                    "success": False,
                    "error": "No targets provided"
                }, status=400)
            
            self.logger.info(f"🔌 API: Starting full exploitation on {len(targets)} targets")
            results = await self.orchestrator.run_full_exploitation(targets, mode)
            
            return json_response({
                "success": True,
                "results": results
            })
            
        except Exception as e:
            self.logger.error(f"Full exploitation API error: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def load_targets(self, request: Request) -> Response:
        """Load targets from file"""
        try:
            data = await request.json()
            file_path = data.get('file_path')
            
            if not file_path:
                return json_response({
                    "success": False,
                    "error": "No file_path provided"
                }, status=400)
            
            targets = self.orchestrator.load_targets(file_path)
            
            return json_response({
                "success": True,
                "targets": targets,
                "count": len(targets)
            })
            
        except Exception as e:
            self.logger.error(f"Load targets API error: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def expand_targets(self, request: Request) -> Response:
        """Expand CIDR targets"""
        try:
            targets = request.query.get('targets', '').split(',')
            targets = [t.strip() for t in targets if t.strip()]
            
            if not targets:
                return json_response({
                    "success": False,
                    "error": "No targets provided"
                }, status=400)
            
            from .utils import FrameworkUtils
            expanded = FrameworkUtils.expand_cidr_targets(targets)
            
            return json_response({
                "success": True,
                "original_targets": targets,
                "expanded_targets": expanded,
                "original_count": len(targets),
                "expanded_count": len(expanded)
            })
            
        except Exception as e:
            self.logger.error(f"Expand targets API error: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def session_info(self, request: Request) -> Response:
        """Get session information"""
        return json_response({
            "session_id": self.orchestrator.session_id,
            "start_time": self.orchestrator.start_time.isoformat(),
            "uptime": str(datetime.utcnow() - self.orchestrator.start_time),
            "api_server": {
                "host": self.host,
                "port": self.port,
                "running": self.running
            }
        })
    
    def run(self):
        """Run the API server"""
        async def start_server():
            try:
                self.running = True
                self.runner = web.AppRunner(self.app)
                await self.runner.setup()
                
                self.site = web.TCPSite(self.runner, self.host, self.port)
                await self.site.start()
                
                self.logger.info(f"🔌 API server started on {self.host}:{self.port}")
                
                # Keep the server running
                while self.running:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"❌ API server failed: {e}")
                self.running = False
            finally:
                if self.runner:
                    await self.runner.cleanup()
        
        # Run the server
        try:
            asyncio.run(start_server())
        except Exception as e:
            self.logger.error(f"❌ Failed to start API server: {e}")
    
    def start_async(self):
        """Start API server in a separate thread"""
        if self.running:
            self.logger.warning("⚠️ API server already running")
            return
        
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        self.logger.info("🔌 API server started in background thread")
    
    def stop(self):
        """Stop the API server"""
        self.running = False
        self.logger.info("⏹️ Stopping API server...")
    
    def get_url(self) -> str:
        """Get the API server URL"""
        return f"http://{self.host}:{self.port}"