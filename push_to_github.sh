#!/bin/bash
# CyberGuard Enterprise Otomatik GitHub Push Sistemi

echo "🚀 GitHub'a gönderim başlatılıyor..."

# Tüm değişiklikleri ekle
git add .

# Değişiklik varsa commit oluştur, yoksa işlemi atla
if git diff --cached --quiet; then
    echo "✅ Yeni bir değişiklik yok, atlanıyor."
else
    # Modül ismini dinamik almak için 1. argümanı kullan, yoksa varsayılan yaz
    COMMIT_MSG="Sistem Guncellemesi: ${1:-'Yeni Modul Eklendi'} - $(date +'%Y-%m-%d %H:%M:%S')"
    
    git commit -m "$COMMIT_MSG"
    
    # Ana dala push et
    git push origin main
    echo "✅ Değişiklikler GitHub'a başarıyla gönderildi!"
fi
