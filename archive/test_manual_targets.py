#!/usr/bin/env python3
"""
Quick test of manual target selection functionality
"""

import sys
import os
import asyncio

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_manual_target_validation():
    """Test the manual target validation methods"""
    print("🧪 Testing Manual Target Validation")
    print("=" * 40)
    
    # Import after path setup
    from optimized_f8s_mega_launch import OptimizedF8SMegaLauncher
    
    launcher = OptimizedF8SMegaLauncher(max_concurrent=100)
    
    # Test cases
    test_targets = [
        ("192.168.1.1:6443", True),
        ("kubernetes.local", True),
        ("10.0.0.1", True), 
        ("example.com:8443", True),
        ("192.168.1.0/24", True),
        ("256.256.256.256:6443", False),
        ("invalid:port:format", False),
        (":6443", False),
        ("", False)
    ]
    
    print("\nValidation Results:")
    for target, expected in test_targets:
        result = launcher._validate_manual_target(target)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {target:<25} -> {result} (expected: {expected})")
    
    print("\n🧪 Testing CIDR Expansion")
    cidr_test = "192.168.1.0/30"  # Small range for testing
    expanded = launcher._expand_cidr_range(cidr_test, max_ips=10)
    print(f"   {cidr_test} -> {len(expanded)} IPs: {expanded}")
    
    print("\n✅ Manual target validation tests completed")

if __name__ == "__main__":
    asyncio.run(test_manual_target_validation())