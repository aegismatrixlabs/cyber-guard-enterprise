import sqlite3
import os

def restore_system_snapshot(backup_path="cyber_guard_backup.db", target_path="cyber_guard.db"):
    """Sistem yedeğini güvenle geri yükleme fonksiyonu"""
    try:
        if not os.path.exists(backup_path):
            return {"status": "error", "code": 404, "message": "Geri yüklenecek yedek dosyası bulunamadı."}
        
        # Dosya bazlı güvenli kopyalama/geri yükleme
        with open(backup_path, 'rb') as src, open(target_path, 'wb') as dst:
            dst.write(src.read())
            
        return {"status": "success", "code": 200, "message": "Sistem başarıyla yedekten geri yüklendi."}
    except Exception as e:
        return {"status": "error", "code": 500, "message": "Sistem geri yükleme sırasında kritik hata önlendi."}

if __name__ == "__main__":
    print(restore_system_snapshot())
