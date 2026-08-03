#!/bin/bash
# CyberGuard Enterprise Otomatik Yedekleme Sistemi

# Yedekleme klasörünü oluştur (yoksa)
mkdir -p backups

# Zaman damgası oluştur (Örn: 20260804_025500)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/snapshot_$TIMESTAMP"

echo "📦 Yedekleme başlatılıyor: $BACKUP_DIR"
mkdir -p $BACKUP_DIR

# 1. Veritabanını (cyber_guard.db) yedekle
if [ -f "cyber_guard.db" ]; then
    cp cyber_guard.db $BACKUP_DIR/
    echo "✅ Veritabanı yedeklendi."
else
    echo "⚠️ Veritabanı dosyası bulunamadı, atlanıyor."
fi

# 2. Tüm Python ve Kritik kodları yedekle
cp main.py database.py models.py schemas.py $BACKUP_DIR/ 2>/dev/null
cp -r routers/ $BACKUP_DIR/ 2>/dev/null
cp -r templates/ $BACKUP_DIR/ 2>/dev/null
cp -r static/ $BACKUP_DIR/ 2>/dev/null
echo "✅ Kod dosyaları yedeklendi."

# 3. 7 günden eski yedeklemeleri otomatik temizle (Disk dolmasın)
find backups/ -type d -ctime +7 -exec rm -rf {} \;
echo "🧹 7 günden eski yedeklemeler temizlendi."

echo "✅ Yedekleme tamamlandı: $BACKUP_DIR"
