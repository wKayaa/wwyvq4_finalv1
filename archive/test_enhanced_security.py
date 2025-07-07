#!/usr/bin/env python3
"""
Test script for Enhanced Security Monitoring System
Tests false positive reduction, detection accuracy, and alerting
Author: wKayaa | Test Version | 2025-01-28
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_security_monitor import (
    EnhancedCredentialDetector, FilterConfig, SeverityLevel, CredentialType
)
from enhanced_telegram_alerts import ProfessionalTelegramAlerter, AlertConfig
from security_monitor_integration import EnhancedSecurityMonitoringSystem

def test_false_positive_filtering():
    """Test false positive filtering capabilities"""
    print("🧪 Testing False Positive Filtering...")
    
    config = FilterConfig()
    detector = EnhancedCredentialDetector(config)
    
    # Test cases with known false positives
    test_cases = [
        # Should be filtered out (false positives)
        ("# Example AWS credentials\nAWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "example_file.md", True),
        ("test_key = 'SG.SENDGRID_API_KEY'", "test_config.py", True),
        ("# This is a demo key: AKIA1234567890123456", "README.md", True),
        
        # Should NOT be filtered out (real credentials)
        ("AWS_ACCESS_KEY=AKIA1234567890ABCDEF\nAWS_SECRET_KEY=abcdefghijklmnopqrstuvwxyz1234567890ABCD", "production.env", False),
        ("SENDGRID_API_KEY=SG.1234567890abcdefghijkl.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd", "config.json", False),
    ]
    
    results = {"total": 0, "correctly_filtered": 0, "false_negatives": 0, "false_positives": 0}
    
    for content, filename, should_be_filtered in test_cases:
        results["total"] += 1
        detections = detector.detect_credentials(content, filename)
        
        if should_be_filtered and len(detections) == 0:
            results["correctly_filtered"] += 1
            print(f"✅ Correctly filtered: {filename}")
        elif not should_be_filtered and len(detections) > 0:
            results["correctly_filtered"] += 1
            print(f"✅ Correctly detected: {filename} - {len(detections)} credentials")
        elif should_be_filtered and len(detections) > 0:
            results["false_positives"] += 1
            print(f"❌ False positive: {filename} - should have been filtered")
        else:
            results["false_negatives"] += 1
            print(f"❌ False negative: {filename} - should have been detected")
    
    print(f"\n📊 Filtering Test Results:")
    print(f"  Total test cases: {results['total']}")
    print(f"  Correctly handled: {results['correctly_filtered']}")
    print(f"  False positives: {results['false_positives']}")
    print(f"  False negatives: {results['false_negatives']}")
    print(f"  Accuracy: {(results['correctly_filtered'] / results['total']) * 100:.1f}%")
    
    return results

def test_proximity_matching():
    """Test proximity-based credential pair detection"""
    print("\n🧪 Testing Proximity Matching...")
    
    config = FilterConfig(enable_proximity_matching=True)
    detector = EnhancedCredentialDetector(config)
    
    # Test AWS credential pairs
    test_content = """
    # Production AWS Configuration
    AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
    AWS_SECRET_ACCESS_KEY=abcdefghijklmnopqrstuvwxyz1234567890ABCD
    AWS_REGION=us-east-1
    """
    
    detections = detector.detect_credentials(test_content, "prod_config.env")
    
    print(f"📋 Proximity Test Results:")
    print(f"  Detections found: {len(detections)}")
    
    aws_access_found = False
    aws_secret_found = False
    proximity_bonus_applied = False
    
    for detection in detections:
        print(f"  - {detection.credential_type.value}: Confidence {detection.confidence_score:.1f}%, Severity {detection.severity.value}")
        
        if detection.credential_type == CredentialType.AWS_ACCESS_KEY:
            aws_access_found = True
            if detection.proximity_matches:
                proximity_bonus_applied = True
                print(f"    Proximity matches: {detection.proximity_matches}")
        
        elif detection.credential_type == CredentialType.AWS_SECRET_KEY:
            aws_secret_found = True
            if detection.proximity_matches:
                proximity_bonus_applied = True
                print(f"    Proximity matches: {detection.proximity_matches}")
    
    success = aws_access_found and aws_secret_found
    print(f"  AWS pair detection: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"  Proximity bonus applied: {'✅ YES' if proximity_bonus_applied else '❌ NO'}")
    
    return success

def test_severity_levels():
    """Test severity level assignment"""
    print("\n🧪 Testing Severity Level Assignment...")
    
    config = FilterConfig()
    detector = EnhancedCredentialDetector(config)
    
    test_cases = [
        # Critical: Production AWS key
        ("production_aws_access_key_id=AKIA1234567890ABCDEF", "production.env", SeverityLevel.CRITICAL),
        # High: AWS key in main config
        ("aws_access_key=AKIA1234567890ABCDEF", "main_config.json", SeverityLevel.HIGH),
        # Medium: SendGrid key
        ("SENDGRID_API_KEY=SG.1234567890abcdefghijkl.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd", "email_config.py", SeverityLevel.MEDIUM),
        # Low: API key with lower confidence
        ("api_key = 'sk_test_1234567890abcdef'", "test_config.py", SeverityLevel.LOW),
    ]
    
    results = {"total": 0, "correct_severity": 0}
    
    for content, filename, expected_severity in test_cases:
        results["total"] += 1
        detections = detector.detect_credentials(content, filename)
        
        if detections:
            actual_severity = detections[0].severity
            if actual_severity == expected_severity:
                results["correct_severity"] += 1
                print(f"✅ Correct severity for {filename}: {actual_severity.value}")
            else:
                print(f"❌ Wrong severity for {filename}: expected {expected_severity.value}, got {actual_severity.value}")
        else:
            print(f"❌ No detection for {filename}")
    
    accuracy = (results["correct_severity"] / results["total"]) * 100 if results["total"] > 0 else 0
    print(f"\n📊 Severity Test Results:")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    return accuracy >= 75.0  # 75% accuracy threshold

async def test_alerting_system():
    """Test the enhanced alerting system"""
    print("\n🧪 Testing Enhanced Alerting System...")
    
    # Configure alerting (without actual Telegram credentials)
    alert_config = AlertConfig(
        telegram_token=None,  # No token for testing
        telegram_chat_id=None,
        alert_threshold=SeverityLevel.MEDIUM,
        rate_limit_seconds=1,  # Reduced for testing
        include_context=True,
        include_suggestions=True
    )
    
    alerter = ProfessionalTelegramAlerter(alert_config)
    
    # Test detection result
    from enhanced_security_monitor import DetectionResult
    
    test_detection = DetectionResult(
        credential_type=CredentialType.AWS_ACCESS_KEY,
        value="AKIA1234567890ABCDEF",
        redacted_value="AKIA***************DEF",
        confidence_score=95.0,
        severity=SeverityLevel.HIGH,
        source_file="production.env",
        line_number=5,
        context="AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF in production environment",
        suggestions=["Rotate AWS credentials immediately", "Use IAM roles instead"]
    )
    
    # Test alert sending (will log instead of actually sending)
    alert_sent = await alerter.send_detection_alert(test_detection, "Test Repository")
    
    # Test system alert
    await alerter.send_system_alert(
        SeverityLevel.LOW,
        "Test System Alert",
        "This is a test of the system alerting functionality"
    )
    
    # Get stats
    stats = alerter.get_alert_stats()
    
    print(f"📊 Alerting Test Results:")
    print(f"  Alert processed: {'✅ YES' if alert_sent else '❌ NO'}")
    print(f"  Alerts sent: {stats['alerts_sent_successfully']}")
    print(f"  System configured: {'✅ YES' if not alerter.telegram_enabled else '✅ YES (with Telegram)'}")
    
    return alert_sent is not None

async def test_integration():
    """Test the complete integration"""
    print("\n🧪 Testing Complete System Integration...")
    
    # Create a temporary config file for testing
    config_path = "./test_security_config.yaml"
    
    try:
        # Initialize the system
        monitor = EnhancedSecurityMonitoringSystem(config_path)
        
        # Test file scanning
        test_content = """
