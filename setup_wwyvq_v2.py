#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Setup Script
Author: wKayaa
Date: 2025-01-15

Script de configuration et d'installation du framework WWYVQ v2.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """Affiche le banner de setup"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                          🚀 WWYVQ FRAMEWORK v2                                 ║
║                            Setup & Installation                                ║
║                                                                                  ║
║                           Author: wKayaa                                        ║
║                          Production Ready                                       ║
╚══════════════════════════════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """Vérifie la version de Python"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True


def install_dependencies():
    """Installe les dépendances"""
    print("\n📦 Installing dependencies...")
    
    dependencies = [
        "aiohttp>=3.8.0",
        "pyyaml>=6.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"   Installing {dep}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Crée les répertoires nécessaires"""
    print("\n📁 Creating directories...")
    
    directories = [
        "logs",
        "sessions", 
        "results",
        "configs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True


def setup_configuration():
    """Configure le framework"""
    print("\n⚙️ Setting up configuration...")
    
    # Vérification des fichiers de configuration
    default_config = Path("wwyvq_v2/configs/default.yaml")
    user_config = Path("configs/default.yaml")
    
    if default_config.exists() and not user_config.exists():
        shutil.copy(default_config, user_config)
        print("   ✅ Default configuration copied")
    
    # Configuration Telegram (optionnelle)
    print("\n📱 Telegram Configuration (Optional):")
    print("   To enable Telegram notifications:")
    print("   1. Create a bot with @BotFather")
    print("   2. Get your bot token and chat ID")
    print("   3. Edit configs/default.yaml:")
    print("      notifier:")
    print("        telegram:")
    print("          enabled: true")
    print("          token: 'YOUR_BOT_TOKEN'")
    print("          chat_id: 'YOUR_CHAT_ID'")
    
    return True


def test_installation():
    """Test l'installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test d'import des modules principaux
        sys.path.insert(0, str(Path.cwd()))
        
        from wwyvq_v2.core import WWYVQEngine
        print("   ✅ Core modules import OK")
        
        # Test de configuration
        engine = WWYVQEngine("wwyvq_v2/configs/default.yaml")
        print("   ✅ Engine initialization OK")
        
        # Test de validation de configuration
        config = engine.config_manager.get_config()
        if engine.config_manager.validate_config():
            print("   ✅ Configuration validation OK")
        else:
            print("   ⚠️ Configuration validation warning")
        
        print("✅ Installation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def show_usage_examples():
    """Affiche des exemples d'utilisation"""
    print("\n📖 Usage Examples:")
    print("""
🔍 Basic Scan:
   python wwyvq.py scan --targets targets.txt

🚀 Advanced Scan:
   python wwyvq.py scan --targets "192.168.1.0/24" --mode aggressive --concurrent 200

⚙️ Configuration:
   python wwyvq.py config --show
   python wwyvq.py config --profile production

🛡️ Safe Mode (Recommended for production):
   python wwyvq.py scan --targets targets.txt --safe-mode

🧪 Test Framework:
   python test_architecture.py
   python demo_wwyvq_v2.py

📚 Documentation:
   See wwyvq_v2/docs/README.md for complete documentation
    """)


def main():
    """Fonction principale de setup"""
    print_banner()
    
    print("🔧 Starting WWYVQ Framework v2 Setup...")
    
    # Vérifications et installations
    steps = [
        ("Python Version Check", check_python_version),
        ("Dependencies Installation", install_dependencies),
        ("Directory Creation", create_directories),
        ("Configuration Setup", setup_configuration),
        ("Installation Test", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"📋 {step_name}")
        print('='*60)
        
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please check the errors above and try again.")
            return False
    
    # Succès
    print("\n" + "="*60)
    print("🎉 WWYVQ Framework v2 Setup Complete!")
    print("="*60)
    
    print("""
✅ Installation Summary:
   • Python version verified
   • Dependencies installed
   • Directories created
   • Configuration ready
   • Framework tested

🚀 Next Steps:
   1. Review configuration in configs/default.yaml
   2. Optionally configure Telegram notifications
   3. Create a targets file for scanning
   4. Run your first scan!

Quick Start:
   python wwyvq.py --help
   python wwyvq.py scan --targets "127.0.0.1" --mode standard
    """)
    
    show_usage_examples()
    
    print("\n🎯 Framework is ready for use!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)