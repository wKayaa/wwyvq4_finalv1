#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Credential Validator
Author: wKayaa
Date: 2025-01-15

Module de validation de credentials en temps réel.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import ssl
import base64


@dataclass
class Credential:
    """Représentation d'un credential"""
    service: str
    endpoint: str
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationResult:
    """Résultat de validation d'un credential"""
    credential: Credential
    is_valid: bool
    status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    validation_time: float = 0.0
    service_info: Dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=datetime.utcnow)


class CredentialValidator:
    """
    Validateur de credentials multi-services
    
    Responsabilités:
    - Validation de credentials en temps réel
    - Support multi-services (Kubernetes, AWS, Azure, GCP, etc.)
    - Détection automatique de services
    - Récupération d'informations de service
    """
    
    def __init__(self, config_manager, logger):
        """
        Initialise le validateur de credentials
        
        Args:
            config_manager: Gestionnaire de configuration
            logger: Logger WWYVQ
        """
        self.config_manager = config_manager
        self.logger = logger
        self.validated_credentials: List[ValidationResult] = []
        
        # Configuration SSL permissive
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def validate_credential(self, credential: Credential) -> ValidationResult:
        """
        Valide un credential spécifique
        
        Args:
            credential: Credential à valider
            
        Returns:
            ValidationResult: Résultat de la validation
        """
        start_time = datetime.utcnow()
        
        try:
            # Sélection de la méthode de validation selon le service
            if credential.service.lower() == 'kubernetes':
                result = await self._validate_kubernetes(credential)
            elif credential.service.lower() == 'aws':
                result = await self._validate_aws(credential)
            elif credential.service.lower() == 'azure':
                result = await self._validate_azure(credential)
            elif credential.service.lower() == 'gcp':
                result = await self._validate_gcp(credential)
            elif credential.service.lower() == 'docker':
                result = await self._validate_docker(credential)
            elif credential.service.lower() in ['mysql', 'postgresql', 'mssql']:
                result = await self._validate_database(credential)
            elif credential.service.lower() in ['smtp', 'imap', 'pop3']:
                result = await self._validate_email(credential)
            else:
                result = await self._validate_generic_http(credential)
            
            # Calcul du temps de validation
            end_time = datetime.utcnow()
            result.validation_time = (end_time - start_time).total_seconds()
            
            # Stockage du résultat
            self.validated_credentials.append(result)
            
            # Logging
            status = "VALID" if result.is_valid else "INVALID"
            self.logger.info(
                f"Credential validation: {credential.service} @ {credential.endpoint} → {status}",
                module="validator.credential_validator",
                service=credential.service,
                endpoint=credential.endpoint,
                valid=result.is_valid
            )
            
            return result
            
        except Exception as e:
            # Gestion des erreurs
            error_result = ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e),
                validation_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            self.logger.error(
                f"Credential validation error: {credential.service} @ {credential.endpoint}: {e}",
                module="validator.credential_validator",
                service=credential.service,
                endpoint=credential.endpoint
            )
            
            return error_result
    
    async def _validate_kubernetes(self, credential: Credential) -> ValidationResult:
        """Valide un credential Kubernetes"""
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Test d'accès à l'API Kubernetes
            api_url = f"{credential.endpoint}/api/v1"
            headers = {}
            
            if credential.token:
                headers['Authorization'] = f'Bearer {credential.token}'
            elif credential.username and credential.password:
                auth_str = base64.b64encode(f"{credential.username}:{credential.password}".encode()).decode()
                headers['Authorization'] = f'Basic {auth_str}'
            
            try:
                async with session.get(api_url, headers=headers, timeout=30) as response:
                    is_valid = response.status in [200, 401, 403]  # 401/403 indiquent un service valide
                    
                    service_info = {}
                    if response.status == 200:
                        # Récupération d'informations additionnelles
                        try:
                            data = await response.json()
                            service_info = {
                                'api_version': data.get('resources', [{}])[0].get('groupVersion', 'unknown'),
                                'accessible': True
                            }
                            
                            # Test version
                            version_url = f"{credential.endpoint}/version"
                            async with session.get(version_url, headers=headers) as version_response:
                                if version_response.status == 200:
                                    version_data = await version_response.json()
                                    service_info['version'] = version_data.get('gitVersion', 'unknown')
                        except:
                            pass
                    
                    return ValidationResult(
                        credential=credential,
                        is_valid=(response.status == 200),
                        status_code=response.status,
                        service_info=service_info
                    )
                    
            except Exception as e:
                return ValidationResult(
                    credential=credential,
                    is_valid=False,
                    error_message=str(e)
                )
    
    async def _validate_aws(self, credential: Credential) -> ValidationResult:
        """Valide un credential AWS"""
        # Simulation de validation AWS (nécessiterait boto3 pour une vraie implémentation)
        try:
            # Test basique de l'endpoint STS
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # AWS STS endpoint pour validation
                sts_url = "https://sts.amazonaws.com/"
                
                # Construction de la requête AWS signée (simplifié)
                params = {
                    'Action': 'GetCallerIdentity',
                    'Version': '2011-06-15'
                }
                
                async with session.get(sts_url, params=params, timeout=30) as response:
                    # Pour AWS, on simule une validation basique
                    is_valid = response.status in [200, 403]  # 403 = credentials invalides mais service accessible
                    
                    service_info = {
                        'service': 'AWS',
                        'region': credential.metadata.get('region', 'us-east-1')
                    }
                    
                    return ValidationResult(
                        credential=credential,
                        is_valid=is_valid,
                        status_code=response.status,
                        service_info=service_info
                    )
                    
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def _validate_azure(self, credential: Credential) -> ValidationResult:
        """Valide un credential Azure"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Azure Management API endpoint
                azure_url = "https://management.azure.com/subscriptions"
                
                headers = {}
                if credential.token:
                    headers['Authorization'] = f'Bearer {credential.token}'
                
                async with session.get(azure_url, headers=headers, timeout=30) as response:
                    is_valid = response.status in [200, 401, 403]
                    
                    service_info = {
                        'service': 'Azure',
                        'tenant_id': credential.metadata.get('tenant_id', 'unknown')
                    }
                    
                    return ValidationResult(
                        credential=credential,
                        is_valid=(response.status == 200),
                        status_code=response.status,
                        service_info=service_info
                    )
                    
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def _validate_gcp(self, credential: Credential) -> ValidationResult:
        """Valide un credential Google Cloud Platform"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # GCP Compute API endpoint
                gcp_url = "https://compute.googleapis.com/compute/v1/projects"
                
                headers = {}
                if credential.token:
                    headers['Authorization'] = f'Bearer {credential.token}'
                elif credential.api_key:
                    gcp_url += f"?key={credential.api_key}"
                
                async with session.get(gcp_url, headers=headers, timeout=30) as response:
                    is_valid = response.status in [200, 401, 403]
                    
                    service_info = {
                        'service': 'GCP',
                        'project_id': credential.metadata.get('project_id', 'unknown')
                    }
                    
                    return ValidationResult(
                        credential=credential,
                        is_valid=(response.status == 200),
                        status_code=response.status,
                        service_info=service_info
                    )
                    
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def _validate_docker(self, credential: Credential) -> ValidationResult:
        """Valide un credential Docker Registry"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Docker Registry API v2
                registry_url = f"{credential.endpoint}/v2/"
                
                headers = {}
                if credential.username and credential.password:
                    auth_str = base64.b64encode(f"{credential.username}:{credential.password}".encode()).decode()
                    headers['Authorization'] = f'Basic {auth_str}'
                
                async with session.get(registry_url, headers=headers, timeout=30) as response:
                    is_valid = response.status in [200, 401]
                    
                    service_info = {
                        'service': 'Docker Registry',
                        'api_version': '2'
                    }
                    
                    return ValidationResult(
                        credential=credential,
                        is_valid=(response.status == 200),
                        status_code=response.status,
                        service_info=service_info
                    )
                    
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def _validate_database(self, credential: Credential) -> ValidationResult:
        """Valide un credential de base de données"""
        # Pour les bases de données, on simule la validation
        # Une vraie implémentation nécessiterait les drivers appropriés
        try:
            import socket
            
            # Test de connectivité basique
            host, port = credential.endpoint.split(':') if ':' in credential.endpoint else (credential.endpoint, 3306)
            port = int(port) if isinstance(port, str) else port
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            is_valid = (result == 0)  # Port accessible
            
            service_info = {
                'service': credential.service,
                'host': host,
                'port': port,
                'connection_test': 'passed' if is_valid else 'failed'
            }
            
            return ValidationResult(
                credential=credential,
                is_valid=is_valid,
                service_info=service_info
            )
            
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def _validate_email(self, credential: Credential) -> ValidationResult:
        """Valide un credential email"""
        # Simulation de validation email
        try:
            import socket
            
            # Test de connectivité SMTP/IMAP
            default_ports = {
                'smtp': 587,
                'imap': 993,
                'pop3': 995
            }
            
            host, port = credential.endpoint.split(':') if ':' in credential.endpoint else (
                credential.endpoint, 
                default_ports.get(credential.service.lower(), 587)
            )
            port = int(port) if isinstance(port, str) else port
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            is_valid = (result == 0)
            
            service_info = {
                'service': credential.service.upper(),
                'host': host,
                'port': port,
                'protocol': credential.service.lower()
            }
            
            return ValidationResult(
                credential=credential,
                is_valid=is_valid,
                service_info=service_info
            )
            
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def _validate_generic_http(self, credential: Credential) -> ValidationResult:
        """Valide un credential HTTP générique"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                headers = {}
                
                if credential.token:
                    headers['Authorization'] = f'Bearer {credential.token}'
                elif credential.api_key:
                    headers['X-API-Key'] = credential.api_key
                elif credential.username and credential.password:
                    auth_str = base64.b64encode(f"{credential.username}:{credential.password}".encode()).decode()
                    headers['Authorization'] = f'Basic {auth_str}'
                
                async with session.get(credential.endpoint, headers=headers, timeout=30) as response:
                    is_valid = response.status in [200, 401, 403]
                    
                    service_info = {
                        'service': credential.service,
                        'status_code': response.status,
                        'content_type': response.headers.get('content-type', 'unknown')
                    }
                    
                    return ValidationResult(
                        credential=credential,
                        is_valid=(response.status == 200),
                        status_code=response.status,
                        service_info=service_info
                    )
                    
        except Exception as e:
            return ValidationResult(
                credential=credential,
                is_valid=False,
                error_message=str(e)
            )
    
    async def validate_multiple_credentials(self, credentials: List[Credential]) -> List[ValidationResult]:
        """
        Valide plusieurs credentials en parallèle
        
        Args:
            credentials: Liste des credentials à valider
            
        Returns:
            List[ValidationResult]: Résultats de validation
        """
        config = self.config_manager.get_config()
        semaphore = asyncio.Semaphore(config.core.max_concurrent)
        
        async def validate_with_semaphore(credential):
            async with semaphore:
                return await self.validate_credential(credential)
        
        # Création des tâches
        tasks = [validate_with_semaphore(cred) for cred in credentials]
        
        # Exécution parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des résultats
        valid_results = []
        for result in results:
            if isinstance(result, ValidationResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                self.logger.error(
                    f"Validation error: {result}",
                    module="validator.credential_validator"
                )
        
        # Statistiques
        valid_count = sum(1 for r in valid_results if r.is_valid)
        total_count = len(valid_results)
        
        self.logger.info(
            f"Bulk validation completed: {valid_count}/{total_count} valid credentials",
            module="validator.credential_validator",
            valid_count=valid_count,
            total_count=total_count
        )
        
        return valid_results
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de validation
        
        Returns:
            Dict: Statistiques
        """
        total_validations = len(self.validated_credentials)
        valid_credentials = sum(1 for r in self.validated_credentials if r.is_valid)
        
        # Statistiques par service
        services_stats = {}
        for result in self.validated_credentials:
            service = result.credential.service
            if service not in services_stats:
                services_stats[service] = {'total': 0, 'valid': 0}
            
            services_stats[service]['total'] += 1
            if result.is_valid:
                services_stats[service]['valid'] += 1
        
        # Temps de validation moyens
        validation_times = [r.validation_time for r in self.validated_credentials if r.validation_time > 0]
        avg_validation_time = sum(validation_times) / len(validation_times) if validation_times else 0
        
        return {
            'total_validations': total_validations,
            'valid_credentials': valid_credentials,
            'invalid_credentials': total_validations - valid_credentials,
            'success_rate': (valid_credentials / total_validations * 100) if total_validations > 0 else 0,
            'services_stats': services_stats,
            'avg_validation_time': avg_validation_time,
            'total_services': len(services_stats)
        }
    
    def export_valid_credentials(self, file_path: str, format_type: str = "json"):
        """
        Exporte les credentials valides
        
        Args:
            file_path: Chemin du fichier d'export
            format_type: Format d'export (json, csv)
        """
        valid_results = [r for r in self.validated_credentials if r.is_valid]
        
        try:
            if format_type.lower() == "json":
                export_data = []
                for result in valid_results:
                    export_data.append({
                        'service': result.credential.service,
                        'endpoint': result.credential.endpoint,
                        'username': result.credential.username,
                        'password': result.credential.password,
                        'token': result.credential.token,
                        'api_key': result.credential.api_key,
                        'metadata': result.credential.metadata,
                        'service_info': result.service_info,
                        'validated_at': result.validated_at.isoformat()
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif format_type.lower() == "csv":
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Service', 'Endpoint', 'Username', 'Password', 'Token', 'API_Key', 'Validated_At'])
                    
                    for result in valid_results:
                        writer.writerow([
                            result.credential.service,
                            result.credential.endpoint,
                            result.credential.username or '',
                            result.credential.password or '',
                            result.credential.token or '',
                            result.credential.api_key or '',
                            result.validated_at.isoformat()
                        ])
            
            self.logger.info(
                f"Exported {len(valid_results)} valid credentials to {file_path}",
                module="validator.credential_validator"
            )
            
        except Exception as e:
            self.logger.error(
                f"Failed to export credentials: {e}",
                module="validator.credential_validator"
            )