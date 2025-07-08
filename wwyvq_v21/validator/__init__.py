#!/usr/bin/env python3
"""
✅ WWYVQ Framework v2.1 - Credential Validator Module
Ultra-Organized Architecture - Real-time Credential Validation

Features:
- Real-time credential validation
- Multi-service validation (AWS, SendGrid, SMTP, etc.)
- Classification by confidence level
- Rate limiting and optimization
- Validation result caching
- Professional error handling
"""

import asyncio
import json
import base64
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import smtplib
import ssl
from email.mime.text import MIMEText


class ValidationStatus(Enum):
    """Validation status"""
    VALID = "valid"
    INVALID = "invalid"
    FAILED = "failed"
    UNKNOWN = "unknown"
    RATE_LIMITED = "rate_limited"


class CredentialService(Enum):
    """Supported services for validation"""
    AWS = "aws"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    TWILIO = "twilio"
    STRIPE = "stripe"
    SMTP = "smtp"
    GITHUB = "github"
    SLACK = "slack"
    GENERIC_API = "generic_api"


@dataclass
class ValidationResult:
    """Credential validation result"""
    service: CredentialService
    credential_type: str
    value: str
    status: ValidationStatus
    confidence_score: float
    validation_method: str
    response_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    permissions: List[str] = None
    quota_info: Dict[str, Any] = None
    validated_at: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.permissions is None:
            self.permissions = []
        if self.quota_info is None:
            self.quota_info = {}
        if self.validated_at is None:
            self.validated_at = time.strftime('%Y-%m-%d %H:%M:%S')


