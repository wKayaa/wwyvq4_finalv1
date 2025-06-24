#!/usr/bin/env python3
"""
Simplified test for Enhanced Security Monitoring System core functionality
Tests the detection logic without external dependencies
Author: wKayaa | Test Version | 2025-01-28
"""

import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

# Simplified versions of core classes for testing
class SeverityLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CredentialType(Enum):
    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    SENDGRID_KEY = "sendgrid_key"
    JWT_TOKEN = "jwt_token"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"

@dataclass
class SimplifiedDetectionResult:
    credential_type: CredentialType
    value: str
    confidence_score: float
    severity: SeverityLevel
    source_file: str
    line_number: int
    is_filtered: bool = False
    filter_reason: Optional[str] = None

class SimplifiedEnhancedDetector:
    """Simplified version for testing core functionality"""
    
    def __init__(self):
        self.patterns = {
            CredentialType.AWS_ACCESS_KEY: r'AKIA[0-9A-Z]{16}',
            CredentialType.AWS_SECRET_KEY: r'[A-Za-z0-9/+=]{40}',
            CredentialType.SENDGRID_KEY: r'SG\.[a-zA-Z0-9_-]{22,}\.[a-zA-Z0-9_-]{43,}',
            CredentialType.JWT_TOKEN: r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
        }
        
        self.test_patterns = {
            'AKIAIOSFODNN7EXAMPLE',
            'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'SG.SENDGRID_API_KEY',
            'your-api-key-here',
            'INSERT_YOUR_KEY_HERE'
        }
        
        self.test_keywords = {'example', 'test', 'demo', 'sample', 'fake', 'dummy'}
        
        self.stats = {
            'total_detections': 0,
            'filtered_out': 0,
            'confirmed_credentials': 0
        }
    
    def detect_credentials(self, content: str, source_file: str) -> List[SimplifiedDetectionResult]:
        """Detect credentials with enhanced filtering"""
        results = []
        
        # Check if file should be scanned
        if self._should_skip_file(source_file):
            return results
        
        lines = content.split('\n')
        
        for cred_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                value = match.group(0)
                
                # Calculate confidence
                confidence = self._calculate_confidence(cred_type, value, content)
                
                # Determine severity
                severity = self._determine_severity(cred_type, confidence, content)
                
                # Apply filtering
                is_filtered, filter_reason = self._apply_filter(value, content, source_file)
                
                detection = SimplifiedDetectionResult(
                    credential_type=cred_type,
                    value=value,
                    confidence_score=confidence,
                    severity=severity,
                    source_file=source_file,
                    line_number=line_num,
                    is_filtered=is_filtered,
                    filter_reason=filter_reason
                )
                
                self.stats['total_detections'] += 1
                
                if not is_filtered:
                    results.append(detection)
                    self.stats['confirmed_credentials'] += 1
                else:
                    self.stats['filtered_out'] += 1
        
        return results
    
    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped"""
        skip_extensions = {'.md', '.txt', '.rst', '.pdf'}
        skip_paths = {'docs/', 'samples/', 'examples/', 'test/', 'README'}
        
        file_lower = file_path.lower()
        
        for ext in skip_extensions:
            if file_lower.endswith(ext):
                return True
        
        for path in skip_paths:
            if path in file_lower:
                return True
        
        return False
    
    def _calculate_confidence(self, cred_type: CredentialType, value: str, content: str) -> float:
        """Calculate confidence score"""
        base_score = 70.0
        
        # Type-specific scoring
        if cred_type == CredentialType.AWS_ACCESS_KEY and value.startswith('AKIA') and len(value) == 20:
            base_score = 95.0
        elif cred_type == CredentialType.SENDGRID_KEY and value.startswith('SG.') and len(value) >= 69:
            base_score = 90.0
        elif cred_type == CredentialType.JWT_TOKEN and value.count('.') == 2:
            base_score = 85.0
        elif cred_type == CredentialType.AWS_SECRET_KEY and len(value) == 40:
            base_score = 80.0
        
        # Context boost
        sensitive_contexts = ['production', 'prod', 'live', 'api', 'secret', 'key']
        for context in sensitive_contexts:
            if context.lower() in content.lower():
                base_score += 5.0
        
        # Proximity boost for AWS pairs
        if cred_type == CredentialType.AWS_ACCESS_KEY and 'aws_secret' in content.lower():
            base_score += 10.0
        elif cred_type == CredentialType.AWS_SECRET_KEY and 'akia' in content.lower():
            base_score += 10.0
        
        return min(base_score, 99.0)
    
    def _determine_severity(self, cred_type: CredentialType, confidence: float, content: str) -> SeverityLevel:
        """Determine severity level with more nuanced logic"""
        content_lower = content.lower()
        
        # Check for production indicators
        production_indicators = ['production', 'prod', 'live']
        is_production = any(indicator in content_lower for indicator in production_indicators)
        
        # Check for main/master indicators (but not as critical as production)
        main_indicators = ['main', 'master']
        is_main = any(indicator in content_lower for indicator in main_indicators)
        
        # High-risk types
        high_risk_types = {CredentialType.AWS_ACCESS_KEY, CredentialType.AWS_SECRET_KEY}
        
        # Critical: High confidence + high risk + production context
        if confidence >= 95.0 and cred_type in high_risk_types and is_production:
            return SeverityLevel.CRITICAL
        
        # High: High confidence + high risk + main context, OR very high confidence + high risk
        elif confidence >= 90.0 and cred_type in high_risk_types and (is_main or confidence >= 95.0):
            return SeverityLevel.HIGH
        
        # High: High confidence + high risk (even without production context)
        elif confidence >= 85.0 and cred_type in high_risk_types:
            return SeverityLevel.HIGH
        
        # Medium: Good confidence OR high-risk type with lower confidence
        elif confidence >= 75.0 or cred_type in high_risk_types:
            return SeverityLevel.MEDIUM
        
        # Low: Everything else
        else:
            return SeverityLevel.LOW
    
    def _apply_filter(self, value: str, content: str, source_file: str) -> tuple:
        """Apply false positive filtering"""
        
        # Known test patterns
        if value in self.test_patterns:
            return True, "Known test pattern"
        
        # Test keywords in value
        value_lower = value.lower()
        for keyword in self.test_keywords:
            if keyword in value_lower:
                return True, f"Test keyword in value: {keyword}"
        
        # Test context
        content_lower = content.lower()
        test_indicators = ['example', 'test', 'demo', 'sample', 'placeholder']
        for indicator in test_indicators:
            if indicator in content_lower:
                return True, f"Test context: {indicator}"
        
        # File-based filtering
        if 'readme' in source_file.lower() or 'example' in source_file.lower():
            return True, "Documentation/example file"
        
        return False, None

def test_false_positive_filtering():
    """Test false positive filtering"""
    print("🧪 Testing False Positive Filtering...")
    
    detector = SimplifiedEnhancedDetector()
    
    test_cases = [
        # Should be filtered (false positives)
        ("AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE", "example.md", True),
        ("test_key = 'SG.SENDGRID_API_KEY'", "test_config.py", True),
        ("# Demo: AKIA1234567890123456", "README.md", True),
        ("example_secret = 'abcdefghijklmnopqrstuvwxyz1234567890ABCD'", "samples/demo.py", True),
        
        # Should NOT be filtered (real credentials)
        ("AWS_ACCESS_KEY=AKIA1234567890ABCDEF", "production.env", False),
        ("SENDGRID_KEY=SG.1234567890abcdefghij.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd", "config.json", False),
        ("production_secret=abcdefghijklmnopqrstuvwxyz1234567890ABCD", "prod_config.py", False),
    ]
    
    results = {"total": 0, "correct": 0, "false_positives": 0, "false_negatives": 0}
    
    for content, filename, should_be_filtered in test_cases:
        results["total"] += 1
        detections = detector.detect_credentials(content, filename)
        
        if should_be_filtered and len(detections) == 0:
            results["correct"] += 1
            print(f"✅ Correctly filtered: {filename}")
        elif not should_be_filtered and len(detections) > 0:
            results["correct"] += 1
            print(f"✅ Correctly detected: {filename} - {len(detections)} credentials")
        elif should_be_filtered and len(detections) > 0:
            results["false_positives"] += 1
            print(f"❌ False positive: {filename} - should have been filtered")
        else:
            results["false_negatives"] += 1
            print(f"❌ False negative: {filename} - should have been detected")
    
    accuracy = (results["correct"] / results["total"]) * 100
    print(f"\n📊 Filtering Results: {accuracy:.1f}% accuracy")
    
    return results

def test_proximity_matching():
    """Test proximity matching for credential pairs"""
    print("\n🧪 Testing Proximity Matching...")
    
    detector = SimplifiedEnhancedDetector()
    
    # Test AWS credential pair
    test_content = """
