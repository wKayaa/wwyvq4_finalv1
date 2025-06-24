#!/bin/bash
# Setup rapide pour lancement immédiat

# 1. Vérifier les dépendances essentielles
pip install aiohttp asyncio requests pyyaml

# 2. Créer le fichier de targets si il n'existe pas
if [ ! -f "targets_massive_optimized.txt" ]; then
    echo "# Targets pour hunt"
    echo "192.168.1.0/24" > targets_massive_optimized.txt
    echo "10.0.0.0/24" >> targets_massive_optimized.txt
    echo "172.16.0.0/24" >> targets_massive_optimized.txt
    echo "✅ Fichier targets créé"
fi

# 3. Variables d'environnement Telegram (optionnel)
export TELEGRAM_TOKEN="7806423696:AAEV7VM9JCNiceHhIo1Lir2nDM8AJkAUZuM"
export TELEGRAM_CHAT="-4732561310"

echo "🚀 Setup terminé - Prêt à lancer!"