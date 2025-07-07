#!/usr/bin/env python3
"""
Enhanced Security Monitoring Integration
Main integration module that combines all enhanced monitoring capabilities
Author: wKayaa | Enhanced Version | 2025-01-28
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import argparse
import sys

# Import enhanced modules
from enhanced_security_monitor import (
    EnhancedCredentialDetector, FalsePositiveFilter, ProgressTracker,
    DetectionResult, FilterConfig, SeverityLevel, CredentialType
)
from enhanced_telegram_alerts import (
    ProfessionalTelegramAlerter, AlertingDashboard, AlertConfig
)
from enhanced_monitoring import (
    SearchableLogManager, RealTimeMonitor, ConfigurationManager,
    MonitoringConfig, SystemConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedSecurityMonitoringSystem:
    """Main enhanced security monitoring system"""
    
    def __init__(self, config_path: str = "./security_monitor_config.yaml"):
        self.config_manager = ConfigurationManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Initialize core components
        self.log_manager = SearchableLogManager(self.config.monitoring)
        self.real_time_monitor = RealTimeMonitor(self.config.monitoring, self.log_manager)
        
        # Initialize detection system
        self.detector = EnhancedCredentialDetector(self.config.filtering)
        self.progress_tracker = ProgressTracker()
        
        # Initialize alerting system
        self.alerter = ProfessionalTelegramAlerter(self.config.alerting)
        self.alert_dashboard = AlertingDashboard(self.alerter)
        
        # System state
        self.active_scans = {}
        self.scan_results = {}
        
        # Initialize logging
        self.log_manager.add_log_entry(
            "INFO", 
            "Enhanced Security Monitoring System initialized", 
            "system",
            {"version": "2.0", "operator": self.config.operator_name}
        )
        
        logger.info("Enhanced Security Monitoring System ready")
    
    async def scan_targets(self, targets: List[str], scan_name: Optional[str] = None) -> Dict[str, Any]:
        """Perform enhanced security scan on targets"""
        
        scan_id = scan_name or f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Register scan with monitoring
        scan_info = {
            "scan_id": scan_id,
            "targets": len(targets),
            "start_time": datetime.utcnow().isoformat(),
            "operator": self.config.operator_name
        }
        
        self.real_time_monitor.register_scan(scan_id, scan_info)
        self.log_manager.add_log_entry("INFO", f"Starting scan: {scan_id}", "scan", scan_info)
        
        # Send scan start alert
        await self.alerter.send_system_alert(
            SeverityLevel.LOW,
            "Security Scan Started",
            f"Starting scan of {len(targets)} targets with ID: {scan_id}"
        )
        
        # Initialize results
        scan_results = {
            "scan_id": scan_id,
            "start_time": datetime.utcnow().isoformat(),
            "targets_scanned": 0,
            "targets_total": len(targets),
            "detections": [],
            "compromised_targets": {},
            "false_positives_filtered": 0,
            "alerts_sent": 0,
            "errors": []
        }
        
        # Start progress tracking
        self.progress_tracker.start_scan(len(targets))
        
        # Create aiohttp session for scanning
        connector = aiohttp.TCPConnector(
            ssl=False,
            keepalive_timeout=30,
            limit=100,
            limit_per_host=20
        )
        
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Process targets in chunks
            chunk_size = 50
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i + chunk_size]
                
                # Create tasks for this chunk
                tasks = [self._scan_single_target(session, target, scan_results) for target in chunk]
                
                # Execute chunk
                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for target, result in zip(chunk, chunk_results):
                    if isinstance(result, Exception):
                        error_msg = f"Error scanning {target}: {result}"
                        scan_results["errors"].append(error_msg)
                        self.log_manager.add_log_entry("ERROR", error_msg, "scan")
                    
                    scan_results["targets_scanned"] += 1
                
                # Update progress
                progress_info = {
                    "completed": scan_results["targets_scanned"],
                    "total": len(targets),
                    "percentage": (scan_results["targets_scanned"] / len(targets)) * 100,
                    "detections": len(scan_results["detections"])
                }
                
                self.real_time_monitor.update_scan_progress(scan_id, progress_info)
                
                # Small delay between chunks
                await asyncio.sleep(0.5)
        
        # Finalize scan results
        scan_results["end_time"] = datetime.utcnow().isoformat()
        scan_results["duration"] = str(datetime.utcnow() - datetime.fromisoformat(scan_results["start_time"]))
        scan_results["confirmed_detections"] = len(scan_results["detections"]) - scan_results["false_positives_filtered"]
        
        # Complete monitoring
        self.real_time_monitor.complete_scan(scan_id, scan_results)
        
        # Send completion alert
        await self.alerter.send_scan_summary(scan_results, "Enhanced Security Scan")
        
        # Store results
        self.scan_results[scan_id] = scan_results
        
        # Save results to file
        await self._save_scan_results(scan_results)
        
        self.log_manager.add_log_entry(
            "INFO", 
            f"Scan completed: {scan_id}", 
            "scan", 
            {
                "duration": scan_results["duration"],
                "detections": len(scan_results["detections"]),
                "targets": scan_results["targets_scanned"]
            }
        )
        
        return scan_results
    
    async def _scan_single_target(self, session: aiohttp.ClientSession, target: str, scan_results: Dict[str, Any]):
        """Scan a single target for credentials"""
        
        try:
            # Common K8s ports and endpoints
            ports = [6443, 8443, 8080, 10250, 2379, 2380]
            endpoints = [
                "/api/v1/secrets", 
                "/api/v1/configmaps", 
                "/.env",
                "/admin", 
                "/metrics", 
                "/debug", 
                "/version",
                "/api/v1/namespaces/kube-system/secrets",
                "/api/v1/pods",
                "/healthz"
            ]
            
            target_detections = []
            
            for port in ports:
                base_url = f"https://{target}:{port}" if port in [6443, 8443] else f"http://{target}:{port}"
                
                for endpoint in endpoints:
                    try:
                        test_url = f"{base_url}{endpoint}"
                        
                        # Update progress
                        self.progress_tracker.update_progress(test_url, "pattern_matching")
                        
                        async with session.get(test_url, ssl=False) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Detect credentials in content
                                detections = self.detector.detect_credentials(content, test_url)
                                
                                for detection in detections:
                                    # Record detection
                                    target_detections.append(detection)
                                    scan_results["detections"].append(detection)
                                    
                                    # Send alert
                                    alert_sent = await self.alerter.send_detection_alert(detection, f"Target: {target}")
                                    if alert_sent:
                                        scan_results["alerts_sent"] += 1
                                    
                                    # Record in dashboard
                                    self.alert_dashboard.record_alert(detection, alert_sent)
                                    
                                    # Log detection
                                    self.log_manager.add_log_entry(
                                        "WARNING",
                                        f"Credential detected: {detection.credential_type.value}",
                                        "detection",
                                        {
                                            "target": target,
                                            "endpoint": endpoint,
                                            "confidence": detection.confidence_score,
                                            "severity": detection.severity.value
                                        }
                                    )
                                
                                # Mark target as compromised if credentials found
                                if target_detections:
                                    if target not in scan_results["compromised_targets"]:
                                        scan_results["compromised_targets"][target] = {
                                            "first_detection": datetime.utcnow().isoformat(),
                                            "detections": 0,
                                            "endpoints": []
                                        }
                                    
                                    scan_results["compromised_targets"][target]["detections"] += len(detections)
                                    if endpoint not in scan_results["compromised_targets"][target]["endpoints"]:
                                        scan_results["compromised_targets"][target]["endpoints"].append(endpoint)
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        self.log_manager.add_log_entry("DEBUG", f"Error accessing {test_url}: {e}", "scan")
                        continue
            
            # Update progress
            self.progress_tracker.file_completed(target, len(target_detections), self.detector.filter.stats.get('false_positives', 0))
            
        except Exception as e:
            self.log_manager.add_log_entry("ERROR", f"Error scanning target {target}: {e}", "scan")
    
    async def scan_file_content(self, file_path: str, content: str) -> List[DetectionResult]:
        """Scan file content for credentials"""
        
        self.log_manager.add_log_entry("DEBUG", f"Scanning file: {file_path}", "file_scan")
        
        # Update progress
        self.progress_tracker.update_progress(file_path, "file_filtering")
        
        # Detect credentials
        detections = self.detector.detect_credentials(content, file_path)
        
        # Process each detection
        processed_detections = []
        for detection in detections:
            # Send alert if enabled
            if self.config.alerting.telegram_token:
                alert_sent = await self.alerter.send_detection_alert(detection, "File Scan")
                self.alert_dashboard.record_alert(detection, alert_sent)
            
            processed_detections.append(detection)
            
            # Log detection
            self.log_manager.add_log_entry(
                "WARNING" if detection.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL] else "INFO",
                f"File credential detected: {detection.credential_type.value}",
                "file_detection",
                {
                    "file": file_path,
                    "line": detection.line_number,
                    "confidence": detection.confidence_score,
                    "severity": detection.severity.value
                }
            )
        
        return processed_detections
    
    async def _save_scan_results(self, scan_results: Dict[str, Any]):
        """Save scan results to file"""
        try:
            output_dir = Path(self.config.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save main results
            results_file = output_dir / f"{scan_results['scan_id']}_results.json"
            with open(results_file, 'w') as f:
                # Convert DetectionResult objects to dictionaries for JSON serialization
                serializable_results = scan_results.copy()
                serializable_results["detections"] = [
                    {
                        "credential_type": det.credential_type.value,
                        "redacted_value": det.redacted_value,
                        "confidence_score": det.confidence_score,
                        "severity": det.severity.value,
                        "source_file": det.source_file,
                        "line_number": det.line_number,
                        "context": det.context[:200],  # Truncate context
                        "timestamp": det.timestamp,
                        "suggestions": det.suggestions
                    }
                    for det in scan_results["detections"]
                ]
                
                json.dump(serializable_results, f, indent=2, default=str)
            
            # Export logs
            log_export = self.log_manager.export_logs("json", {"category": "scan"})
            log_file = output_dir / f"{scan_results['scan_id']}_logs.json"
            with open(log_file, 'w') as f:
                f.write(log_export)
            
            self.log_manager.add_log_entry("INFO", f"Results saved to {results_file}", "system")
            
        except Exception as e:
            self.log_manager.add_log_entry("ERROR", f"Failed to save results: {e}", "system")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "system_status": self.real_time_monitor.get_dashboard_data(),
            "alert_metrics": self.alert_dashboard.get_dashboard_data(),
            "detection_stats": self.detector.filter.stats,
            "configuration": {
                "scan_name": self.config.scan_name,
                "operator": self.config.operator_name,
                "telegram_enabled": self.alerter.telegram_enabled,
                "monitoring_active": self.real_time_monitor.running
            },
            "recent_scans": {
                scan_id: {
                    "start_time": results["start_time"],
                    "duration": results.get("duration", "In Progress"),
                    "detections": len(results["detections"]),
                    "targets": results["targets_scanned"]
                }
                for scan_id, results in list(self.scan_results.items())[-10:]  # Last 10 scans
            }
        }
    
    def search_logs(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Search system logs"""
        return self.log_manager.search_logs(query, **filters)
    
    def search_alerts(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search alert history"""
        return self.alert_dashboard.search_alerts(query, limit)
    
    def start_real_time_monitoring(self):
        """Start real-time monitoring"""
        self.real_time_monitor.start_monitoring()
    
    def stop_real_time_monitoring(self):
        """Stop real-time monitoring"""
        self.real_time_monitor.stop_monitoring()
    
    async def update_configuration(self, config_updates: Dict[str, Any]):
        """Update system configuration"""
        self.config_manager.update_config(config_updates)
        self.config = self.config_manager.get_config()
        
        # Update components with new config
        self.detector = EnhancedCredentialDetector(self.config.filtering)
        self.alerter = ProfessionalTelegramAlerter(self.config.alerting)
        
        self.log_manager.add_log_entry("INFO", "Configuration updated", "system", config_updates)
    
    async def process_queued_alerts(self):
        """Process any queued alerts"""
        await self.alerter.process_queued_alerts()

async def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Enhanced Security Monitoring System')
    parser.add_argument('--config', default='./security_monitor_config.yaml', help='Configuration file path')
    parser.add_argument('--targets', nargs='+', help='Target URLs to scan')
    parser.add_argument('--file', help='File to scan for credentials')
    parser.add_argument('--scan-name', help='Custom scan name')
    parser.add_argument('--dashboard', action='store_true', help='Start dashboard mode')
    
    args = parser.parse_args()
    
    # Initialize system
    monitor = EnhancedSecurityMonitoringSystem(args.config)
    
    if args.dashboard:
        # Start real-time monitoring
        monitor.start_real_time_monitoring()
        
        print("🚀 Enhanced Security Monitoring Dashboard")
        print("=" * 50)
        
        try:
            while True:
                dashboard_data = monitor.get_dashboard_data()
                
                # Clear screen and display dashboard
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🚀 Enhanced Security Monitoring Dashboard")
                print("=" * 50)
                print(f"Status: {'🟢 Active' if monitor.real_time_monitor.running else '🔴 Inactive'}")
                print(f"Operator: {monitor.config.operator_name}")
                print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print()
                
                # System metrics
                print("📊 System Metrics:")
                system_status = dashboard_data["system_status"]
                print(f"  Active Scans: {len(system_status['active_scans'])}")
                print(f"  Uptime: {system_status['system_status']['uptime']}")
                print()
                
                # Detection stats
                print("🔍 Detection Statistics:")
                detection_stats = dashboard_data["detection_stats"]
                print(f"  Total Detections: {detection_stats.get('total_detections', 0)}")
                print(f"  Confirmed Credentials: {detection_stats.get('confirmed_credentials', 0)}")
                print(f"  False Positives Filtered: {detection_stats.get('false_positives', 0)}")
                print()
                
                # Recent alerts
                print("🚨 Recent Alerts:")
                alert_data = dashboard_data["alert_metrics"]
                recent_alerts = alert_data.get("recent_alerts", [])
                for alert in recent_alerts[-5:]:  # Last 5 alerts
                    print(f"  {alert['timestamp'][:19]} - {alert['severity']} - {alert['credential_type']}")
                
                print("\nPress Ctrl+C to exit...")
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\nShutting down dashboard...")
            monitor.stop_real_time_monitoring()
    
    elif args.targets:
        # Scan targets
        print(f"🚀 Starting enhanced security scan of {len(args.targets)} targets")
        results = await monitor.scan_targets(args.targets, args.scan_name)
        
        print("\n📊 Scan Results:")
        print(f"  Targets Scanned: {results['targets_scanned']}")
        print(f"  Credentials Detected: {len(results['detections'])}")
        print(f"  Compromised Targets: {len(results['compromised_targets'])}")
        print(f"  Alerts Sent: {results['alerts_sent']}")
        
    elif args.file:
        # Scan file
        if os.path.exists(args.file):
            with open(args.file, 'r') as f:
                content = f.read()
            
            print(f"🔍 Scanning file: {args.file}")
            detections = await monitor.scan_file_content(args.file, content)
            
            print(f"\n📊 File Scan Results:")
            print(f"  Credentials Detected: {len(detections)}")
            
            for detection in detections:
                print(f"  - {detection.credential_type.value} (Line {detection.line_number}, Confidence: {detection.confidence_score:.1f}%)")
        else:
            print(f"❌ File not found: {args.file}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())