# Production AWS Configuration
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=abcdefghijklmnopqrstuvwxyz1234567890ABCD
AWS_REGION=us-east-1
"""
    
    detections = detector.detect_credentials(test_content, "prod_config.env")
    
    aws_access_found = False
    aws_secret_found = False
    high_confidence_found = False
    
    print(f"📋 Detections found: {len(detections)}")
    
    for detection in detections:
        print(f"  - {detection.credential_type.value}: {detection.confidence_score:.1f}% confidence, {detection.severity.value} severity")
        
        if detection.credential_type == CredentialType.AWS_ACCESS_KEY:
            aws_access_found = True
            if detection.confidence_score >= 95.0:
                high_confidence_found = True
        
        elif detection.credential_type == CredentialType.AWS_SECRET_KEY:
            aws_secret_found = True
            if detection.confidence_score >= 90.0:  # Should get proximity boost
                high_confidence_found = True
    
    success = aws_access_found and aws_secret_found and high_confidence_found
    print(f"  AWS pair detection: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"  High confidence scores: {'✅ YES' if high_confidence_found else '❌ NO'}")
    
    return success

def test_severity_assignment():
    """Test severity level assignment"""
    print("\n🧪 Testing Severity Assignment...")
    
    detector = SimplifiedEnhancedDetector()
    
    test_cases = [
        ("production_aws_key=AKIA1234567890ABCDEF", "production.env", SeverityLevel.CRITICAL),
        ("aws_access_key=AKIA1234567890ABCDEF", "main_config.json", SeverityLevel.HIGH),
        ("SENDGRID_KEY=SG.1234567890abcdefghij.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd", "email.py", SeverityLevel.HIGH),
    ]
    
    results = {"total": 0, "correct": 0}
    
    for content, filename, expected_severity in test_cases:
        results["total"] += 1
        detections = detector.detect_credentials(content, filename)
        
        if detections:
            actual_severity = detections[0].severity
            if actual_severity == expected_severity:
                results["correct"] += 1
                print(f"✅ Correct severity for {filename}: {actual_severity.value}")
            else:
                print(f"❌ Wrong severity for {filename}: expected {expected_severity.value}, got {actual_severity.value}")
        else:
            print(f"❌ No detection for {filename}")
    
    accuracy = (results["correct"] / results["total"]) * 100 if results["total"] > 0 else 0
    print(f"\n📊 Severity accuracy: {accuracy:.1f}%")
    
    return accuracy >= 75.0

def test_file_filtering():
    """Test file-based filtering"""
    print("\n🧪 Testing File Filtering...")
    
    detector = SimplifiedEnhancedDetector()
    
    # Test files that should be skipped
    skip_files = [
        "README.md",
        "docs/example.txt",
        "samples/demo.py",
        "test/credentials.py"
    ]
    
    # Test files that should be scanned
    scan_files = [
        "config.json",
        "production.env",
        "app/settings.py"
    ]
    
    test_content = "AWS_ACCESS_KEY=AKIA1234567890ABCDEF"
    
    skipped_correctly = 0
    scanned_correctly = 0
    
    for filename in skip_files:
        detections = detector.detect_credentials(test_content, filename)
        if len(detections) == 0:
            skipped_correctly += 1
            print(f"✅ Correctly skipped: {filename}")
        else:
            print(f"❌ Should have skipped: {filename}")
    
    for filename in scan_files:
        detections = detector.detect_credentials(test_content, filename)
        if len(detections) > 0:
            scanned_correctly += 1
            print(f"✅ Correctly scanned: {filename}")
        else:
            print(f"❌ Should have detected in: {filename}")
    
    total_correct = skipped_correctly + scanned_correctly
    total_tests = len(skip_files) + len(scan_files)
    accuracy = (total_correct / total_tests) * 100
    
    print(f"\n📊 File filtering accuracy: {accuracy:.1f}%")
    
    return accuracy >= 80.0

def test_performance():
    """Test detection performance"""
    print("\n🧪 Testing Performance...")
    
    detector = SimplifiedEnhancedDetector()
    
    # More realistic test content with actual credentials to detect
    test_content = """
