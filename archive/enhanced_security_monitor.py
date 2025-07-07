#!/usr/bin/env python3
"""
Enhanced Security Monitoring System
Comprehensive false positive reduction, advanced alerting, and monitoring capabilities
Author: wKayaa | Enhanced Version | 2025-01-28
"""

import asyncio
import aiohttp
import json
import re
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeverityLevel(Enum):
    """Alert severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CredentialType(Enum):
    """Supported credential types"""
    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    SENDGRID_KEY = "sendgrid_key"
    JWT_TOKEN = "jwt_token"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"
    PASSWORD = "password"
    SECRET = "secret"

@dataclass
class DetectionResult:
    """Enhanced detection result structure"""
    credential_type: CredentialType
    value: str
    redacted_value: str
    confidence_score: float
    severity: SeverityLevel
    source_file: str
    line_number: int
    context: str
    proximity_matches: List[str] = field(default_factory=list)
    filter_reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    suggestions: List[str] = field(default_factory=list)

@dataclass
class FilterConfig:
    """Configuration for filtering and detection"""
    excluded_extensions: Set[str] = field(default_factory=lambda: {
        '.md', '.txt', '.rst', '.pdf', '.doc', '.docx', '.png', '.jpg', '.gif'
    })
    excluded_paths: Set[str] = field(default_factory=lambda: {
        'docs/', 'samples/', 'examples/', 'test/', 'tests/', '__pycache__/',
        'node_modules/', '.git/', 'README', 'LICENSE'
    })
    test_keywords: Set[str] = field(default_factory=lambda: {
        'example', 'test', 'demo', 'sample', 'fake', 'dummy', 'placeholder'
    })
    proximity_distance: int = 200  # Characters distance for proximity matching
    min_confidence_threshold: float = 75.0
    enable_proximity_matching: bool = True
    enable_context_analysis: bool = True

class FalsePositiveFilter:
    """Advanced false positive reduction system"""
    
    def __init__(self, config: FilterConfig):
        self.config = config
        self.known_test_patterns = {
            'AKIAIOSFODNN7EXAMPLE',  # AWS documentation example
            'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',  # AWS documentation example
            'SG.SENDGRID_API_KEY',  # SendGrid placeholder
            'your-api-key-here',
            'INSERT_YOUR_KEY_HERE',
            'REPLACE_WITH_YOUR_KEY'
        }
        self.stats = {
            'total_detections': 0,
            'filtered_out': 0,
            'false_positives': 0,
            'confirmed_credentials': 0
        }
    
    def should_scan_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """Determine if file should be scanned based on path and extension"""
        path_lower = file_path.lower()
        
        # Check excluded extensions
        for ext in self.config.excluded_extensions:
            if path_lower.endswith(ext):
                return False, f"Excluded extension: {ext}"
        
        # Check excluded paths
        for excluded_path in self.config.excluded_paths:
            if excluded_path.lower() in path_lower:
                return False, f"Excluded path: {excluded_path}"
        
        return True, None
    
    def is_test_credential(self, value: str, context: str) -> Tuple[bool, Optional[str]]:
        """Check if credential appears to be a test/example credential"""
        value_lower = value.lower()
        context_lower = context.lower()
        
        # Check against known test patterns
        if value in self.known_test_patterns:
            return True, "Known test pattern"
        
        # Check for test keywords in value
        for keyword in self.config.test_keywords:
            if keyword in value_lower:
                return True, f"Test keyword in value: {keyword}"
        
        # Check for test keywords in context
        test_context_patterns = ['example', 'test', 'demo', 'sample', 'placeholder']
        for pattern in test_context_patterns:
            if pattern in context_lower:
                return True, f"Test context detected: {pattern}"
        
        return False, None
    
    def filter_detection(self, detection: DetectionResult) -> Tuple[bool, Optional[str]]:
        """Apply comprehensive filtering to detection result"""
        self.stats['total_detections'] += 1
        
        # Test credential check
        is_test, test_reason = self.is_test_credential(detection.value, detection.context)
        if is_test:
            self.stats['false_positives'] += 1
            return False, f"Test credential: {test_reason}"
        
        # Confidence threshold check
        if detection.confidence_score < self.config.min_confidence_threshold:
            self.stats['filtered_out'] += 1
            return False, f"Low confidence: {detection.confidence_score:.1f}%"
        
        self.stats['confirmed_credentials'] += 1
        return True, None

class EnhancedCredentialDetector:
    """Enhanced credential detector with proximity matching and context analysis"""
    
    def __init__(self, config: FilterConfig):
        self.config = config
        self.filter = FalsePositiveFilter(config)
        
        # Enhanced regex patterns with context awareness
        self.patterns = {
            CredentialType.AWS_ACCESS_KEY: {
                'pattern': r'\b(AKIA[0-9A-Z]{16})\b',
                'context_patterns': [r'aws[_\-]?access[_\-]?key', r'access[_\-]?key[_\-]?id'],
                'proximity_patterns': [r'aws[_\-]?secret', r'secret[_\-]?access[_\-]?key']
            },
            CredentialType.AWS_SECRET_KEY: {
                'pattern': r'\b([A-Za-z0-9/+=]{40})\b',
                'context_patterns': [r'aws[_\-]?secret', r'secret[_\-]?access[_\-]?key'],
                'proximity_patterns': [r'AKIA[0-9A-Z]{16}', r'access[_\-]?key']
            },
            CredentialType.SENDGRID_KEY: {
                'pattern': r'\b(SG\.[a-zA-Z0-9_-]{22,}\.[a-zA-Z0-9_-]{43,})\b',
                'context_patterns': [r'sendgrid', r'sg[_\-]?api', r'email[_\-]?api'],
                'proximity_patterns': []
            },
            CredentialType.JWT_TOKEN: {
                'pattern': r'\b(eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*)\b',
                'context_patterns': [r'jwt', r'token', r'bearer'],
                'proximity_patterns': []
            },
            CredentialType.BEARER_TOKEN: {
                'pattern': r'Bearer\s+([A-Za-z0-9_-]{20,})',
                'context_patterns': [r'bearer', r'authorization', r'auth'],
                'proximity_patterns': []
            },
            CredentialType.API_KEY: {
                'pattern': r'(?i)api[_\-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{20,})["\']',
                'context_patterns': [r'api[_\-]?key', r'key'],
                'proximity_patterns': []
            }
        }
    
    def detect_credentials(self, content: str, source_file: str) -> List[DetectionResult]:
        """Detect credentials with enhanced filtering and context analysis"""
        
        # Check if file should be scanned
        should_scan, skip_reason = self.filter.should_scan_file(source_file)
        if not should_scan:
            logger.debug(f"Skipping file {source_file}: {skip_reason}")
            return []
        
        results = []
        lines = content.split('\n')
        
        for cred_type, pattern_config in self.patterns.items():
            matches = re.finditer(pattern_config['pattern'], content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                context = self._extract_context(content, match.start(), match.end())
                
                # Calculate confidence score
                confidence = self._calculate_confidence(cred_type, match.group(1), context, content)
                
                # Determine severity
                severity = self._determine_severity(cred_type, confidence, context)
                
                # Create detection result
                detection = DetectionResult(
                    credential_type=cred_type,
                    value=match.group(1),
                    redacted_value=self._redact_credential(match.group(1)),
                    confidence_score=confidence,
                    severity=severity,
                    source_file=source_file,
                    line_number=line_num,
                    context=context,
                    proximity_matches=self._find_proximity_matches(content, match.start(), pattern_config),
                    suggestions=self._generate_suggestions(cred_type, context)
                )
                
                # Apply filtering
                should_alert, filter_reason = self.filter.filter_detection(detection)
                if should_alert:
                    results.append(detection)
                else:
                    detection.filter_reason = filter_reason
                    logger.debug(f"Filtered detection: {filter_reason}")
        
        return results
    
    def _extract_context(self, content: str, start: int, end: int, context_size: int = 100) -> str:
        """Extract context around the detected credential"""
        context_start = max(0, start - context_size)
        context_end = min(len(content), end + context_size)
        return content[context_start:context_end].replace('\n', ' ').strip()
    
    def _calculate_confidence(self, cred_type: CredentialType, value: str, context: str, full_content: str) -> float:
        """Calculate confidence score for detected credential"""
        base_score = 70.0
        
        # Type-specific confidence boosts
        if cred_type == CredentialType.AWS_ACCESS_KEY and value.startswith('AKIA'):
            base_score = 95.0
        elif cred_type == CredentialType.SENDGRID_KEY and value.startswith('SG.'):
            base_score = 90.0
        elif cred_type == CredentialType.JWT_TOKEN and value.count('.') == 2:
            base_score = 85.0
        
        # Context analysis boost
        pattern_config = self.patterns[cred_type]
        for context_pattern in pattern_config['context_patterns']:
            if re.search(context_pattern, context, re.IGNORECASE):
                base_score += 10.0
        
        # Proximity matching boost
        if self.config.enable_proximity_matching and pattern_config['proximity_patterns']:
            proximity_context = self._get_proximity_context(full_content, value)
            for proximity_pattern in pattern_config['proximity_patterns']:
                if re.search(proximity_pattern, proximity_context, re.IGNORECASE):
                    base_score += 15.0
        
        # Production context boost
        production_indicators = ['production', 'prod', 'live', 'main', 'master']
        for indicator in production_indicators:
            if indicator in context.lower():
                base_score += 5.0
        
        return min(base_score, 99.0)
    
    def _determine_severity(self, cred_type: CredentialType, confidence: float, context: str) -> SeverityLevel:
        """Determine severity level based on credential type and context"""
        
        # Check for production indicators
        production_indicators = ['production', 'prod', 'live', 'main', 'master']
        is_production = any(indicator in context.lower() for indicator in production_indicators)
        
        # High-risk credential types
        high_risk_types = {CredentialType.AWS_ACCESS_KEY, CredentialType.AWS_SECRET_KEY}
        
        if confidence >= 95.0 and (cred_type in high_risk_types or is_production):
            return SeverityLevel.CRITICAL
        elif confidence >= 85.0 and cred_type in high_risk_types:
            return SeverityLevel.HIGH
        elif confidence >= 75.0:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _redact_credential(self, value: str) -> str:
        """Redact credential value for safe display"""
        if len(value) <= 8:
            return '*' * len(value)
        return value[:4] + '*' * (len(value) - 8) + value[-4:]
    
    def _find_proximity_matches(self, content: str, match_pos: int, pattern_config: Dict) -> List[str]:
        """Find proximity matches for enhanced context"""
        if not self.config.enable_proximity_matching:
            return []
        
        proximity_matches = []
        search_start = max(0, match_pos - self.config.proximity_distance)
        search_end = min(len(content), match_pos + self.config.proximity_distance)
        search_context = content[search_start:search_end]
        
        for proximity_pattern in pattern_config['proximity_patterns']:
            matches = re.finditer(proximity_pattern, search_context, re.IGNORECASE)
            for match in matches:
                proximity_matches.append(match.group(0))
        
        return proximity_matches
    
    def _get_proximity_context(self, content: str, value: str) -> str:
        """Get extended context for proximity analysis"""
        value_pos = content.find(value)
        if value_pos == -1:
            return ""
        
        start_pos = max(0, value_pos - self.config.proximity_distance)
        end_pos = min(len(content), value_pos + self.config.proximity_distance)
        
        return content[start_pos:end_pos]
    
    def _generate_suggestions(self, cred_type: CredentialType, context: str) -> List[str]:
        """Generate remediation suggestions"""
        suggestions = []
        
        if cred_type in {CredentialType.AWS_ACCESS_KEY, CredentialType.AWS_SECRET_KEY}:
            suggestions.extend([
                "Rotate AWS credentials immediately",
                "Use AWS IAM roles instead of hardcoded keys",
                "Store credentials in AWS Secrets Manager or environment variables",
                "Review CloudTrail logs for unauthorized access"
            ])
        elif cred_type == CredentialType.SENDGRID_KEY:
            suggestions.extend([
                "Rotate SendGrid API key immediately",
                "Store API key in environment variables",
                "Use SendGrid's API key restrictions"
            ])
        else:
            suggestions.extend([
                "Remove hardcoded credentials from source code",
                "Use environment variables or secure key management",
                "Implement proper secret management practices"
            ])
        
        return suggestions

class ProgressTracker:
    """Real-time progress tracking and reporting"""
    
    def __init__(self):
        self.stats = {
            'scan_start_time': None,
            'files_scanned': 0,
            'files_total': 0,
            'credentials_detected': 0,
            'false_positives_filtered': 0,
            'current_file': '',
            'detection_stages': {
                'file_filtering': 0,
                'pattern_matching': 0,
                'context_analysis': 0,
                'false_positive_filtering': 0,
                'alert_generation': 0
            }
        }
        self.reports = []
    
    def start_scan(self, total_files: int):
        """Start progress tracking"""
        self.stats['scan_start_time'] = datetime.utcnow()
        self.stats['files_total'] = total_files
        logger.info(f"Starting scan of {total_files} files")
    
    def update_progress(self, current_file: str, stage: str):
        """Update progress for current operation"""
        self.stats['current_file'] = current_file
        if stage in self.stats['detection_stages']:
            self.stats['detection_stages'][stage] += 1
    
    def file_completed(self, file_path: str, detections: int, filtered: int):
        """Mark file as completed"""
        self.stats['files_scanned'] += 1
        self.stats['credentials_detected'] += detections
        self.stats['false_positives_filtered'] += filtered
        
        # Log progress every 100 files
        if self.stats['files_scanned'] % 100 == 0:
            self._log_progress()
    
    def _log_progress(self):
        """Log current progress"""
        if self.stats['files_total'] > 0:
            progress_percent = (self.stats['files_scanned'] / self.stats['files_total']) * 100
            elapsed = datetime.utcnow() - self.stats['scan_start_time']
            
            logger.info(f"Progress: {progress_percent:.1f}% ({self.stats['files_scanned']}/{self.stats['files_total']}) "
                       f"- Credentials: {self.stats['credentials_detected']} "
                       f"- Filtered: {self.stats['false_positives_filtered']} "
                       f"- Elapsed: {elapsed}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        elapsed = datetime.utcnow() - self.stats['scan_start_time'] if self.stats['scan_start_time'] else None
        
        return {
            'scan_summary': {
                'start_time': self.stats['scan_start_time'].isoformat() if self.stats['scan_start_time'] else None,
                'elapsed_time': str(elapsed) if elapsed else None,
                'files_scanned': self.stats['files_scanned'],
                'files_total': self.stats['files_total'],
                'completion_percentage': (self.stats['files_scanned'] / self.stats['files_total']) * 100 if self.stats['files_total'] > 0 else 0
            },
            'detection_summary': {
                'total_credentials_detected': self.stats['credentials_detected'],
                'false_positives_filtered': self.stats['false_positives_filtered'],
                'confirmed_credentials': self.stats['credentials_detected'] - self.stats['false_positives_filtered']
            },
            'processing_stages': self.stats['detection_stages'],
            'current_status': {
                'current_file': self.stats['current_file'],
                'scan_active': self.stats['scan_start_time'] is not None
            }
        }

# Export classes for use in other modules
__all__ = [
    'EnhancedCredentialDetector', 'FalsePositiveFilter', 'ProgressTracker',
    'DetectionResult', 'FilterConfig', 'SeverityLevel', 'CredentialType'
]

if __name__ == "__main__":
    print("🚀 Enhanced Security Monitoring System - wKayaa Production")