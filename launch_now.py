#!/usr/bin/env python3
"""
🔥 LANCEMENT IMMÉDIAT - Version Simplifiée
Pour avoir des résultats rapidement
"""

import asyncio
import os
from pathlib import Path

# Importer le launcher existant
from intensive_hunt_launcher import IntensiveHuntLauncher

async def quick_launch():
    """Lancement rapide avec configuration optimisée"""
    print("🚀 Lancement immédiat du hunt...")
    
    # Créer targets minimal si manquant
    if not Path("targets_massive_optimized.txt").exists():
        with open("targets_massive_optimized.txt", "w") as f:
            f.write("""# Targets pour test rapide
# Remplacez par vos vraies cibles
192.168.1.0/24
10.0.0.0/24
127.0.0.1
localhost
""")
        print("✅ Fichier targets créé")
    
    # Initialiser et lancer
    launcher = IntensiveHuntLauncher()
    
    # Configuration pour résultats rapides
    launcher.config.update({
        "threads": 100,  # Réduit pour éviter overload
        "timeout": 5,    # Plus rapide
        "aggressive_mode": True,
        "live_notifications": True
    })
    
    # Lancer le hunt
    await launcher.run_full_hunt()

if __name__ == "__main__":
    asyncio.run(quick_launch())