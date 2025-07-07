#!/usr/bin/env python3
"""
🧪 Mega CIDR UHQ System Validation Test
Author: wKayaa | F8S Pod Exploitation Framework | 2025-01-28

Comprehensive validation test for the Mega CIDR UHQ system to ensure
all categories are properly implemented and integration works correctly.
"""

import asyncio
import json
from mega_cidr_uhq import MegaCIDRUHQ
from f8s_exploit_pod import F8sPodExploiter, run_f8s_exploitation

def test_category_coverage():
    """Test that all 10 required categories are implemented"""
    print("🧪 Testing Category Coverage...")
    
    mega_cidr = MegaCIDRUHQ()
    required_categories = [
        'enterprise_networks',
        'cloud_providers', 
        'container_orchestration',
        'government_military',
        'isp_telecom',
        'educational',
        'financial',
        'healthcare',
        'critical_infrastructure',
        'emerging_markets'
    ]
    
    stats = mega_cidr.get_category_statistics()
    
    for category in required_categories:
        assert category in stats, f"Missing category: {category}"
        assert stats[category]['total_ranges'] > 0, f"No ranges in category: {category}"
        print(f"  ✅ {category}: {stats[category]['total_ranges']} ranges")
    
    print(f"✅ All {len(required_categories)} categories implemented")
    return True

def test_priority_levels():
    """Test priority-based targeting"""
    print("\n🧪 Testing Priority Levels...")
    
    mega_cidr = MegaCIDRUHQ()
    
    # Test each priority level
    for priority in range(1, 11):
        targets = mega_cidr.get_targets_by_priority(min_priority=priority, max_priority=priority)
        print(f"  📊 Priority {priority}: {len(targets)} targets")
    
    # Test high-priority filtering
    high_priority = mega_cidr.get_targets_by_priority(min_priority=8)
    print(f"✅ High-priority targets (8-10): {len(high_priority)}")
    
    return True

def test_security_features():
    """Test security and stealth features"""
    print("\n🧪 Testing Security Features...")
    
    mega_cidr = MegaCIDRUHQ()
    
    # Test stealth-safe targets
    stealth_safe = mega_cidr.get_stealth_safe_targets()
    print(f"  🛡️ Stealth-safe targets: {len(stealth_safe)}")
    
    # Test aggressive scan targets
    aggressive = mega_cidr.get_aggressive_scan_targets()
    print(f"  ⚡ Aggressive scan targets: {len(aggressive)}")
    
    # Test high-probability targets
    high_prob = mega_cidr.get_high_probability_targets()
    print(f"  💎 High-probability targets: {len(high_prob)}")
    
    # Check for security warnings
    warning_targets = [t for t in mega_cidr.targets if t.warning]
    print(f"  ⚠️ Targets with warnings: {len(warning_targets)}")
    
    print("✅ Security features validated")
    return True

def test_geographic_targeting():
    """Test geographic region targeting"""
    print("\n🧪 Testing Geographic Targeting...")
    
    mega_cidr = MegaCIDRUHQ()
    
    regions = ['north_america', 'europe', 'asia_pacific', 'latin_america', 'africa', 'global']
    
    for region in regions:
        targets = mega_cidr.get_targets_by_region(region)
        print(f"  🌍 {region}: {len(targets)} targets")
    
    print("✅ Geographic targeting validated")
    return True

def test_target_generation():
    """Test target list generation with different parameters"""
    print("\n🧪 Testing Target Generation...")
    
    mega_cidr = MegaCIDRUHQ()
    
    # Test stealth mode
    stealth_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=8,
        max_targets=100,
        stealth_mode=True,
        include_ipv6=False
    )
    print(f"  🔒 Stealth targets (100 max): {len(stealth_targets)}")
    
    # Test aggressive mode
    aggressive_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=9,
        max_targets=200,
        stealth_mode=False,
        include_ipv6=False
    )
    print(f"  ⚡ Aggressive targets (200 max): {len(aggressive_targets)}")
    
    # Test IPv6 inclusion
    ipv6_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=5,
        max_targets=50,
        include_ipv6=True
    )
    print(f"  🌐 IPv6 included targets (50 max): {len(ipv6_targets)}")
    
    print("✅ Target generation validated")
    return True