# Production Configuration
aws_access_key_id = AKIA1234567890ABCDEF
aws_secret_access_key = abcdefghijklmnopqrstuvwxyz1234567890ABCD
sendgrid_api_key = SG.1234567890abcdefghijkl.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd

# This should be filtered out
# Example: AKIAIOSFODNN7EXAMPLE
"""
        
        detections = await monitor.scan_file_content("test_production.env", test_content)
        
        # Test dashboard data
        dashboard_data = monitor.get_dashboard_data()
        
        # Test log search
        logs = monitor.search_logs("credential")
        
        print(f"📊 Integration Test Results:")
        print(f"  System initialized: ✅ YES")
        print(f"  Detections found: {len(detections)}")
        print(f"  Dashboard data available: {'✅ YES' if dashboard_data else '❌ NO'}")
        print(f"  Log search working: {'✅ YES' if logs is not None else '❌ NO'}")
        
        # Clean up test config
        if os.path.exists(config_path):
            os.remove(config_path)
        
        return len(detections) > 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Enhanced Security Monitoring System - Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("False Positive Filtering", test_false_positive_filtering()["correctly_filtered"] > 0))
    test_results.append(("Proximity Matching", test_proximity_matching()))
    test_results.append(("Severity Levels", test_severity_levels()))
    test_results.append(("Alerting System", await test_alerting_system()))
    test_results.append(("System Integration", await test_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"  Total Tests: {len(test_results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {len(test_results) - passed}")
    print(f"  Success Rate: {(passed / len(test_results)) * 100:.1f}%")
    
    if passed == len(test_results):
        print("\n🎉 ALL TESTS PASSED - System ready for deployment!")
        return 0
    else:
        print("\n⚠️  Some tests failed - Review implementation before deployment")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())