#!/usr/bin/env python3
"""
🧪 WWYVQ Framework v2.1 - Comprehensive Test Suite
Ultra-Organized Architecture Validation

Tests all major components and functionalities of the new architecture.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the wwyvq_v21 directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "wwyvq_v21"))

# Import all modules
from core.engine import WWYVQEngine
from core.config import ConfigurationManager
from core.session import SessionManager
from core.target import TargetManager
from core.logger import WWYVQLogger


class WWYVQTestSuite:
    """Comprehensive test suite for WWYVQ v2.1"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.engine = None
    
    def print_test_header(self, test_name: str):
        """Print test header"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {test_name}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, passed: bool, message: str = ""):
        """Print test result"""
        if passed:
            print(f"✅ {test_name}: PASSED {message}")
            self.passed_tests += 1
        else:
            print(f"❌ {test_name}: FAILED {message}")
            self.failed_tests += 1
    
    def print_summary(self):
        """Print test summary"""
        total_tests = self.passed_tests + self.failed_tests
        print(f"\n{'='*60}")
        print(f"🏁 Test Summary")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        
        if self.failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! WWYVQ v2.1 is ready!")
        else:
            print(f"\n⚠️ {self.failed_tests} tests failed. Please check the issues.")
    
    async def test_configuration_manager(self):
        """Test configuration manager"""
        self.print_test_header("Configuration Manager")
        
        try:
            # Test configuration loading
            config_manager = ConfigurationManager()
            config = config_manager.get_config()
            
            self.print_result("Config Loading", True, "- Configuration loaded successfully")
            
            # Test configuration validation
            validation_result = config_manager.validate_config()
            self.print_result("Config Validation", validation_result, "- Configuration is valid")
            
            # Test profile loading
            profiles = config_manager.list_profiles()
            self.print_result("Profile Management", len(profiles) > 0, f"- Found {len(profiles)} profiles")
            
            return config_manager
            
        except Exception as e:
            self.print_result("Configuration Manager", False, f"- Error: {e}")
            return None
    
    async def test_logger(self, config_manager):
        """Test logging system"""
        self.print_test_header("Logging System")
        
        try:
            # Test logger initialization
            logger = WWYVQLogger(config_manager)
            self.print_result("Logger Initialization", True, "- Logger initialized")
            
            # Test logging methods
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            self.print_result("Logging Methods", True, "- All log levels working")
            
            # Test log statistics
            stats = logger.get_log_statistics()
            self.print_result("Log Statistics", isinstance(stats, dict), f"- Stats: {stats}")
            
            return logger
            
        except Exception as e:
            self.print_result("Logging System", False, f"- Error: {e}")
            return None
    
    async def test_session_manager(self, config_manager):
        """Test session management"""
        self.print_test_header("Session Manager")
        
        try:
            # Test session manager initialization
            session_manager = SessionManager(config_manager)
            await session_manager.initialize()
            self.print_result("Session Manager Init", True, "- Session manager initialized")
            
            # Test session creation
            session_id = await session_manager.create_session("test_operation")
            self.print_result("Session Creation", session_id is not None, f"- Created session: {session_id}")
            
            # Test session retrieval
            session = await session_manager.get_session(session_id)
            self.print_result("Session Retrieval", session is not None, f"- Retrieved session: {session_id}")
            
            # Test session listing
            sessions = await session_manager.list_sessions()
            self.print_result("Session Listing", len(sessions) > 0, f"- Found {len(sessions)} sessions")
            
            return session_manager
            
        except Exception as e:
            self.print_result("Session Manager", False, f"- Error: {e}")
            return None
    
    async def test_target_manager(self, config_manager):
        """Test target management"""
        self.print_test_header("Target Manager")
        
        try:
            # Test target manager initialization
            target_manager = TargetManager(config_manager)
            await target_manager.initialize()
            self.print_result("Target Manager Init", True, "- Target manager initialized")
            
            # Test target addition
            success = await target_manager.add_target("127.0.0.1")
            self.print_result("Target Addition", success, "- Added localhost target")
            
            # Test CIDR expansion
            expanded = await target_manager._expand_cidr("192.168.1.0/30")
            self.print_result("CIDR Expansion", len(expanded) > 0, f"- Expanded to {len(expanded)} IPs")
            
            # Test target statistics
            stats = await target_manager.get_target_statistics()
            self.print_result("Target Statistics", isinstance(stats, dict), f"- Stats: {stats}")
            
            return target_manager
            
        except Exception as e:
            self.print_result("Target Manager", False, f"- Error: {e}")
            return None
    
    async def test_engine_initialization(self, config_path=None):
        """Test engine initialization"""
        self.print_test_header("Engine Initialization")
        
        try:
            # Test engine creation
            self.engine = WWYVQEngine(config_path)
            self.print_result("Engine Creation", True, f"- Engine ID: {self.engine.engine_id}")
            
            # Test engine initialization
            init_success = await self.engine.initialize()
            self.print_result("Engine Initialization", init_success, "- Engine initialized successfully")
            
            if init_success:
                # Test engine stats
                stats = self.engine.get_engine_stats()
                self.print_result("Engine Statistics", isinstance(stats, dict), f"- Stats collected")
                
                # Test active operations
                active_ops = self.engine.get_active_operations()
                self.print_result("Active Operations", isinstance(active_ops, dict), f"- {len(active_ops)} active operations")
            
            return self.engine
            
        except Exception as e:
            self.print_result("Engine Initialization", False, f"- Error: {e}")
            return None
    
    async def test_modules_loading(self):
        """Test module loading"""
        self.print_test_header("Module Loading")
        
        if not self.engine:
            self.print_result("Module Loading", False, "- Engine not available")
            return
        
        try:
            # Check loaded modules
            modules = self.engine.modules
            self.print_result("Modules Loaded", len(modules) > 0, f"- {len(modules)} modules loaded")
            
            # Test specific modules
            expected_modules = ['exploit', 'scrape', 'validator', 'notifier', 'exporter', 'utils']
            for module_name in expected_modules:
                if module_name in modules:
                    self.print_result(f"Module: {module_name}", True, f"- {module_name} module loaded")
                else:
                    self.print_result(f"Module: {module_name}", False, f"- {module_name} module missing")
            
        except Exception as e:
            self.print_result("Module Loading", False, f"- Error: {e}")
    
    async def test_operations(self):
        """Test basic operations"""
        self.print_test_header("Operations Testing")
        
        if not self.engine:
            self.print_result("Operations", False, "- Engine not available")
            return
        
        try:
            # Test scan operation
            scan_result = await self.engine.execute_operation(
                operation_type='scan',
                targets=['127.0.0.1']
            )
            self.print_result("Scan Operation", scan_result is not None, f"- Status: {scan_result.status.value}")
            
            # Test scrape operation
            scrape_result = await self.engine.execute_operation(
                operation_type='scrape',
                targets=['http://httpbin.org']
            )
            self.print_result("Scrape Operation", scrape_result is not None, f"- Status: {scrape_result.status.value}")
            
        except Exception as e:
            self.print_result("Operations", False, f"- Error: {e}")
    
    async def test_cli_interface(self):
        """Test CLI interface"""
        self.print_test_header("CLI Interface")
        
        try:
            from interface.cli import WWYVQCLIInterface
            
            if self.engine:
                cli = WWYVQCLIInterface(self.engine)
                self.print_result("CLI Creation", True, "- CLI interface created")
                
                # Test command structure
                commands = cli.commands
                self.print_result("CLI Commands", len(commands) > 0, f"- {len(commands)} commands available")
            else:
                self.print_result("CLI Interface", False, "- Engine not available")
            
        except Exception as e:
            self.print_result("CLI Interface", False, f"- Error: {e}")
    
    async def test_web_interface(self):
        """Test web interface"""
        self.print_test_header("Web Interface")
        
        try:
            from interface.web import WWYVQWebDashboard
            
            if self.engine:
                web_dashboard = WWYVQWebDashboard(self.engine)
                self.print_result("Web Dashboard", True, "- Web dashboard created")
            else:
                self.print_result("Web Interface", False, "- Engine not available")
            
        except Exception as e:
            self.print_result("Web Interface", False, f"- Error: {e}")
    
    async def test_api_interface(self):
        """Test API interface"""
        self.print_test_header("API Interface")
        
        try:
            from interface.api import WWYVQRestAPI
            
            if self.engine:
                rest_api = WWYVQRestAPI(self.engine)
                self.print_result("REST API", True, "- REST API created")
            else:
                self.print_result("API Interface", False, "- Engine not available")
            
        except Exception as e:
            self.print_result("API Interface", False, f"- Error: {e}")
    
    async def test_runner_script(self):
        """Test main runner script"""
        self.print_test_header("Runner Script")
        
        try:
            # Check if runner script exists
            runner_path = Path("wwyvq_runner.py")
            self.print_result("Runner Script Exists", runner_path.exists(), f"- Found at {runner_path}")
            
            if runner_path.exists():
                # Test import
                sys.path.insert(0, str(Path.cwd()))
                try:
                    import wwyvq_runner
                    self.print_result("Runner Import", True, "- Runner script imports successfully")
                except Exception as e:
                    self.print_result("Runner Import", False, f"- Import error: {e}")
            
        except Exception as e:
            self.print_result("Runner Script", False, f"- Error: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print(f"""
🔥 WWYVQ Framework v2.1 - Comprehensive Test Suite
Ultra-Organized Architecture Validation
{'='*60}
""")
        
        # Test core components
        config_manager = await self.test_configuration_manager()
        
        if config_manager:
            logger = await self.test_logger(config_manager)
            session_manager = await self.test_session_manager(config_manager)
            target_manager = await self.test_target_manager(config_manager)
            
            # Test engine
            engine = await self.test_engine_initialization()
            
            if engine:
                # Test modules and operations
                await self.test_modules_loading()
                await self.test_operations()
                
                # Test interfaces
                await self.test_cli_interface()
                await self.test_web_interface()
                await self.test_api_interface()
                
                # Shutdown engine
                await engine.shutdown()
        
        # Test runner script
        await self.test_runner_script()
        
        # Print summary
        self.print_summary()
        
        return self.failed_tests == 0


async def main():
    """Main test function"""
    test_suite = WWYVQTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print(f"\n🎉 WWYVQ v2.1 ARCHITECTURE VALIDATION COMPLETE!")
        print(f"✅ All systems operational - Framework ready for deployment!")
        return 0
    else:
        print(f"\n⚠️ SOME TESTS FAILED")
        print(f"❌ Please review and fix the issues before deployment")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)