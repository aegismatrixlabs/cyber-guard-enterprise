import os
import sys

# app dizinini python yoluna ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from saas_backup_manager import SaaSBackupManager
    manager = SaaSBackupManager()
    sonuc = manager.create_secure_snapshot("tenant_alpha_01", "Bearer-CG-secrettoken123", "manual_backup_key")
    print("[BAŞARILI] Yedekleme Sonucu:", sonuc)
except Exception as e:
    print("[HATA] Yedekleme sırasında hata oluştu:", str(e))
