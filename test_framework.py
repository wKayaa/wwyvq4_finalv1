#!/usr/bin/env python3
"""
Framework Test Script
Author: wKayaa
Date: 2025-06-24 17:02:05 UTC

Test the framework functionality end-to-end
"""

import sys
import os
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test all framework imports"""
    print("🧪 Testing framework imports...")
    
    try:
        from framework import ModularOrchestrator, WebInterface, APIServer, ConfigManager, FrameworkUtils
        print("✅ Framework imports successful")
        return True
    except ImportError as e:
        print(f"❌ Framework import failed: {e}")
        return False

def test_config():
    """Test configuration management"""
    print("🧪 Testing configuration...")
    
    try:
        from framework import ConfigManager
        
        config_manager = ConfigManager("/tmp/test_config.yaml")
        
        # Test setting and getting values
        config_manager.set("test.value", 123)
        value = config_manager.get("test.value")
        
        if value == 123:
            print("✅ Configuration management works")
            return True
        else:
            print(f"❌ Configuration test failed: expected 123, got {value}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_orchestrator():
    """Test orchestrator initialization"""
    print("🧪 Testing orchestrator...")
    
    try:
        from framework import ModularOrchestrator
        
        orchestrator = ModularOrchestrator("/tmp/test_config.yaml")
        
        # Test basic functionality
        status = orchestrator.get_status()
        
        if "session_id" in status and "modules" in status:
            print("✅ Orchestrator initialization successful")
            return True
        else:
            print("❌ Orchestrator test failed: missing expected status fields")
            return False
            
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def test_target_loading():
    """Test target loading functionality"""
    print("🧪 Testing target loading...")
    
    try:
        from framework import ModularOrchestrator, FrameworkUtils
        
        # Create a test targets file
        test_targets = ["127.0.0.1", "localhost", "192.168.1.0/30"]
        with open("/tmp/test_targets.txt", "w") as f:
            for target in test_targets:
                f.write(f"{target}\n")
        
        orchestrator = ModularOrchestrator("/tmp/test_config.yaml")
        targets = orchestrator.load_targets("/tmp/test_targets.txt")
        
        if len(targets) >= len(test_targets):
            print("✅ Target loading successful")
            return True
        else:
            print(f"❌ Target loading failed: expected {len(test_targets)}, got {len(targets)}")
            return False
            
    except Exception as e:
        print(f"❌ Target loading test failed: {e}")
        return False

async def test_exploitation():
    """Test basic exploitation functionality"""
    print("🧪 Testing exploitation...")
    
    try:
        from framework import ModularOrchestrator
        
        orchestrator = ModularOrchestrator("/tmp/test_config.yaml")
        
        # Test with minimal targets
        test_targets = ["127.0.0.1"]
        
        results = await orchestrator.run_k8s_exploitation(test_targets)
        
        if "session_id" in results and "targets_count" in results:
            print("✅ Exploitation test successful")
            return True
        else:
            print("❌ Exploitation test failed: missing expected result fields")
            return False
            
    except Exception as e:
        print(f"❌ Exploitation test failed: {e}")
        return False

def test_web_interface():
    """Test web interface initialization"""
    print("🧪 Testing web interface...")
    
    try:
        from framework import ModularOrchestrator, WebInterface
        
        orchestrator = ModularOrchestrator("/tmp/test_config.yaml")
        web_interface = WebInterface(orchestrator)
        
        url = web_interface.get_url()
        
        if url and "http://" in url:
            print("✅ Web interface initialization successful")
            return True
        else:
            print("❌ Web interface test failed: invalid URL")
            return False
            
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def test_api_server():
    """Test API server initialization"""
    print("🧪 Testing API server...")
    
    try:
        from framework import ModularOrchestrator, APIServer
        
        orchestrator = ModularOrchestrator("/tmp/test_config.yaml")
        api_server = APIServer(orchestrator)
        
        url = api_server.get_url()
        
        if url and "http://" in url:
            print("✅ API server initialization successful")
            return True
        else:
            print("❌ API server test failed: invalid URL")
            return False
            
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Framework Test Suite")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Orchestrator", test_orchestrator),
        ("Target Loading", test_target_loading),
        ("Web Interface", test_web_interface),
        ("API Server", test_api_server),
    ]
    
    async_tests = [
        ("Exploitation", test_exploitation),
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
    
    # Run asynchronous tests
    for test_name, test_func in async_tests:
        print(f"\n📋 Running {test_name} test...")
        if await test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Framework is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)