class ValidatorModule:
    """
    Real-time credential validation module
    
    Features:
    - Multi-service validation
    - Intelligent rate limiting
    - Result caching
    - Professional classification
    """
    
    def __init__(self, config_manager, logger, engine):
        """Initialize validator module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        self.config = config_manager.get_config().validator
        
        # HTTP session for API calls
        self.session = None
        
        # Validation cache
        self.validation_cache: Dict[str, ValidationResult] = {}
        
        # Rate limiting
        self.rate_limiters: Dict[str, asyncio.Semaphore] = {
            'aws': asyncio.Semaphore(5),
            'sendgrid': asyncio.Semaphore(10),
            'mailgun': asyncio.Semaphore(10),
            'twilio': asyncio.Semaphore(10),
            'stripe': asyncio.Semaphore(5),
            'smtp': asyncio.Semaphore(3),
            'github': asyncio.Semaphore(5),
            'slack': asyncio.Semaphore(5)
        }
        
        # Statistics
        self.stats = {
            'total_validations': 0,
            'valid_credentials': 0,
            'invalid_credentials': 0,
            'failed_validations': 0,
            'cache_hits': 0,
            'by_service': {}
        }
        
        # Service validation methods
        self.validators = {
            CredentialService.AWS: self._validate_aws,
            CredentialService.SENDGRID: self._validate_sendgrid,
            CredentialService.MAILGUN: self._validate_mailgun,
            CredentialService.TWILIO: self._validate_twilio,
            CredentialService.STRIPE: self._validate_stripe,
            CredentialService.SMTP: self._validate_smtp,
            CredentialService.GITHUB: self._validate_github,
            CredentialService.SLACK: self._validate_slack
        }
        
        self.logger.info("✅ Credential Validator Module initialized")
    
    async def validate_targets(self, targets: List[str], mode, **kwargs) -> Dict[str, Any]:
        """Validate credentials found in targets"""
        results = {'results': [], 'errors': []}
        
        # This method is called by the engine for validation operations
        # In practice, credentials would be passed directly
        credentials = kwargs.get('credentials', [])
        
        if not credentials:
            self.logger.warning("No credentials provided for validation")
            return results
        
        # Initialize HTTP session
        await self._init_session()
        
        try:
            # Validate each credential
            for credential in credentials:
                try:
                    validation_result = await self.validate_credential(credential)
                    
                    if validation_result:
                        results['results'].append({
                            'type': 'credential_validation',
                            'service': validation_result.service.value,
                            'credential_type': validation_result.credential_type,
                            'status': validation_result.status.value,
                            'confidence_score': validation_result.confidence_score,
                            'validation_method': validation_result.validation_method,
                            'response_time': validation_result.response_time,
                            'permissions': validation_result.permissions,
                            'quota_info': validation_result.quota_info,
                            'metadata': validation_result.metadata
                        })
                
                except Exception as e:
                    self.logger.error(f"Failed to validate credential: {e}")
                    results['errors'].append(f"Credential validation: {e}")
        
        finally:
            await self._close_session()
        
        return results
    
    async def validate_credential(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate a single credential"""
        try:
            # Extract credential information
            cred_type = credential_data.get('type', 'unknown')
            cred_value = credential_data.get('value', '')
            
            if not cred_value:
                return None
            
            # Check cache first
            cache_key = self._get_cache_key(cred_type, cred_value)
            if cache_key in self.validation_cache:
                self.stats['cache_hits'] += 1
                return self.validation_cache[cache_key]
            
            # Determine service and validate
            service = self._determine_service(cred_type)
            if service and service in self.validators:
                result = await self.validators[service](credential_data)
                
                # Cache result
                if result:
                    self.validation_cache[cache_key] = result
                    
                    # Update statistics
                    self.stats['total_validations'] += 1
                    if result.status == ValidationStatus.VALID:
                        self.stats['valid_credentials'] += 1
                    elif result.status == ValidationStatus.INVALID:
                        self.stats['invalid_credentials'] += 1
                    else:
                        self.stats['failed_validations'] += 1
                    
                    # Update service stats
                    service_name = service.value
                    if service_name not in self.stats['by_service']:
                        self.stats['by_service'][service_name] = {'total': 0, 'valid': 0}
                    
                    self.stats['by_service'][service_name]['total'] += 1
                    if result.status == ValidationStatus.VALID:
                        self.stats['by_service'][service_name]['valid'] += 1
                
                return result
            
            else:
                # Generic validation
                return await self._validate_generic(credential_data)
        
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return None
    
    async def _init_session(self):
        """Initialize HTTP session"""
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=50,
                limit_per_host=10,
                ttl_dns_cache=300
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config.validation_timeout)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
    
    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_cache_key(self, cred_type: str, cred_value: str) -> str:
        """Generate cache key for credential"""
        return hashlib.md5(f"{cred_type}:{cred_value}".encode()).hexdigest()
    
    def _determine_service(self, cred_type: str) -> Optional[CredentialService]:
        """Determine service from credential type"""
        type_mapping = {
            'aws_access_key': CredentialService.AWS,
            'aws_secret_key': CredentialService.AWS,
            'sendgrid_api_key': CredentialService.SENDGRID,
            'mailgun_api_key': CredentialService.MAILGUN,
            'twilio_sid': CredentialService.TWILIO,
            'twilio_token': CredentialService.TWILIO,
            'stripe_key': CredentialService.STRIPE,
            'smtp_password': CredentialService.SMTP,
            'github_token': CredentialService.GITHUB,
            'slack_token': CredentialService.SLACK
        }
        
        return type_mapping.get(cred_type)
    
    async def _validate_aws(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate AWS credentials"""
        start_time = time.time()
        
        async with self.rate_limiters['aws']:
            try:
                cred_type = credential_data.get('type', '')
                cred_value = credential_data.get('value', '')
                
                if cred_type == 'aws_access_key':
                    # For access key, we need the secret key too for full validation
                    # For now, we'll do format validation
                    if cred_value.startswith(('AKIA', 'ASIA', 'AIDA')) and len(cred_value) == 20:
                        return ValidationResult(
                            service=CredentialService.AWS,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.8,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            metadata={'aws_key_type': 'access_key'}
                        )
                    else:
                        return ValidationResult(
                            service=CredentialService.AWS,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.9,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            error_message="Invalid AWS access key format"
                        )
                
                elif cred_type == 'aws_secret_key':
                    # Validate AWS secret key format
                    if len(cred_value) == 40:
                        # Try to use STS GetCallerIdentity for validation
                        # Note: This requires boto3, but we'll do format check for now
                        return ValidationResult(
                            service=CredentialService.AWS,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.7,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            metadata={'aws_key_type': 'secret_key'}
                        )
                    else:
                        return ValidationResult(
                            service=CredentialService.AWS,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.9,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            error_message="Invalid AWS secret key format"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.AWS,
                    credential_type=cred_type,
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="API_TEST",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_sendgrid(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate SendGrid API key"""
        start_time = time.time()
        
        async with self.rate_limiters['sendgrid']:
            try:
                cred_value = credential_data.get('value', '')
                
                # SendGrid API validation
                headers = {
                    'Authorization': f'Bearer {cred_value}',
                    'Content-Type': 'application/json'
                }
                
                url = 'https://api.sendgrid.com/v3/user/account'
                
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return ValidationResult(
                            service=CredentialService.SENDGRID,
                            credential_type='sendgrid_api_key',
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            metadata={
                                'account_type': data.get('type', 'unknown'),
                                'reputation': data.get('reputation', 'unknown')
                            }
                        )
                    
                    elif response.status == 401:
                        return ValidationResult(
                            service=CredentialService.SENDGRID,
                            credential_type='sendgrid_api_key',
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message="Invalid SendGrid API key"
                        )
                    
                    else:
                        return ValidationResult(
                            service=CredentialService.SENDGRID,
                            credential_type='sendgrid_api_key',
                            value=cred_value,
                            status=ValidationStatus.FAILED,
                            confidence_score=0.0,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message=f"HTTP {response.status}"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.SENDGRID,
                    credential_type='sendgrid_api_key',
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="API_TEST",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_mailgun(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate Mailgun API key"""
        start_time = time.time()
        
        async with self.rate_limiters['mailgun']:
            try:
                cred_value = credential_data.get('value', '')
                
                # Mailgun API validation
                auth = aiohttp.BasicAuth('api', cred_value)
                url = 'https://api.mailgun.net/v3/domains'
                
                async with self.session.get(url, auth=auth) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return ValidationResult(
                            service=CredentialService.MAILGUN,
                            credential_type='mailgun_api_key',
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            metadata={
                                'domains_count': len(data.get('items', [])),
                                'total_count': data.get('total_count', 0)
                            }
                        )
                    
                    elif response.status == 401:
                        return ValidationResult(
                            service=CredentialService.MAILGUN,
                            credential_type='mailgun_api_key',
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message="Invalid Mailgun API key"
                        )
                    
                    else:
                        return ValidationResult(
                            service=CredentialService.MAILGUN,
                            credential_type='mailgun_api_key',
                            value=cred_value,
                            status=ValidationStatus.FAILED,
                            confidence_score=0.0,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message=f"HTTP {response.status}"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.MAILGUN,
                    credential_type='mailgun_api_key',
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="API_TEST",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_twilio(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate Twilio credentials"""
        start_time = time.time()
        
        async with self.rate_limiters['twilio']:
            try:
                cred_type = credential_data.get('type', '')
                cred_value = credential_data.get('value', '')
                
                if cred_type == 'twilio_sid':
                    # Validate Twilio Account SID format
                    if cred_value.startswith('AC') and len(cred_value) == 34:
                        return ValidationResult(
                            service=CredentialService.TWILIO,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.9,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            metadata={'twilio_type': 'account_sid'}
                        )
                    else:
                        return ValidationResult(
                            service=CredentialService.TWILIO,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.9,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            error_message="Invalid Twilio Account SID format"
                        )
                
                elif cred_type == 'twilio_token':
                    # For auth token, we need the SID too for full validation
                    if len(cred_value) == 32:
                        return ValidationResult(
                            service=CredentialService.TWILIO,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.7,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            metadata={'twilio_type': 'auth_token'}
                        )
                    else:
                        return ValidationResult(
                            service=CredentialService.TWILIO,
                            credential_type=cred_type,
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.9,
                            validation_method="FORMAT_CHECK",
                            response_time=time.time() - start_time,
                            error_message="Invalid Twilio Auth Token format"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.TWILIO,
                    credential_type=cred_type,
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="FORMAT_CHECK",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_stripe(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate Stripe API key"""
        start_time = time.time()
        
        async with self.rate_limiters['stripe']:
            try:
                cred_value = credential_data.get('value', '')
                
                # Stripe API validation
                headers = {
                    'Authorization': f'Bearer {cred_value}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                url = 'https://api.stripe.com/v1/balance'
                
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return ValidationResult(
                            service=CredentialService.STRIPE,
                            credential_type='stripe_key',
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            metadata={
                                'account_type': 'live' if cred_value.startswith('sk_live_') else 'test',
                                'available_balance': data.get('available', [])
                            }
                        )
                    
                    elif response.status == 401:
                        return ValidationResult(
                            service=CredentialService.STRIPE,
                            credential_type='stripe_key',
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message="Invalid Stripe API key"
                        )
                    
                    else:
                        return ValidationResult(
                            service=CredentialService.STRIPE,
                            credential_type='stripe_key',
                            value=cred_value,
                            status=ValidationStatus.FAILED,
                            confidence_score=0.0,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message=f"HTTP {response.status}"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.STRIPE,
                    credential_type='stripe_key',
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="API_TEST",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_smtp(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate SMTP credentials"""
        start_time = time.time()
        
        async with self.rate_limiters['smtp']:
            try:
                # Extract SMTP details from metadata
                smtp_server = credential_data.get('smtp_server', 'smtp.gmail.com')
                smtp_port = credential_data.get('smtp_port', 587)
                username = credential_data.get('username', '')
                password = credential_data.get('value', '')
                
                if not username or not password:
                    return ValidationResult(
                        service=CredentialService.SMTP,
                        credential_type='smtp_password',
                        value=password,
                        status=ValidationStatus.FAILED,
                        confidence_score=0.0,
                        validation_method="CONFIG_CHECK",
                        response_time=time.time() - start_time,
                        error_message="Missing username or password"
                    )
                
                # Test SMTP connection
                def test_smtp():
                    try:
                        server = smtplib.SMTP(smtp_server, smtp_port)
                        server.starttls()
                        server.login(username, password)
                        server.quit()
                        return True, None
                    except Exception as e:
                        return False, str(e)
                
                # Run in thread to avoid blocking
                loop = asyncio.get_event_loop()
                success, error = await loop.run_in_executor(None, test_smtp)
                
                response_time = time.time() - start_time
                
                if success:
                    return ValidationResult(
                        service=CredentialService.SMTP,
                        credential_type='smtp_password',
                        value=password,
                        status=ValidationStatus.VALID,
                        confidence_score=0.95,
                        validation_method="SMTP_LOGIN",
                        response_time=response_time,
                        metadata={
                            'smtp_server': smtp_server,
                            'smtp_port': smtp_port,
                            'username': username
                        }
                    )
                else:
                    return ValidationResult(
                        service=CredentialService.SMTP,
                        credential_type='smtp_password',
                        value=password,
                        status=ValidationStatus.INVALID,
                        confidence_score=0.95,
                        validation_method="SMTP_LOGIN",
                        response_time=response_time,
                        error_message=error
                    )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.SMTP,
                    credential_type='smtp_password',
                    value=credential_data.get('value', ''),
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="SMTP_LOGIN",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_github(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate GitHub token"""
        start_time = time.time()
        
        async with self.rate_limiters['github']:
            try:
                cred_value = credential_data.get('value', '')
                
                # GitHub API validation
                headers = {
                    'Authorization': f'token {cred_value}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                url = 'https://api.github.com/user'
                
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return ValidationResult(
                            service=CredentialService.GITHUB,
                            credential_type='github_token',
                            value=cred_value,
                            status=ValidationStatus.VALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            metadata={
                                'username': data.get('login', 'unknown'),
                                'user_type': data.get('type', 'User'),
                                'public_repos': data.get('public_repos', 0)
                            },
                            permissions=data.get('permissions', [])
                        )
                    
                    elif response.status == 401:
                        return ValidationResult(
                            service=CredentialService.GITHUB,
                            credential_type='github_token',
                            value=cred_value,
                            status=ValidationStatus.INVALID,
                            confidence_score=0.95,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message="Invalid GitHub token"
                        )
                    
                    else:
                        return ValidationResult(
                            service=CredentialService.GITHUB,
                            credential_type='github_token',
                            value=cred_value,
                            status=ValidationStatus.FAILED,
                            confidence_score=0.0,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message=f"HTTP {response.status}"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.GITHUB,
                    credential_type='github_token',
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="API_TEST",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_slack(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate Slack token"""
        start_time = time.time()
        
        async with self.rate_limiters['slack']:
            try:
                cred_value = credential_data.get('value', '')
                
                # Slack API validation
                headers = {
                    'Authorization': f'Bearer {cred_value}',
                    'Content-Type': 'application/json'
                }
                
                url = 'https://slack.com/api/auth.test'
                
                async with self.session.post(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('ok'):
                            return ValidationResult(
                                service=CredentialService.SLACK,
                                credential_type='slack_token',
                                value=cred_value,
                                status=ValidationStatus.VALID,
                                confidence_score=0.95,
                                validation_method="API_TEST",
                                response_time=response_time,
                                metadata={
                                    'team': data.get('team', 'unknown'),
                                    'user': data.get('user', 'unknown'),
                                    'team_id': data.get('team_id', 'unknown')
                                }
                            )
                        else:
                            return ValidationResult(
                                service=CredentialService.SLACK,
                                credential_type='slack_token',
                                value=cred_value,
                                status=ValidationStatus.INVALID,
                                confidence_score=0.95,
                                validation_method="API_TEST",
                                response_time=response_time,
                                error_message=data.get('error', 'Invalid token')
                            )
                    
                    else:
                        return ValidationResult(
                            service=CredentialService.SLACK,
                            credential_type='slack_token',
                            value=cred_value,
                            status=ValidationStatus.FAILED,
                            confidence_score=0.0,
                            validation_method="API_TEST",
                            response_time=response_time,
                            error_message=f"HTTP {response.status}"
                        )
            
            except Exception as e:
                return ValidationResult(
                    service=CredentialService.SLACK,
                    credential_type='slack_token',
                    value=cred_value,
                    status=ValidationStatus.FAILED,
                    confidence_score=0.0,
                    validation_method="API_TEST",
                    response_time=time.time() - start_time,
                    error_message=str(e)
                )
    
    async def _validate_generic(self, credential_data: Dict[str, Any]) -> Optional[ValidationResult]:
        """Generic validation for unknown credential types"""
        start_time = time.time()
        
        cred_type = credential_data.get('type', 'unknown')
        cred_value = credential_data.get('value', '')
        
        # Basic format validation
        confidence = 0.5
        status = ValidationStatus.UNKNOWN
        
        # Length-based validation
        if len(cred_value) >= 20:
            confidence += 0.1
        
        if len(cred_value) >= 32:
            confidence += 0.1
        
        # Entropy check
        unique_chars = len(set(cred_value))
        if unique_chars > 10:
            confidence += 0.1
        
        # Character set analysis
        has_upper = any(c.isupper() for c in cred_value)
        has_lower = any(c.islower() for c in cred_value)
        has_digit = any(c.isdigit() for c in cred_value)
        has_special = any(c in '._-+/=' for c in cred_value)
        
        char_variety = sum([has_upper, has_lower, has_digit, has_special])
        confidence += char_variety * 0.05
        
        if confidence > 0.7:
            status = ValidationStatus.VALID
        elif confidence < 0.3:
            status = ValidationStatus.INVALID
        
        return ValidationResult(
            service=CredentialService.GENERIC_API,
            credential_type=cred_type,
            value=cred_value,
            status=status,
            confidence_score=min(1.0, confidence),
            validation_method="HEURISTIC",
            response_time=time.time() - start_time,
            metadata={
                'length': len(cred_value),
                'unique_chars': unique_chars,
                'character_variety': char_variety
            }
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        stats = self.stats.copy()
        stats['cache_size'] = len(self.validation_cache)
        return stats
    
    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        self.logger.info("🧹 Validation cache cleared")
    
    async def shutdown(self):
        """Shutdown module"""
        await self._close_session()
        self.logger.info("🛑 Credential Validator Module shutdown completed")