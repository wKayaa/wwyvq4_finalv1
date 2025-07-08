#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Telegram Notifier
Author: wKayaa
Date: 2025-01-15

Module de notification Telegram professionnel.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import html


@dataclass
class TelegramMessage:
    """Représentation d'un message Telegram"""
    text: str
    chat_id: str
    parse_mode: str = "HTML"
    disable_notification: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationResult:
    """Résultat d'envoi de notification"""
    message: TelegramMessage
    success: bool
    message_id: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    sent_at: Optional[datetime] = None


class TelegramNotifier:
    """
    Système de notification Telegram professionnel
    
    Responsabilités:
    - Envoi de notifications temps réel
    - Formatage de messages avancé
    - Gestion des erreurs et retry
    - Statistiques d'envoi
    """
    
    def __init__(self, config_manager, logger):
        """
        Initialise le notificateur Telegram
        
        Args:
            config_manager: Gestionnaire de configuration
            logger: Logger WWYVQ
        """
        self.config_manager = config_manager
        self.logger = logger
        self.sent_messages: List[NotificationResult] = []
        
        # Configuration Telegram
        config = self.config_manager.get_config()
        telegram_config = config.modules.notifier.get('telegram', {})
        
        self.token = telegram_config.get('token', '')
        self.default_chat_id = telegram_config.get('chat_id', '')
        self.enabled = telegram_config.get('enabled', False)
        
        if not self.token:
            self.logger.warning(
                "Telegram token not configured",
                module="notifier.telegram"
            )
            self.enabled = False
        
        # API Telegram
        self.api_base = f"https://api.telegram.org/bot{self.token}"
    
    async def send_message(self, text: str, chat_id: Optional[str] = None, 
                          parse_mode: str = "HTML", priority: str = "normal") -> NotificationResult:
        """
        Envoie un message Telegram
        
        Args:
            text: Texte du message
            chat_id: ID du chat (optionnel, utilise le défaut si non spécifié)
            parse_mode: Mode de parsing (HTML, Markdown)
            priority: Priorité du message (low, normal, high, critical)
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        if not self.enabled:
            return NotificationResult(
                message=TelegramMessage(text=text, chat_id=chat_id or ""),
                success=False,
                error_message="Telegram notifications disabled"
            )
        
        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            return NotificationResult(
                message=TelegramMessage(text=text, chat_id=""),
                success=False,
                error_message="No chat ID specified"
            )
        
        # Création du message
        message = TelegramMessage(
            text=text,
            chat_id=target_chat_id,
            parse_mode=parse_mode,
            disable_notification=(priority == "low"),
            metadata={"priority": priority}
        )
        
        try:
            # Envoi via API Telegram
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/sendMessage"
                
                payload = {
                    "chat_id": target_chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_notification": message.disable_notification
                }
                
                async with session.post(url, json=payload, timeout=30) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("ok"):
                        # Succès
                        result = NotificationResult(
                            message=message,
                            success=True,
                            message_id=response_data.get("result", {}).get("message_id"),
                            response_data=response_data,
                            sent_at=datetime.utcnow()
                        )
                        
                        self.logger.info(
                            f"Telegram message sent successfully",
                            module="notifier.telegram",
                            chat_id=target_chat_id,
                            priority=priority
                        )
                        
                    else:
                        # Erreur
                        error_msg = response_data.get("description", f"HTTP {response.status}")
                        result = NotificationResult(
                            message=message,
                            success=False,
                            error_message=error_msg,
                            response_data=response_data
                        )
                        
                        self.logger.error(
                            f"Telegram message failed: {error_msg}",
                            module="notifier.telegram",
                            chat_id=target_chat_id
                        )
            
            # Stockage du résultat
            self.sent_messages.append(result)
            return result
            
        except Exception as e:
            error_result = NotificationResult(
                message=message,
                success=False,
                error_message=str(e)
            )
            
            self.logger.error(
                f"Telegram send error: {e}",
                module="notifier.telegram",
                chat_id=target_chat_id
            )
            
            return error_result
    
    async def send_operation_start(self, operation_type: str, targets_count: int, 
                                  session_id: str, mode: str = "standard") -> NotificationResult:
        """
        Envoie une notification de début d'opération
        
        Args:
            operation_type: Type d'opération (scan, exploit, validate)
            targets_count: Nombre de cibles
            session_id: ID de session
            mode: Mode d'exécution
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        emoji_map = {
            "scan": "🔍",
            "exploit": "🚀", 
            "validate": "✅"
        }
        
        emoji = emoji_map.get(operation_type, "⚡")
        
        message = f"""
{emoji} <b>WWYVQ Operation Started</b>

<b>Type:</b> {operation_type.upper()}
<b>Mode:</b> {mode.upper()}
<b>Targets:</b> {targets_count:,}
<b>Session:</b> <code>{session_id}</code>
<b>Started:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

<i>Operation in progress...</i>
        """.strip()
        
        return await self.send_message(message, priority="normal")
    
    async def send_operation_complete(self, operation_type: str, session_id: str,
                                    results: Dict[str, Any]) -> NotificationResult:
        """
        Envoie une notification de fin d'opération
        
        Args:
            operation_type: Type d'opération
            session_id: ID de session
            results: Résultats de l'opération
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        emoji_map = {
            "scan": "🔍",
            "exploit": "🚀",
            "validate": "✅"
        }
        
        emoji = emoji_map.get(operation_type, "⚡")
        
        # Extraction des statistiques
        stats = results.get('statistics', {})
        duration = results.get('duration', 'unknown')
        
        message = f"""
{emoji} <b>WWYVQ Operation Complete</b>

