#!/bin/bash
# ğŸ›¡ï¸ CYBERGUARD ENTERPRISE - COMPACT SYSTEM STATE EXPORTER
# Compliance: venv and external package filtering enabled

OUTPUT_FILE="CYBERGUARD_SYSTEM_STATE.md"

echo "# ğŸ›¡ï¸ CYBERGUARD ENTERPRISE - LIGHTWEIGHT STATE DUMP" > $OUTPUT_FILE
echo "Generated on: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "## 1. Proje Dizin YapÄ±sÄ±" >> $OUTPUT_FILE
echo '```' >> $OUTPUT_FILE
find . -maxdepth 3 -not -path '*/.*' -not -path './venv*' -not -path '*/__pycache__*' >> $OUTPUT_FILE
echo '```' >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "## 2. Aktif Proje ModÃ¼lleri (*.py)" >> $OUTPUT_FILE
echo '```' >> $OUTPUT_FILE
find . -maxdepth 3 -type f -name "*.py" -not -path './venv*' -not -path '*/__pycache__*' >> $OUTPUT_FILE
echo '```' >> $OUTPUT_FILE

echo "[+] Hafif rapor oluÅŸturuldu: $OUTPUT_FILE"
