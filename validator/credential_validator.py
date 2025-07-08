#!/usr/bin/env python3
"""
WWYVQ v2.1 Credential Validator Module
Real-time validation of credentials with multi-level validation

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
import socket
import ssl

from .base_validator import BaseValidatorModule, ValidationResult, ValidationStatus


class CredentialValidatorModule(BaseValidatorModule):
    """
    Advanced credential validation module with real-time validation
    Supports AWS, SMTP, SendGrid, Mailgun, Twilio, and more
    """
    
    def __init__(self):
        super().__init__(
            name="CredentialValidator",
            description="Real-time validation of credentials with multi-level validation"
        )
        
        # Rate limiting
        self.rate_limits = {
            'aws': {'requests': 0, 'window_start': datetime.utcnow(), 'max_requests': 100, 'window_seconds': 3600},
            'sendgrid': {'requests': 0, 'window_start': datetime.utcnow(), 'max_requests': 100, 'window_seconds': 3600},
            'mailgun': {'requests': 0, 'window_start': datetime.utcnow(), 'max_requests': 100, 'window_seconds': 3600},
            'smtp': {'requests': 0, 'window_start': datetime.utcnow(), 'max_requests': 50, 'window_seconds': 3600},
            'twilio': {'requests': 0, 'window_start': datetime.utcnow(), 'max_requests': 100, 'window_seconds': 3600},
        }
        
        # Validation cache
        self.validation_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Supported credential types
        self.supported_types = {
            'aws_access_key_id': self._validate_aws_credentials,
            'aws_secret_access_key': self._validate_aws_credentials,
            'sendgrid_api_key': self._validate_sendgrid_key,
            'mailgun_api_key': self._validate_mailgun_key,
            'smtp_username': self._validate_smtp_credentials,
            'smtp_password': self._validate_smtp_credentials,
            'twilio_account_sid': self._validate_twilio_credentials,
            'twilio_auth_token': self._validate_twilio_credentials,
            'database_url': self._validate_database_url,
            'api_key': self._validate_generic_api_key,
            'jwt_token': self._validate_jwt_token,
            'github_token': self._validate_github_token,
            'slack_token': self._validate_slack_token,
            'discord_token': self._validate_discord_token,
        }
    
    async def execute_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute credential validation asynchronously"""
        try:
            # Get credentials from context
            credentials = []
            
            # Check if we have results from previous phases
            if 'results' in context:
                if 'exploitation' in context['results']:
                    exploitation_results = context['results']['exploitation']
                    if 'credentials' in exploitation_results:
                        credentials.extend(exploitation_results['credentials'])
            
            # Check if we have direct credentials in context
            if 'credentials' in context:
                credentials.extend(context['credentials'])
            
            if not credentials:
                return {'credentials_validated': 0, 'valid_credentials': [], 'invalid_credentials': []}
            
            self.logger.info(f"🔍 Validating {len(credentials)} credentials")
            
            # Validate credentials
            validation_results = await self.validate_batch(credentials)
            
            # Categorize results
            valid_credentials = []
            invalid_credentials = []
            
            for result in validation_results:
                if result.status == ValidationStatus.VALID:
                    valid_credentials.append({
                        'type': result.credential_type,
                        'value': result.credential_value,
                        'confidence': result.confidence,
                        'details': result.details,
                        'service_info': result.service_info,
                        'timestamp': result.timestamp.isoformat()
                    })
                elif result.status == ValidationStatus.INVALID:
                    invalid_credentials.append({
                        'type': result.credential_type,
                        'value': result.credential_value,
                        'error': result.error_message,
                        'timestamp': result.timestamp.isoformat()
                    })
            
            aggregated = {
                'credentials_validated': len(validation_results),
                'valid_credentials': valid_credentials,
                'invalid_credentials': invalid_credentials,
                'validation_stats': self.get_stats()
            }
            
            self.logger.info(f"✅ Validation complete: {len(valid_credentials)} valid, {len(invalid_credentials)} invalid")
            return aggregated
            
        except Exception as e:
            self.logger.error(f"❌ Credential validation failed: {e}")
            return {'error': str(e)}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute credential validation synchronously"""
        return asyncio.run(self.execute_async(context))
    
    async def _validate_credential_impl(self, credential: Dict[str, Any]) -> ValidationResult:
        """Implementation of credential validation"""
        try:
            credential_type = credential.get('type', '')
            credential_value = credential.get('value', '')
            
            # Check cache first
            cache_key = f"{credential_type}:{credential_value}"
            if cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                if datetime.utcnow() - cached_result['timestamp'] < timedelta(seconds=self.cache_ttl):
                    return cached_result['result']
            
            # Check if we support this credential type
            if credential_type not in self.supported_types:
                return ValidationResult(
                    credential_type=credential_type,
                    credential_value=credential_value,
                    status=ValidationStatus.UNKNOWN,
                    confidence=0.0,
                    error_message=f"Unsupported credential type: {credential_type}"
                )
            
            # Check rate limiting
            service = self._get_service_for_type(credential_type)
            if self._is_rate_limited(service):
                await self._wait_for_rate_limit(service)
            
            # Validate the credential
            validator_func = self.supported_types[credential_type]
            result = await validator_func(credential)
            
            # Cache the result
            self.validation_cache[cache_key] = {
                'result': result,
                'timestamp': datetime.utcnow()
            }
            
            # Update rate limit
            self._update_rate_limit(service)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error validating credential {credential_type}: {e}")
            return ValidationResult(
                credential_type=credential.get('type', 'unknown'),
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    def _get_service_for_type(self, credential_type: str) -> str:
        """Get service name for credential type"""
        if credential_type.startswith('aws_'):
            return 'aws'
        elif credential_type.startswith('sendgrid_'):
            return 'sendgrid'
        elif credential_type.startswith('mailgun_'):
            return 'mailgun'
        elif credential_type.startswith('smtp_'):
            return 'smtp'
        elif credential_type.startswith('twilio_'):
            return 'twilio'
        else:
            return 'generic'
    
    def _is_rate_limited(self, service: str) -> bool:
        """Check if service is rate limited"""
        if service not in self.rate_limits:
            return False
        
        rate_info = self.rate_limits[service]
        now = datetime.utcnow()
        
        # Reset window if expired
        if (now - rate_info['window_start']).total_seconds() >= rate_info['window_seconds']:
            rate_info['requests'] = 0
            rate_info['window_start'] = now
            return False
        
        return rate_info['requests'] >= rate_info['max_requests']
    
    async def _wait_for_rate_limit(self, service: str) -> None:
        """Wait for rate limit to reset"""
        if service not in self.rate_limits:
            return
        
        rate_info = self.rate_limits[service]
        now = datetime.utcnow()
        window_elapsed = (now - rate_info['window_start']).total_seconds()
        wait_time = rate_info['window_seconds'] - window_elapsed
        
        if wait_time > 0:
            self.logger.info(f"⏳ Rate limited for {service}, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
    
    def _update_rate_limit(self, service: str) -> None:
        """Update rate limit counters"""
        if service in self.rate_limits:
            self.rate_limits[service]['requests'] += 1
    
    async def _validate_aws_credentials(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate AWS credentials"""
        try:
            # For AWS credentials, we need both access key and secret key
            # This is a simplified validation - in real implementation, you'd use AWS STS
            
            credential_type = credential.get('type', '')
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if credential_type == 'aws_access_key_id':
                if not re.match(r'^AKIA[0-9A-Z]{16}$', credential_value):
                    return ValidationResult(
                        credential_type=credential_type,
                        credential_value=credential_value,
                        status=ValidationStatus.INVALID,
                        confidence=90.0,
                        error_message="Invalid AWS access key format"
                    )
            elif credential_type == 'aws_secret_access_key':
                if len(credential_value) != 40:
                    return ValidationResult(
                        credential_type=credential_type,
                        credential_value=credential_value,
                        status=ValidationStatus.INVALID,
                        confidence=90.0,
                        error_message="Invalid AWS secret key format"
                    )
            
            # Simulate AWS STS validation (in real implementation, use boto3)
            # Here we return unknown since we can't actually validate without both keys
            return ValidationResult(
                credential_type=credential_type,
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=75.0,
                details={'format_valid': True},
                error_message="AWS validation requires both access key and secret key"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type=credential.get('type', 'aws'),
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_sendgrid_key(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate SendGrid API key"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if not re.match(r'^SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}$', credential_value):
                return ValidationResult(
                    credential_type='sendgrid_api_key',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid SendGrid API key format"
                )
            
            # Simulate API validation (in real implementation, make HTTP request to SendGrid API)
            import aiohttp
            
            headers = {
                'Authorization': f'Bearer {credential_value}',
                'Content-Type': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('https://api.sendgrid.com/v3/user/account', headers=headers) as response:
                    if response.status == 200:
                        account_info = await response.json()
                        return ValidationResult(
                            credential_type='sendgrid_api_key',
                            credential_value=credential_value,
                            status=ValidationStatus.VALID,
                            confidence=95.0,
                            details={'format_valid': True},
                            service_info={
                                'service': 'SendGrid',
                                'account_type': account_info.get('type', 'unknown'),
                                'email': account_info.get('email', 'unknown')
                            }
                        )
                    elif response.status == 401:
                        return ValidationResult(
                            credential_type='sendgrid_api_key',
                            credential_value=credential_value,
                            status=ValidationStatus.INVALID,
                            confidence=95.0,
                            error_message="Invalid SendGrid API key - unauthorized"
                        )
                    else:
                        return ValidationResult(
                            credential_type='sendgrid_api_key',
                            credential_value=credential_value,
                            status=ValidationStatus.UNKNOWN,
                            confidence=50.0,
                            error_message=f"SendGrid API returned status {response.status}"
                        )
            
        except Exception as e:
            return ValidationResult(
                credential_type='sendgrid_api_key',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_mailgun_key(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate Mailgun API key"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if not re.match(r'^key-[a-fA-F0-9]{32}$', credential_value):
                return ValidationResult(
                    credential_type='mailgun_api_key',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid Mailgun API key format"
                )
            
            # Simulate API validation (in real implementation, make HTTP request to Mailgun API)
            import aiohttp
            import base64
            
            auth_string = base64.b64encode(f'api:{credential_value}'.encode()).decode()
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('https://api.mailgun.net/v3/domains', headers=headers) as response:
                    if response.status == 200:
                        domains_info = await response.json()
                        return ValidationResult(
                            credential_type='mailgun_api_key',
                            credential_value=credential_value,
                            status=ValidationStatus.VALID,
                            confidence=95.0,
                            details={'format_valid': True},
                            service_info={
                                'service': 'Mailgun',
                                'domains_count': len(domains_info.get('items', [])),
                                'total_count': domains_info.get('total_count', 0)
                            }
                        )
                    elif response.status == 401:
                        return ValidationResult(
                            credential_type='mailgun_api_key',
                            credential_value=credential_value,
                            status=ValidationStatus.INVALID,
                            confidence=95.0,
                            error_message="Invalid Mailgun API key - unauthorized"
                        )
                    else:
                        return ValidationResult(
                            credential_type='mailgun_api_key',
                            credential_value=credential_value,
                            status=ValidationStatus.UNKNOWN,
                            confidence=50.0,
                            error_message=f"Mailgun API returned status {response.status}"
                        )
            
        except Exception as e:
            return ValidationResult(
                credential_type='mailgun_api_key',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_smtp_credentials(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate SMTP credentials"""
        try:
            credential_type = credential.get('type', '')
            credential_value = credential.get('value', '')
            
            # For SMTP validation, we need host, port, username, and password
            # This is a simplified validation
            
            if credential_type == 'smtp_username':
                # Basic email format validation
                if '@' not in credential_value:
                    return ValidationResult(
                        credential_type=credential_type,
                        credential_value=credential_value,
                        status=ValidationStatus.INVALID,
                        confidence=70.0,
                        error_message="Invalid SMTP username format (should be email)"
                    )
                
                return ValidationResult(
                    credential_type=credential_type,
                    credential_value=credential_value,
                    status=ValidationStatus.UNKNOWN,
                    confidence=60.0,
                    details={'format_valid': True},
                    error_message="SMTP validation requires host, port, username, and password"
                )
            
            elif credential_type == 'smtp_password':
                # Basic length validation
                if len(credential_value) < 4:
                    return ValidationResult(
                        credential_type=credential_type,
                        credential_value=credential_value,
                        status=ValidationStatus.INVALID,
                        confidence=70.0,
                        error_message="SMTP password too short"
                    )
                
                return ValidationResult(
                    credential_type=credential_type,
                    credential_value=credential_value,
                    status=ValidationStatus.UNKNOWN,
                    confidence=60.0,
                    details={'format_valid': True},
                    error_message="SMTP validation requires host, port, username, and password"
                )
            
        except Exception as e:
            return ValidationResult(
                credential_type=credential.get('type', 'smtp'),
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_twilio_credentials(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate Twilio credentials"""
        try:
            credential_type = credential.get('type', '')
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if credential_type == 'twilio_account_sid':
                if not re.match(r'^AC[a-fA-F0-9]{32}$', credential_value):
                    return ValidationResult(
                        credential_type=credential_type,
                        credential_value=credential_value,
                        status=ValidationStatus.INVALID,
                        confidence=90.0,
                        error_message="Invalid Twilio Account SID format"
                    )
            elif credential_type == 'twilio_auth_token':
                if len(credential_value) != 32:
                    return ValidationResult(
                        credential_type=credential_type,
                        credential_value=credential_value,
                        status=ValidationStatus.INVALID,
                        confidence=90.0,
                        error_message="Invalid Twilio Auth Token format"
                    )
            
            # Simulate API validation (in real implementation, make HTTP request to Twilio API)
            return ValidationResult(
                credential_type=credential_type,
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=75.0,
                details={'format_valid': True},
                error_message="Twilio validation requires both Account SID and Auth Token"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type=credential.get('type', 'twilio'),
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_database_url(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate database URL"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic URL format validation
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://[^\\s]+$', credential_value):
                return ValidationResult(
                    credential_type='database_url',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid database URL format"
                )
            
            # Extract database type
            db_type = credential_value.split('://')[0].lower()
            
            return ValidationResult(
                credential_type='database_url',
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=70.0,
                details={'format_valid': True, 'database_type': db_type},
                error_message="Database URL format valid, but connection not tested"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type='database_url',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_generic_api_key(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate generic API key"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic validation
            if len(credential_value) < 8:
                return ValidationResult(
                    credential_type='api_key',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=70.0,
                    error_message="API key too short"
                )
            
            return ValidationResult(
                credential_type='api_key',
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=60.0,
                details={'format_valid': True},
                error_message="Generic API key - service unknown"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type='api_key',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_jwt_token(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate JWT token"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic JWT format validation
            if not re.match(r'^eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*$', credential_value):
                return ValidationResult(
                    credential_type='jwt_token',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid JWT token format"
                )
            
            # Try to decode (without verification for security reasons)
            try:
                import base64
                import json
                
                # Decode header
                header_data = credential_value.split('.')[0]
                # Add padding if needed
                header_data += '=' * (4 - len(header_data) % 4)
                header = json.loads(base64.b64decode(header_data))
                
                # Decode payload
                payload_data = credential_value.split('.')[1]
                payload_data += '=' * (4 - len(payload_data) % 4)
                payload = json.loads(base64.b64decode(payload_data))
                
                return ValidationResult(
                    credential_type='jwt_token',
                    credential_value=credential_value,
                    status=ValidationStatus.VALID,
                    confidence=85.0,
                    details={
                        'format_valid': True,
                        'header': header,
                        'payload': {k: v for k, v in payload.items() if k not in ['exp', 'iat', 'nbf']}
                    },
                    service_info={
                        'service': 'JWT',
                        'algorithm': header.get('alg', 'unknown'),
                        'type': header.get('typ', 'unknown')
                    }
                )
                
            except Exception:
                return ValidationResult(
                    credential_type='jwt_token',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=80.0,
                    error_message="JWT token format appears valid but cannot be decoded"
                )
            
        except Exception as e:
            return ValidationResult(
                credential_type='jwt_token',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_github_token(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate GitHub token"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if not re.match(r'^gh[prao]_[A-Za-z0-9]{36}$', credential_value):
                return ValidationResult(
                    credential_type='github_token',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid GitHub token format"
                )
            
            return ValidationResult(
                credential_type='github_token',
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=75.0,
                details={'format_valid': True},
                error_message="GitHub token format valid, but API validation not implemented"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type='github_token',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_slack_token(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate Slack token"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if not re.match(r'^xox[bpras]-[A-Za-z0-9-]{10,}$', credential_value):
                return ValidationResult(
                    credential_type='slack_token',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid Slack token format"
                )
            
            return ValidationResult(
                credential_type='slack_token',
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=75.0,
                details={'format_valid': True},
                error_message="Slack token format valid, but API validation not implemented"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type='slack_token',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _validate_discord_token(self, credential: Dict[str, Any]) -> ValidationResult:
        """Validate Discord token"""
        try:
            credential_value = credential.get('value', '')
            
            # Basic format validation
            if not re.match(r'^[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}$', credential_value):
                return ValidationResult(
                    credential_type='discord_token',
                    credential_value=credential_value,
                    status=ValidationStatus.INVALID,
                    confidence=90.0,
                    error_message="Invalid Discord token format"
                )
            
            return ValidationResult(
                credential_type='discord_token',
                credential_value=credential_value,
                status=ValidationStatus.UNKNOWN,
                confidence=75.0,
                details={'format_valid': True},
                error_message="Discord token format valid, but API validation not implemented"
            )
            
        except Exception as e:
            return ValidationResult(
                credential_type='discord_token',
                credential_value=credential.get('value', ''),
                status=ValidationStatus.ERROR,
                confidence=0.0,
                error_message=str(e)
            )
    
    def supports_credential_type(self, credential_type: str) -> bool:
        """Check if module supports validating this credential type"""
        return credential_type in self.supported_types
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported credential types"""
        return list(self.supported_types.keys())