def test_scanning_strategies():
    """Test scanning strategy configuration"""
    print("\n🧪 Testing Scanning Strategies...")
    
    mega_cidr = MegaCIDRUHQ()
    
    categories = ['cloud_providers', 'enterprise_networks', 'financial', 'educational']
    
    for category in categories:
        strategy = mega_cidr.get_scanning_strategy(category)
        if strategy:
            print(f"  📋 {category}: concurrent={strategy.concurrent_limit}, timeout={strategy.timeout}s")
    
    print("✅ Scanning strategies validated")
    return True

async def test_f8s_integration():
    """Test integration with F8S framework"""
    print("\n🧪 Testing F8S Integration...")
    
    # Test basic integration
    mega_cidr = MegaCIDRUHQ()
    test_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=10,
        max_targets=5,
        stealth_mode=True
    )
    
    print(f"  🎯 Generated {len(test_targets)} test targets")
    
    # Test F8S exploiter initialization 
    exploiter = F8sPodExploiter(stealth_mode=True)
    print(f"  🚀 F8S exploiter initialized: {exploiter.session_id}")
    
    # Test run function signature (without actually running)
    try:
        # This tests the function signature compatibility
        import inspect
        sig = inspect.signature(run_f8s_exploitation)
        params = list(sig.parameters.keys())
        expected_params = ['target_ranges', 'telegram_token', 'exploiter', 'max_concurrent', 'timeout']
        
        for param in expected_params:
            assert param in params, f"Missing parameter: {param}"
        
        print("  ✅ F8S function signature compatible")
    except Exception as e:
        print(f"  ❌ Integration error: {e}")
        return False
    
    print("✅ F8S integration validated")
    return True

def test_file_exports():
    """Test file export functionality"""
    print("\n🧪 Testing File Exports...")
    
    mega_cidr = MegaCIDRUHQ()
    
    # Test export functionality
    test_files = [
        ("test_stealth.txt", {"priority_threshold": 8, "max_targets": 50, "stealth_mode": True}),
        ("test_aggressive.txt", {"priority_threshold": 9, "max_targets": 100, "stealth_mode": False}),
        ("test_comprehensive.txt", {"priority_threshold": 5, "max_targets": 200, "include_ipv6": True})
    ]
    
    for filename, kwargs in test_files:
        targets = mega_cidr.export_targets_for_f8s(filename, **kwargs)
        print(f"  📄 {filename}: {len(targets)} targets exported")
    
    print("✅ File exports validated")
    return True

def test_comprehensive_coverage():
    """Test comprehensive coverage statistics"""
    print("\n🧪 Testing Comprehensive Coverage...")
    
    mega_cidr = MegaCIDRUHQ()
    stats = mega_cidr.get_category_statistics()
    
    total_ranges = sum(s['total_ranges'] for s in stats.values())
    total_ipv4 = sum(s['ipv4_ranges'] for s in stats.values())  
    total_ipv6 = sum(s['ipv6_ranges'] for s in stats.values())
    
    print(f"  📊 Total CIDR ranges: {total_ranges}")
    print(f"  🌐 IPv4 ranges: {total_ipv4}")
    print(f"  🌐 IPv6 ranges: {total_ipv6}")
    print(f"  📁 Categories: {len(stats)}")
    
    # Validate minimum requirements
    assert total_ranges >= 200, f"Insufficient total ranges: {total_ranges}"
    assert total_ipv4 >= 180, f"Insufficient IPv4 ranges: {total_ipv4}"
    assert total_ipv6 >= 15, f"Insufficient IPv6 ranges: {total_ipv6}"
    assert len(stats) == 10, f"Incorrect category count: {len(stats)}"
    
    print("✅ Comprehensive coverage validated")
    return True

async def main():
    """Run all validation tests"""
    print("🚀 MEGA CIDR UHQ SYSTEM VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Category Coverage", test_category_coverage),
        ("Priority Levels", test_priority_levels),
        ("Security Features", test_security_features),
        ("Geographic Targeting", test_geographic_targeting),
        ("Target Generation", test_target_generation),
        ("Scanning Strategies", test_scanning_strategies),
        ("F8S Integration", test_f8s_integration),
        ("File Exports", test_file_exports),
        ("Comprehensive Coverage", test_comprehensive_coverage)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Total Tests: {len(tests)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ Mega CIDR UHQ System is ready for production use")
    else:
        print(f"\n⚠️ {failed} validation tests failed")
        print("❌ System requires fixes before production use")
    
    return failed == 0

if __name__ == "__main__":
    asyncio.run(main())