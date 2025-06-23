#!/bin/bash
LOG_FILE="bounty_6h_20250623_210345.log"

tail -f $LOG_FILE | while read line; do
    if echo "$line" | grep -q "AWS\|AKIA\|SECRET"; then
        echo "🚨 BOUNTY HIT DÉTECTÉ: $(date)"
        echo "$line"
        echo "=================="
        
        # Sauvegarde hit
        echo "$(date): $line" >> bounty_hits_$(date +%Y%m%d).txt
    fi
done
