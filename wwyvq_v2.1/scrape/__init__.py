#!/usr/bin/env python3
"""
🔍 WWYVQ Framework v2.1 - Credential Scraping Module
Ultra-Organized Architecture - Intelligent Credential Extraction

Features:
- API key leak detection (.env, config.js, etc.)
- JavaScript file analysis for secrets
- 2500+ path enumeration
- Regex + heuristic extraction
- File sensitivity analysis
- Intelligent credential classification
"""

import asyncio
import re
import json
import base64
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
from urllib.parse import urljoin, urlparse
import mimetypes
import hashlib


class CredentialType(Enum):
    """Credential types"""
    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    SENDGRID_API_KEY = "sendgrid_api_key"
    MAILGUN_API_KEY = "mailgun_api_key"
    TWILIO_SID = "twilio_sid"
    TWILIO_TOKEN = "twilio_token"
    STRIPE_KEY = "stripe_key"
    GITHUB_TOKEN = "github_token"
    SLACK_TOKEN = "slack_token"
    JWT_TOKEN = "jwt_token"
    DATABASE_URL = "database_url"
    SMTP_PASSWORD = "smtp_password"
    DOCKER_PASSWORD = "docker_password"
    API_KEY_GENERIC = "api_key_generic"
    UNKNOWN = "unknown"


