#!/usr/bin/env python3
"""
🧹 Nettoyage automatique du repository
Supprime les doublons et organise les fichiers
"""

import os
import shutil
import glob
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
        "wwyvq4_ultimate_fix.py",    # Remplacé
        "demo_improvements.py",      # Fichier de démonstration
        "enhanced_monitoring.py",    # Remplacé par enhanced_credential_validator.py
        "enhanced_security_monitor.py", # Remplacé par enhanced_credential_validator.py
        "enhanced_telegram_alerts.py", # Remplacé par professional_telegram_notifier.py
        "f8s_example_usage.py",      # Fichier f8s obsolète
        "f8s_exploit_pod.py",        # Fichier f8s obsolète
        "final_demo.py",             # Fichier de démonstration
        "intensive_hunt_launcher.py", # Fichier intensif obsolète
        "optimized_f8s_mega_launch.py", # Fichier optimisé obsolète
        "ultimate_6h_hunt.py",       # Fichier ultimate obsolète
        "mega_cidr_uhq.py",          # Fichier mega obsolète
        "speed_hunt.py",             # Fichier speed obsolète
        "examples_usage.py",         # Fichier d'exemple
        "dashboard.py",              # Remplacé par interface web
        "aio_k8s_exploit.py",        # Fichier aio obsolète
        "aio_k8s_exploit_integration.py", # Fichier aio obsolète
        "security_monitor_integration.py", # Intégré dans le nouveau système
        "verify_implementation.py",   # Fichier de vérification
        "telegram_test.py"           # Fichier de test
    ]
    
    # Fichiers de test à supprimer
    test_files = glob.glob("test_*.py")
    files_to_remove.extend(test_files)
    
    # Fichiers à GARDER (essentiels)
    essential_files = [
        "wwyvq_master_final.py",     # SCRIPT PRINCIPAL
        "wwyvq_enhanced_framework.py", # NOUVEAU SCRIPT PRINCIPAL
        "kubernetes_advanced.py",    # Framework principal
        "k8s_exploit_master.py",     # Exploitation avancée
        "mail_services_hunter.py",   # Mail hunter
        "telegram_perfect_hits.py",  # Notifications
        "enhanced_credential_validator.py", # Validation avancée
        "professional_telegram_notifier.py", # Notifications pros
        "organized_results_manager.py",    # Gestion résultats
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
            try:
                shutil.move(file, f"archive/{file}")
                print(f"🗑️ Archivé: {file}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de l'archivage de {file}: {e}")
    
    # Déplacer modules spécialisés vers modules/
    specialized_modules = [
        "k8s_config_production.py",
        "kubernetes_privilege_escalation.py",
        "telegram_mail_enhanced.py",
        "wwyvq5_mail_orchestrator.py",
        "massive_cidr_generator.py",
        "k8s_production_harvester.py"
    ]
    
    moved_count = 0
    for module in specialized_modules:
        if os.path.exists(module):
            try:
                shutil.move(module, f"modules/{module}")
                print(f"🔧 Module déplacé: {module}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Erreur lors du déplacement de {module}: {e}")
    
    # Déplacer configurations vers configs/
    config_files = [
        "framework_config.yaml",
        "kubernetes_config.py"
    ]
    
    for config in config_files:
        if os.path.exists(config):
            try:
                shutil.move(config, f"configs/{config}")
                print(f"⚙️ Config déplacée: {config}")
            except Exception as e:
                print(f"❌ Erreur lors du déplacement de {config}: {e}")
    
    # Nettoyer les anciens dossiers de résultats
    result_dirs_to_clean = []
    for item in os.listdir('.'):
        if (item.startswith('results_MASTER_') or 
            item.startswith('hunt_results_') or 
            item.startswith('exploitation_results_')):
            result_dirs_to_clean.append(item)
    
    cleaned_results = 0
    for result_dir in result_dirs_to_clean:
        if os.path.exists(result_dir):
            try:
                shutil.move(result_dir, f"archive/{result_dir}")
                print(f"📁 Ancien résultat archivé: {result_dir}")
                cleaned_results += 1
            except Exception as e:
                print(f"❌ Erreur lors de l'archivage de {result_dir}: {e}")
    
    # Créer README pour la nouvelle structure
    readme_content = f"""# 🚀 WWYVQ Enhanced Framework - Structure Organisée

## 📁 STRUCTURE DU PROJET:

### 🎯 FICHIERS PRINCIPAUX:
- `wwyvq_enhanced_framework.py` - **NOUVEAU SCRIPT PRINCIPAL AVEC AMÉLIORATIONS**
- `wwyvq_master_final.py` - Script principal original
- `launch_now.py` - Lancement rapide
- `app.py` - Interface web (port 5000)

### 🔧 MODULES CORE:
- `enhanced_credential_validator.py` - **VALIDATION AVANCÉE DES CREDENTIALS**
- `professional_telegram_notifier.py` - **NOTIFICATIONS PROFESSIONNELLES**
- `organized_results_manager.py` - **GESTION ORGANISÉE DES RÉSULTATS**
- `kubernetes_advanced.py` - Framework principal
- `k8s_exploit_master.py` - Exploitation avancée  
- `mail_services_hunter.py` - Chasse aux credentials mail
- `telegram_perfect_hits.py` - Notifications Telegram

### 📂 DOSSIERS:
- `archive/` - Fichiers archivés/obsolètes ({removed_count} fichiers)
- `modules/` - Modules spécialisés ({moved_count} fichiers)
- `configs/` - Fichiers de configuration
- `results/` - **NOUVEAUX RÉSULTATS ORGANISÉS**
  - Format: results/session_YYYYMMDD_HHMMSS/
  - Fichiers par service: aws.txt, sendgrid.txt, mailgun.txt, etc.
  - Exports JSON et CSV automatiques
  - Fichier host.txt généré automatiquement
- `docs/` - Documentation

### 🚀 NOUVELLES FONCTIONNALITÉS:

#### ✅ Validation Avancée des Credentials:
- Validation en temps réel via API
- Détection des faux positifs
- Scoring de confiance
- Support AWS, SendGrid, Mailgun, Mailjet, Postmark

#### ✅ Notifications Telegram Professionnelles:
- Format professionnel avec détails complets
- Statistiques en temps réel
- Alertes d'erreur contextuelles
- Résumés de session détaillés

#### ✅ Gestion Organisée des Résultats:
- Structure par service (aws.txt, sendgrid.txt, etc.)
- Exports JSON et CSV automatiques
- Fichier host.txt généré
- Résumés de session

### 🎯 UTILISATION:

```bash
# Créer un fichier de configuration
python3 wwyvq_enhanced_framework.py --create-config

# Éditer wwyvq_config.json avec vos paramètres Telegram

# Lancer un scan
python3 wwyvq_enhanced_framework.py --targets targets.txt --config wwyvq_config.json --mode standard

# Modes disponibles: standard, intensive, stealth
```

### 📊 AMÉLIORATIONS RÉALISÉES:

1. ✅ **Validation des credentials** - Évite les faux positifs
2. ✅ **Notifications professionnelles** - Format comme demandé
3. ✅ **Résultats organisés** - Structure aws.txt, sendgrid.txt, etc.
4. ✅ **Nettoyage du repository** - Suppression des doublons
5. ✅ **Architecture modulaire** - Séparation des responsabilités

### 🔧 CONFIGURATION:

Le fichier `wwyvq_config.json` permet de configurer:
- Paramètres Telegram (token, chat_id)
- Paramètres de scan (concurrence, timeout)
- Paramètres de validation (seuils, services)
- Paramètres de résultats (formats d'export)

### 👨‍💻 OPÉRATEUR: wKayaa
### 📅 VERSION: 5.0 Enhanced
### 🚀 FRAMEWORK: WWYVQ Enhanced

#WWYVQ #EnhancedFramework #ProfessionalCredentialHunting #OrganizedResults #wKayaa
"""
    
    try:
        with open("README_ENHANCED.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
        print("📖 README créé: README_ENHANCED.md")
    except Exception as e:
        print(f"❌ Erreur lors de la création du README: {e}")
    
    print(f"""
🎉 NETTOYAGE TERMINÉ !
{'='*50}
✅ Fichiers archivés: {removed_count}
✅ Modules déplacés: {moved_count}
✅ Anciens résultats archivés: {cleaned_results}
✅ Structure organisée créée
✅ README Enhanced créé

🚀 PRÊT POUR LE NOUVEAU FRAMEWORK !
Utilisez: python3 wwyvq_enhanced_framework.py --help
""")

if __name__ == "__main__":
    cleanup_repository()
    
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