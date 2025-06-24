#!/usr/bin/env python3
"""
🧹 Nettoyage automatique du repository
Supprime les doublons et organise les fichiers
"""

import os
import shutil
from pathlib import Path

def cleanup_repository():
    """Nettoie et organise le repository"""
    
    print("🧹 NETTOYAGE DU REPOSITORY WWYVQ")
    
    # Fichiers à SUPPRIMER (doublons/obsolètes)
    files_to_remove = [
        "main.py",                    # Remplacé par wwyvq_master_final.py
        "main_updated.py",           # Doublon
        "main_enhanced.py",          # Doublon
        "launcher.py",               # Remplacé par launch_now.py
        "ultimate_launcher.py",      # Doublon
        "kubernetes_advanced_old.py", # Version obsolète
        "wwyv4q_final.py",           # Version intermédiaire
        "wwyvq4_ultimate.py",        # Version intermédiaire
        "wwyvq4_ultimate_fix.py"     # Remplacé
    ]
    
    # Fichiers à GARDER (essentiels)
    essential_files = [
        "wwyvq_master_final.py",     # SCRIPT PRINCIPAL
        "kubernetes_advanced.py",    # Framework principal
        "k8s_exploit_master.py",     # Exploitation avancée
        "mail_services_hunter.py",   # Mail hunter
        "telegram_perfect_hits.py",  # Notifications
        "app.py",                    # Interface web
        "launch_now.py",             # Launcher rapide
        "targets.txt",               # Cibles
        "targets_massive_optimized.txt", # Cibles optimisées
        "setup_ultimate.sh",         # Setup
        "requirements_ultimate.txt"  # Dépendances
    ]
    
    # Créer dossiers d'organisation
    folders = ["archive/", "modules/", "configs/", "results/", "docs/"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📁 Dossier créé: {folder}")
    
    # Supprimer les doublons
    removed_count = 0
    for file in files_to_remove:
        if os.path.exists(file):
            shutil.move(file, f"archive/{file}")
            print(f"🗑️ Archivé: {file}")
            removed_count += 1
    
    # Déplacer modules spécialisés
    specialized_modules = [
        "k8s_config_production.py",
        "kubernetes_privilege_escalation.py",
        "telegram_mail_enhanced.py",
        "wwyvq5_mail_orchestrator.py",
        "massive_cidr_generator.py",
        "speed_hunt.py"
    ]
    
    moved_count = 0
    for module in specialized_modules:
        if os.path.exists(module):
            shutil.move(module, f"modules/{module}")
            print(f"🔧 Module déplacé: {module}")
            moved_count += 1
    
    # Déplacer configurations
    config_files = [
        "framework_config.yaml",
        "kubernetes_config.py"
    ]
    
    for config in config_files:
        if os.path.exists(config):
            shutil.move(config, f"configs/{config}")
            print(f"⚙️ Config déplacée: {config}")
    
    # Créer README pour la nouvelle structure
    readme_content = f"""# 🚀 WWYVQ Framework - Structure Organisée

## 📁 STRUCTURE DU PROJET:

### 🎯 FICHIERS PRINCIPAUX:
- `wwyvq_master_final.py` - **SCRIPT PRINCIPAL UNIFIÉ**
- `launch_now.py` - Lancement rapide
- `app.py` - Interface web (port 5000)

### 🔧 MODULES CORE:
- `kubernetes_advanced.py` - Framework principal
- `k8s_exploit_master.py` - Exploitation avancée  
- `mail_services_hunter.py` - Chasse aux credentials mail
- `telegram_perfect_hits.py` - Notifications Telegram

### 📂 DOSSIERS:
- `modules/` - Modules spécialisés
- `configs/` - Fichiers de configuration
- `results/` - Résultats des campagnes
- `archive/` - Anciens fichiers (doublons supprimés)

## 🚀 UTILISATION:

```bash
# Mode agressif avec Telegram
python wwyvq_master_final.py --mode aggressive --file targets.txt --telegram-token YOUR_TOKEN

# Mode mail avec interface web
python wwyvq_master_final.py --mode mail --target 192.168.1.0/24 --web

# Tous les modules en parallèle
python wwyvq_master_final.py --mode all --file targets.txt --threads 1000 --web

# Mode furtif
python wwyvq_master_final.py --mode stealth --target example.com --threads 5

# Lancement rapide
python launch_now.py
"""