# Configuration file with multiple credentials
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=abcdefghijklmnopqrstuvwxyz1234567890ABCD
SENDGRID_API_KEY=SG.1234567890abcdefghij.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd

# Some other config
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# JWT tokens
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
"""
    
    # Test with smaller content first to ensure detections work
    import time
    start_time = time.time()
    
    detections = detector.detect_credentials(test_content, "performance_test.env")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"📊 Performance Results:")
    print(f"  Content size: {len(test_content):,} characters")
    print(f"  Processing time: {processing_time:.3f} seconds")
    print(f"  Detections found: {len(detections)}")
    print(f"  Total processed: {detector.stats['total_detections']}")
    print(f"  Filtered out: {detector.stats['filtered_out']}")
    print(f"  Confirmed: {detector.stats['confirmed_credentials']}")
    
    # Performance should find credentials and be reasonably fast
    performance_ok = processing_time < 0.1 and len(detections) >= 3  # Should find AWS keys + SendGrid + JWT
    
    print(f"  Performance: {'✅ GOOD' if performance_ok else '❌ NEEDS IMPROVEMENT'}")
    
    return performance_ok

def main():
    """Run all simplified tests"""
    print("🚀 Enhanced Security Monitoring - Simplified Test Suite")
    print("=" * 70)
    
    test_results = []
    
    # Run tests
    test_results.append(("False Positive Filtering", test_false_positive_filtering()["correct"] >= 5))
    test_results.append(("Proximity Matching", test_proximity_matching()))
    test_results.append(("Severity Assignment", test_severity_assignment()))
    test_results.append(("File Filtering", test_file_filtering()))
    test_results.append(("Performance", test_performance()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 70)
    print(f"  Total Tests: {len(test_results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {len(test_results) - passed}")
    print(f"  Success Rate: {(passed / len(test_results)) * 100:.1f}%")
    
    if passed == len(test_results):
        print("\n🎉 ALL TESTS PASSED - Core functionality working correctly!")
        print("✅ False positive reduction: IMPLEMENTED")
        print("✅ Context-aware detection: IMPLEMENTED") 
        print("✅ Proximity matching: IMPLEMENTED")
        print("✅ Severity levels: IMPLEMENTED")
        print("✅ File filtering: IMPLEMENTED")
        return 0
    else:
        print("\n⚠️  Some tests failed - Review implementation")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)