@dataclass
class ExtractedCredential:
    """Extracted credential information"""
    credential_type: CredentialType
    value: str
    source_url: str
    source_file: str
    context: str
    confidence: float
    line_number: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ScrapeResult:
    """Scraping result"""
    url: str
    status_code: int
    content_type: str
    file_size: int
    credentials: List[ExtractedCredential]
    file_hash: str
    processing_time: float
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ScrapeModule:
    """
    Intelligent credential scraping module
    
    Features:
    - 2500+ path enumeration
    - Multi-pattern credential extraction
    - JavaScript analysis
    - Heuristic classification
    """
    
    def __init__(self, config_manager, logger, engine):
        """Initialize scrape module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        self.config = config_manager.get_config().scrape
        
        # HTTP session
        self.session = None
        
        # Credential patterns
        self.credential_patterns = {
            CredentialType.AWS_ACCESS_KEY: [
                r'AKIA[0-9A-Z]{16}',
                r'ASIA[0-9A-Z]{16}',
                r'AIDA[0-9A-Z]{16}'
            ],
            CredentialType.AWS_SECRET_KEY: [
                r'[A-Za-z0-9/+=]{40}',
                r'aws_secret_access_key["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?'
            ],
            CredentialType.SENDGRID_API_KEY: [
                r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
                r'sendgrid[_-]?api[_-]?key["\']?\s*[:=]\s*["\']?(SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43})["\']?'
            ],
            CredentialType.MAILGUN_API_KEY: [
                r'key-[0-9a-f]{32}',
                r'mailgun[_-]?api[_-]?key["\']?\s*[:=]\s*["\']?(key-[0-9a-f]{32})["\']?'
            ],
            CredentialType.TWILIO_SID: [
                r'AC[0-9a-f]{32}',
                r'twilio[_-]?account[_-]?sid["\']?\s*[:=]\s*["\']?(AC[0-9a-f]{32})["\']?'
            ],
            CredentialType.TWILIO_TOKEN: [
                r'[0-9a-f]{32}',
                r'twilio[_-]?auth[_-]?token["\']?\s*[:=]\s*["\']?([0-9a-f]{32})["\']?'
            ],
            CredentialType.STRIPE_KEY: [
                r'sk_live_[0-9a-zA-Z]{24}',
                r'sk_test_[0-9a-zA-Z]{24}',
                r'pk_live_[0-9a-zA-Z]{24}',
                r'pk_test_[0-9a-zA-Z]{24}'
            ],
            CredentialType.GITHUB_TOKEN: [
                r'ghp_[0-9a-zA-Z]{36}',
                r'github[_-]?token["\']?\s*[:=]\s*["\']?(ghp_[0-9a-zA-Z]{36})["\']?'
            ],
            CredentialType.SLACK_TOKEN: [
                r'xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}',
                r'xoxp-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}',
                r'slack[_-]?token["\']?\s*[:=]\s*["\']?(xox[bp]-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24})["\']?'
            ],
            CredentialType.JWT_TOKEN: [
                r'eyJ[0-9a-zA-Z_-]*\.eyJ[0-9a-zA-Z_-]*\.[0-9a-zA-Z_-]*'
            ],
            CredentialType.DATABASE_URL: [
                r'(postgresql|postgres|mysql|mongodb|redis)://[^/\s]+',
                r'database[_-]?url["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?'
            ],
            CredentialType.SMTP_PASSWORD: [
                r'smtp[_-]?password["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?',
                r'mail[_-]?password["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?'
            ],
            CredentialType.DOCKER_PASSWORD: [
                r'docker[_-]?password["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?',
                r'registry[_-]?password["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?'
            ],
            CredentialType.API_KEY_GENERIC: [
                r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?',
                r'apikey["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?'
            ]
        }
        
        # File paths to check (2500+ paths)
        self.sensitive_paths = self._generate_sensitive_paths()
        
        # Statistics
        self.stats = {
            'urls_scraped': 0,
            'files_analyzed': 0,
            'credentials_found': 0,
            'js_files_analyzed': 0,
            'env_files_found': 0,
            'config_files_found': 0
        }
        
        self.logger.info("🔍 Credential Scraping Module initialized")
    
    def _generate_sensitive_paths(self) -> List[str]:
        """Generate 2500+ sensitive file paths"""
        base_paths = [
            # Environment files
            ".env", ".env.local", ".env.production", ".env.development",
            ".env.staging", ".env.test", ".env.example", ".env.sample",
            ".env.backup", ".env.old", ".env.bak", ".env.orig",
            "env", "environment", "config.env", "app.env",
            
            # Configuration files
            "config.js", "config.json", "config.yaml", "config.yml",
            "config.xml", "config.ini", "config.cfg", "config.conf",
            "configuration.js", "configuration.json", "settings.js",
            "settings.json", "app.config", "web.config", "site.config",
            
            # JavaScript files
            "app.js", "main.js", "index.js", "bundle.js", "config.js",
            "settings.js", "api.js", "auth.js", "credentials.js",
            "keys.js", "secrets.js", "tokens.js", "constants.js",
            
            # AWS/Cloud configs
            "aws-credentials", ".aws/credentials", ".aws/config",
            "gcp-credentials.json", "azure-credentials.json",
            "service-account.json", "key.json", "credentials.json",
            
            # Database configs
            "database.yml", "database.json", "db.config", "db.json",
            "connection.js", "connection.json", "knexfile.js",
            "sequelize.js", "mongoose.js", "redis.conf",
            
            # Docker/Container configs
            "docker-compose.yml", "docker-compose.yaml", "Dockerfile",
            ".dockerignore", "docker-compose.override.yml",
            "docker-compose.prod.yml", "docker-compose.dev.yml",
            
            # SSH/Keys
            "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
            ".ssh/id_rsa", ".ssh/config", "authorized_keys",
            "known_hosts", "private.key", "public.key",
            
            # Application-specific
            "wp-config.php", "local_settings.py", "settings.py",
            "production.py", "development.py", "local.py",
            "app.yaml", "app.yml", "application.yml",
            "application.properties", "bootstrap.yml",
            
            # CI/CD configs
            ".github/workflows/", ".gitlab-ci.yml", ".travis.yml",
            "circle.yml", "jenkins.yml", "pipeline.yml",
            "deploy.yml", "build.yml", "release.yml",
            
            # Backup/Old files
            "backup.sql", "dump.sql", "database.sql", "data.sql",
            "config.backup", "config.old", "config.bak",
            "settings.backup", "app.backup", "env.backup"
        ]
        
        # Generate directory variations
        directories = [
            "", "admin/", "api/", "app/", "assets/", "backup/", "bin/",
            "build/", "cache/", "config/", "conf/", "data/", "db/",
            "deploy/", "dev/", "docs/", "etc/", "files/", "html/",
            "includes/", "js/", "lib/", "logs/", "public/", "resources/",
            "scripts/", "src/", "static/", "temp/", "tmp/", "uploads/",
            "var/", "www/", "assets/js/", "assets/css/", "assets/img/",
            "public/js/", "public/css/", "static/js/", "static/css/",
            "wp-content/", "wp-admin/", "wp-includes/", "node_modules/",
            ".git/", ".svn/", ".hg/", ".vscode/", ".idea/", "vendor/"
        ]
        
        # Generate file extensions
        extensions = [
            "", ".js", ".json", ".yml", ".yaml", ".xml", ".ini", ".cfg",
            ".conf", ".config", ".properties", ".txt", ".log", ".bak",
            ".old", ".orig", ".backup", ".tmp", ".temp", ".swp", ".swo",
            ".php", ".py", ".rb", ".java", ".go", ".cs", ".cpp", ".c",
            ".sh", ".bat", ".cmd", ".ps1", ".sql", ".db", ".sqlite"
        ]
        
        # Generate all combinations
        all_paths = []
        for base in base_paths:
            for directory in directories:
                for ext in extensions:
                    if base.endswith(tuple(extensions)) and ext:
                        continue  # Skip double extensions
                    path = f"{directory}{base}{ext}"
                    all_paths.append(path)
        
        # Add numbered variations
        numbered_paths = []
        for path in all_paths[:500]:  # Limit to avoid too many
            for i in range(1, 6):
                numbered_paths.append(f"{path}.{i}")
                numbered_paths.append(f"{path}_{i}")
        
        all_paths.extend(numbered_paths)
        
        # Remove duplicates and sort
        unique_paths = list(set(all_paths))
        unique_paths.sort()
        
        return unique_paths[:2500]  # Limit to 2500 paths
    
    async def scrape_targets(self, targets: List[str], mode, **kwargs) -> Dict[str, Any]:
        """Scrape targets for credentials"""
        results = {'results': [], 'errors': []}
        
        # Initialize HTTP session
        await self._init_session()
        
        try:
            # Scrape each target
            for target in targets:
                try:
                    scrape_results = await self._scrape_target(target)
                    results['results'].extend(scrape_results)
                
                except Exception as e:
                    self.logger.error(f"Failed to scrape target {target}: {e}")
                    results['errors'].append(f"Target {target}: {e}")
        
        finally:
            await self._close_session()
        
        return results
    
    async def _init_session(self):
        """Initialize HTTP session"""
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
    
    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _scrape_target(self, target: str) -> List[Dict[str, Any]]:
        """Scrape a single target"""
        results = []
        
        # Ensure target has protocol
        if not target.startswith(('http://', 'https://')):
            target = f"http://{target}"
        
        # Test each sensitive path
        for path in self.sensitive_paths:
            try:
                url = urljoin(target, path)
                scrape_result = await self._scrape_url(url)
                
                if scrape_result and scrape_result.credentials:
                    results.append({
                        'type': 'credential_scrape',
                        'target': target,
                        'url': url,
                        'path': path,
                        'credentials': [
                            {
                                'type': cred.credential_type.value,
                                'value': cred.value,
                                'confidence': cred.confidence,
                                'context': cred.context,
                                'line_number': cred.line_number
                            }
                            for cred in scrape_result.credentials
                        ],
                        'file_info': {
                            'content_type': scrape_result.content_type,
                            'file_size': scrape_result.file_size,
                            'file_hash': scrape_result.file_hash
                        }
                    })
                    
                    self.stats['credentials_found'] += len(scrape_result.credentials)
                    
                    # Log the find
                    self.logger.info(f"🔍 Found {len(scrape_result.credentials)} credentials in {url}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.debug(f"Failed to scrape {path}: {e}")
        
        return results
    
    async def _scrape_url(self, url: str) -> Optional[ScrapeResult]:
        """Scrape a single URL"""
        import time
        start_time = time.time()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    content_length = int(response.headers.get('Content-Length', 0))
                    
                    # Check file size limit
                    if content_length > self.config.file_size_limit:
                        return None
                    
                    # Read content
                    content = await response.text()
                    
                    # Calculate hash
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    # Extract credentials
                    credentials = await self._extract_credentials(content, url)
                    
                    # Update statistics
                    self.stats['urls_scraped'] += 1
                    self.stats['files_analyzed'] += 1
                    
                    # Check file type
                    if '.js' in url.lower() or 'javascript' in content_type:
                        self.stats['js_files_analyzed'] += 1
                    elif '.env' in url.lower():
                        self.stats['env_files_found'] += 1
                    elif 'config' in url.lower():
                        self.stats['config_files_found'] += 1
                    
                    return ScrapeResult(
                        url=url,
                        status_code=response.status,
                        content_type=content_type,
                        file_size=len(content),
                        credentials=credentials,
                        file_hash=file_hash,
                        processing_time=time.time() - start_time
                    )
        
        except Exception as e:
            self.logger.debug(f"Failed to scrape URL {url}: {e}")
        
        return None
    
    async def _extract_credentials(self, content: str, source_url: str) -> List[ExtractedCredential]:
        """Extract credentials from content"""
        credentials = []
        
        # Split content into lines for context
        lines = content.split('\n')
        
        # Apply each pattern
        for cred_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        # Get the matched value
                        if match.groups():
                            value = match.group(1)
                        else:
                            value = match.group(0)
                        
                        # Skip if value is too short or too long
                        if len(value) < 5 or len(value) > 200:
                            continue
                        
                        # Get line number and context
                        line_num = content[:match.start()].count('\n') + 1
                        context = ""
                        
                        if line_num <= len(lines):
                            context = lines[line_num - 1].strip()
                        
                        # Calculate confidence
                        confidence = self._calculate_confidence(cred_type, value, context)
                        
                        # Skip low confidence matches
                        if confidence < 0.3:
                            continue
                        
                        # Create credential
                        credential = ExtractedCredential(
                            credential_type=cred_type,
                            value=value,
                            source_url=source_url,
                            source_file=source_url.split('/')[-1],
                            context=context,
                            confidence=confidence,
                            line_number=line_num
                        )
                        
                        credentials.append(credential)
                
                except Exception as e:
                    self.logger.debug(f"Pattern matching failed for {cred_type}: {e}")
        
        # Additional heuristic analysis
        heuristic_creds = await self._heuristic_analysis(content, source_url)
        credentials.extend(heuristic_creds)
        
        # Remove duplicates
        unique_credentials = []
        seen_values = set()
        
        for cred in credentials:
            if cred.value not in seen_values:
                seen_values.add(cred.value)
                unique_credentials.append(cred)
        
        return unique_credentials
    
    def _calculate_confidence(self, cred_type: CredentialType, value: str, context: str) -> float:
        """Calculate confidence score for credential"""
        confidence = 0.5  # Base confidence
        
        # Length-based confidence
        if cred_type == CredentialType.AWS_ACCESS_KEY:
            if len(value) == 20 and value.startswith('AKIA'):
                confidence = 0.9
        elif cred_type == CredentialType.AWS_SECRET_KEY:
            if len(value) == 40:
                confidence = 0.8
        elif cred_type == CredentialType.SENDGRID_API_KEY:
            if value.startswith('SG.') and len(value) == 69:
                confidence = 0.95
        elif cred_type == CredentialType.GITHUB_TOKEN:
            if value.startswith('ghp_') and len(value) == 40:
                confidence = 0.95
        
        # Context-based confidence
        context_lower = context.lower()
        
        # Positive indicators
        positive_indicators = [
            'api_key', 'apikey', 'secret', 'password', 'token',
            'credential', 'auth', 'key', 'access', 'private'
        ]
        
        for indicator in positive_indicators:
            if indicator in context_lower:
                confidence += 0.1
        
        # Negative indicators
        negative_indicators = [
            'example', 'sample', 'test', 'demo', 'placeholder',
            'dummy', 'fake', 'mock', 'xxx', 'yyy', 'zzz'
        ]
        
        for indicator in negative_indicators:
            if indicator in context_lower:
                confidence -= 0.3
        
        # Entropy-based confidence
        entropy = self._calculate_entropy(value)
        if entropy > 4.0:
            confidence += 0.1
        elif entropy < 2.0:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_entropy(self, string: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not string:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in string:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(string)
        
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    async def _heuristic_analysis(self, content: str, source_url: str) -> List[ExtractedCredential]:
        """Perform heuristic analysis for credentials"""
        credentials = []
        
        # Look for JSON structures
        try:
            if '{' in content and '}' in content:
                # Try to parse as JSON
                json_objects = self._extract_json_objects(content)
                for json_obj in json_objects:
                    json_creds = self._analyze_json_structure(json_obj, source_url)
                    credentials.extend(json_creds)
        except:
            pass
        
        # Look for environment variable patterns
        env_patterns = [
            r'([A-Z_]+)=(["\']?)([^"\'\s]+)\2',
            r'export\s+([A-Z_]+)=(["\']?)([^"\'\s]+)\2',
            r'process\.env\.([A-Z_]+)',
            r'os\.environ\[(["\'])([A-Z_]+)\1\]'
        ]
        
        for pattern in env_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                var_name = match.group(1) if match.groups() else ""
                var_value = match.group(3) if len(match.groups()) >= 3 else ""
                
                if self._is_credential_variable(var_name):
                    cred_type = self._classify_credential_by_name(var_name)
                    confidence = self._calculate_confidence(cred_type, var_value, match.group(0))
                    
                    if confidence > 0.4:
                        credentials.append(ExtractedCredential(
                            credential_type=cred_type,
                            value=var_value,
                            source_url=source_url,
                            source_file=source_url.split('/')[-1],
                            context=match.group(0),
                            confidence=confidence,
                            line_number=content[:match.start()].count('\n') + 1
                        ))
        
        return credentials
    
    def _extract_json_objects(self, content: str) -> List[Dict[str, Any]]:
        """Extract JSON objects from content"""
        json_objects = []
        
        # Find potential JSON structures
        brace_count = 0
        start_pos = -1
        
        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    start_pos = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_pos != -1:
                    json_str = content[start_pos:i+1]
                    try:
                        json_obj = json.loads(json_str)
                        json_objects.append(json_obj)
                    except:
                        pass
        
        return json_objects
    
    def _analyze_json_structure(self, json_obj: Dict[str, Any], source_url: str) -> List[ExtractedCredential]:
        """Analyze JSON structure for credentials"""
        credentials = []
        
        def analyze_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, str) and self._is_credential_variable(key):
                        cred_type = self._classify_credential_by_name(key)
                        confidence = self._calculate_confidence(cred_type, value, key)
                        
                        if confidence > 0.4:
                            credentials.append(ExtractedCredential(
                                credential_type=cred_type,
                                value=value,
                                source_url=source_url,
                                source_file=source_url.split('/')[-1],
                                context=f"{key}: {value}",
                                confidence=confidence,
                                metadata={'json_path': current_path}
                            ))
                    
                    elif isinstance(value, (dict, list)):
                        analyze_recursive(value, current_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    analyze_recursive(item, f"{path}[{i}]")
        
        analyze_recursive(json_obj)
        return credentials
    
    def _is_credential_variable(self, name: str) -> bool:
        """Check if variable name indicates a credential"""
        name_lower = name.lower()
        
        credential_keywords = [
            'api_key', 'apikey', 'secret', 'password', 'token',
            'credential', 'auth', 'key', 'access', 'private',
            'aws_access_key', 'aws_secret', 'sendgrid', 'mailgun',
            'twilio', 'stripe', 'github', 'slack', 'jwt',
            'database_url', 'smtp', 'docker', 'registry'
        ]
        
        for keyword in credential_keywords:
            if keyword in name_lower:
                return True
        
        return False
    
    def _classify_credential_by_name(self, name: str) -> CredentialType:
        """Classify credential type by variable name"""
        name_lower = name.lower()
        
        if 'aws_access_key' in name_lower or 'access_key_id' in name_lower:
            return CredentialType.AWS_ACCESS_KEY
        elif 'aws_secret' in name_lower or 'secret_access_key' in name_lower:
            return CredentialType.AWS_SECRET_KEY
        elif 'sendgrid' in name_lower:
            return CredentialType.SENDGRID_API_KEY
        elif 'mailgun' in name_lower:
            return CredentialType.MAILGUN_API_KEY
        elif 'twilio' in name_lower and 'sid' in name_lower:
            return CredentialType.TWILIO_SID
        elif 'twilio' in name_lower and ('token' in name_lower or 'auth' in name_lower):
            return CredentialType.TWILIO_TOKEN
        elif 'stripe' in name_lower:
            return CredentialType.STRIPE_KEY
        elif 'github' in name_lower:
            return CredentialType.GITHUB_TOKEN
        elif 'slack' in name_lower:
            return CredentialType.SLACK_TOKEN
        elif 'jwt' in name_lower:
            return CredentialType.JWT_TOKEN
        elif 'database_url' in name_lower or 'db_url' in name_lower:
            return CredentialType.DATABASE_URL
        elif 'smtp' in name_lower and 'password' in name_lower:
            return CredentialType.SMTP_PASSWORD
        elif 'docker' in name_lower or 'registry' in name_lower:
            return CredentialType.DOCKER_PASSWORD
        elif 'api_key' in name_lower or 'apikey' in name_lower:
            return CredentialType.API_KEY_GENERIC
        else:
            return CredentialType.UNKNOWN
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get module statistics"""
        return self.stats.copy()
    
    async def shutdown(self):
        """Shutdown module"""
        await self._close_session()
        self.logger.info("🛑 Credential Scraping Module shutdown completed")