<b>Type:</b> {operation_type.upper()}
<b>Session:</b> <code>{session_id}</code>
<b>Duration:</b> {duration}
<b>Status:</b> ✅ COMPLETED

<b>📊 Results:</b>
"""
        
        # Ajout des statistiques spécifiques
        if operation_type == "scan":
            clusters_found = stats.get('clusters_found', 0)
            targets_scanned = stats.get('targets_scanned', 0)
            message += f"""
• Targets Scanned: {targets_scanned:,}
• Clusters Found: {clusters_found:,}
"""
        
        elif operation_type == "exploit":
            clusters_exploited = stats.get('clusters_exploited', 0)
            secrets_extracted = stats.get('secrets_extracted', 0)
            message += f"""
• Clusters Exploited: {clusters_exploited:,}
• Secrets Extracted: {secrets_extracted:,}
"""
        
        elif operation_type == "validate":
            valid_credentials = stats.get('valid_credentials', 0)
            total_credentials = stats.get('total_credentials', 0)
            success_rate = stats.get('success_rate', 0)
            message += f"""
• Valid Credentials: {valid_credentials:,}
• Total Tested: {total_credentials:,}
• Success Rate: {success_rate:.1f}%
"""
        
        message += f"\n<b>Completed:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        return await self.send_message(message, priority="normal")
    
    async def send_critical_alert(self, title: str, description: str, 
                                 details: Optional[Dict[str, Any]] = None) -> NotificationResult:
        """
        Envoie une alerte critique
        
        Args:
            title: Titre de l'alerte
            description: Description de l'alerte
            details: Détails additionnels
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        message = f"""
🚨 <b>CRITICAL ALERT</b> 🚨

<b>{html.escape(title)}</b>

{html.escape(description)}
"""
        
        if details:
            message += "\n<b>📋 Details:</b>\n"
            for key, value in details.items():
                message += f"• <b>{html.escape(str(key))}:</b> {html.escape(str(value))}\n"
        
        message += f"\n<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        return await self.send_message(message, priority="critical")
    
    async def send_perfect_hit(self, service: str, endpoint: str, credentials: Dict[str, str],
                              additional_info: Optional[Dict[str, Any]] = None) -> NotificationResult:
        """
        Envoie une notification de "perfect hit" (credential valide trouvé)
        
        Args:
            service: Type de service
            endpoint: Endpoint du service
            credentials: Credentials trouvés
            additional_info: Informations additionnelles
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        message = f"""
🎯 <b>PERFECT HIT!</b> 🎯

<b>Service:</b> {html.escape(service)}
<b>Endpoint:</b> <code>{html.escape(endpoint)}</code>

<b>🔑 Credentials:</b>
"""
        
        # Ajout des credentials (en masquant partiellement)
        for key, value in credentials.items():
            if key.lower() in ['password', 'token', 'api_key', 'secret']:
                # Masquer partiellement les données sensibles
                masked_value = value[:3] + "*" * (len(value) - 6) + value[-3:] if len(value) > 6 else "*" * len(value)
                message += f"• <b>{html.escape(key)}:</b> <code>{masked_value}</code>\n"
            else:
                message += f"• <b>{html.escape(key)}:</b> <code>{html.escape(str(value))}</code>\n"
        
        if additional_info:
            message += "\n<b>📋 Additional Info:</b>\n"
            for key, value in additional_info.items():
                message += f"• <b>{html.escape(str(key))}:</b> {html.escape(str(value))}\n"
        
        message += f"\n<b>Discovered:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        return await self.send_message(message, priority="high")
    
    async def send_statistics_summary(self, statistics: Dict[str, Any], 
                                    session_id: str) -> NotificationResult:
        """
        Envoie un résumé statistique
        
        Args:
            statistics: Statistiques à envoyer
            session_id: ID de session
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        message = f"""
📊 <b>WWYVQ Statistics Summary</b>

<b>Session:</b> <code>{session_id}</code>
<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

<b>🎯 Targets:</b>
• Processed: {statistics.get('targets_processed', 0):,}
• Clusters Found: {statistics.get('clusters_found', 0):,}
• Clusters Exploited: {statistics.get('clusters_exploited', 0):,}

<b>🔑 Credentials:</b>
• Total Found: {statistics.get('credentials_found', 0):,}
• Valid: {statistics.get('valid_credentials', 0):,}
• Success Rate: {statistics.get('credential_success_rate', 0):.1f}%

<b>⚡ Performance:</b>
• Operations Completed: {statistics.get('operations_completed', 0):,}
• Operations Failed: {statistics.get('operations_failed', 0):,}
• Total Runtime: {statistics.get('total_runtime', 'unknown')}
"""
        
        return await self.send_message(message, priority="normal")
    
    async def send_error_alert(self, error_type: str, error_message: str,
                              context: Optional[Dict[str, Any]] = None) -> NotificationResult:
        """
        Envoie une alerte d'erreur
        
        Args:
            error_type: Type d'erreur
            error_message: Message d'erreur
            context: Contexte de l'erreur
            
        Returns:
            NotificationResult: Résultat de l'envoi
        """
        message = f"""
❌ <b>ERROR ALERT</b>

<b>Type:</b> {html.escape(error_type)}
<b>Message:</b> <code>{html.escape(error_message)}</code>
"""
        
        if context:
            message += "\n<b>📋 Context:</b>\n"
            for key, value in context.items():
                message += f"• <b>{html.escape(str(key))}:</b> {html.escape(str(value))}\n"
        
        message += f"\n<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        return await self.send_message(message, priority="high")
    
    async def send_bulk_messages(self, messages: List[str], 
                                chat_id: Optional[str] = None) -> List[NotificationResult]:
        """
        Envoie plusieurs messages en parallèle
        
        Args:
            messages: Liste des messages à envoyer
            chat_id: ID du chat
            
        Returns:
            List[NotificationResult]: Résultats des envois
        """
        semaphore = asyncio.Semaphore(5)  # Limite de 5 messages simultanés
        
        async def send_with_semaphore(message):
            async with semaphore:
                return await self.send_message(message, chat_id)
        
        tasks = [send_with_semaphore(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des résultats
        valid_results = []
        for result in results:
            if isinstance(result, NotificationResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                self.logger.error(
                    f"Bulk message error: {result}",
                    module="notifier.telegram"
                )
        
        return valid_results
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de notification
        
        Returns:
            Dict: Statistiques
        """
        total_sent = len(self.sent_messages)
        successful_sent = sum(1 for msg in self.sent_messages if msg.success)
        failed_sent = total_sent - successful_sent
        
        # Statistiques par priorité
        priority_stats = {}
        for msg in self.sent_messages:
            priority = msg.message.metadata.get('priority', 'normal')
            if priority not in priority_stats:
                priority_stats[priority] = {'total': 0, 'success': 0}
            
            priority_stats[priority]['total'] += 1
            if msg.success:
                priority_stats[priority]['success'] += 1
        
        return {
            'total_messages': total_sent,
            'successful_messages': successful_sent,
            'failed_messages': failed_sent,
            'success_rate': (successful_sent / total_sent * 100) if total_sent > 0 else 0,
            'priority_stats': priority_stats,
            'enabled': self.enabled,
            'configured': bool(self.token and self.default_chat_id)
        }
    
    def is_configured(self) -> bool:
        """
        Vérifie si Telegram est correctement configuré
        
        Returns:
            bool: True si configuré
        """
        return bool(self.token and self.default_chat_id and self.enabled)
    
    async def test_connection(self) -> bool:
        """
        Test la connexion Telegram
        
        Returns:
            bool: True si la connexion fonctionne
        """
        if not self.is_configured():
            return False
        
        try:
            result = await self.send_message(
                "🧪 WWYVQ Framework v2 - Connection Test\n\nTelegram notifications are working correctly!",
                priority="low"
            )
            return result.success
            
        except Exception as e:
            self.logger.error(
                f"Telegram connection test failed: {e}",
                module="notifier.telegram"
            )
            return False