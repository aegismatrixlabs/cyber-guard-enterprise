import os
import glob
import json
import shutil
import logging

# Loglama Yapılandırması (Kritik kurtarma olayları kayıt altına alınır)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("CyberGuardRestore")

class SystemRestorer:
    def __init__(self, base_dir: str = "app"):
        self.base_dir = base_dir
        self.backup_root = os.path.join(base_dir, "backups")

    def auto_rollback_latest(self, target_tenant_id: str) -> None:
        """backups/ dizinindeki en son zaman damgalı snapshot'ı otomatik bulur ve geri yükler."""
        try:
            if not os.path.exists(self.backup_root):
                raise FileNotFoundError(f"Yedekleme dizini bulunamadı: {self.backup_root}")

            # En son zaman damgasına sahip snapshot klasörünü bulma (Zaman damgası sıralamasına göre)
            snapshot_pattern = os.path.join(self.backup_root, "snapshot_*")
            all_snapshots = glob.glob(snapshot_pattern)

            if not all_snapshots:
                logger.error("Geri yüklenebilecek hiçbir anlık görüntü (snapshot) bulunamadı!")
                return

            # Alfabetik/Zamansal sıralamada en son (en güncel) yedeği seçme
            latest_snapshot = max(all_snapshots, key=os.path.getmtime)
            logger.info(f"En güncel anlık görüntü tespit edildi: {latest_snapshot}")

            # Metadata doğrulama ve Çoklu-Kiracı (Tenant) Güvenliği
            meta_file_path = os.path.join(latest_snapshot, "metadata.json")
            if os.path.exists(meta_file_path):
                with open(meta_file_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    snapshot_tenant = metadata.get("tenant_id")
                    
                    if snapshot_tenant != target_tenant_id:
                        logger.critical(f"İzolasyon İhlali: Hedef tenant ({target_tenant_id}), yedek tenant ({snapshot_tenant}) ile uyuşmuyor!")
                        print("[-] [HATA] Güvenlik uyarısı: Tenant ID uyuşmazlığı nedeniyle geri yükleme iptal edildi.")
                        return
            else:
                logger.warning("Metadata dosyası bulunamadı, ancak sistem kurtarmaya zorlanıyor.")

            # Dosyaları güvenle ana dizine geri yükleme (Rollback)
            for file_name in os.listdir(latest_snapshot):
                if file_name == "metadata.json":
                    continue
                src_file = os.path.join(latest_snapshot, file_name)
                if os.path.isfile(src_file):
                    shutil.copy(src_file, self.base_dir)
                    logger.info(f"Geri yüklenen dosya: {file_name}")

            print(f"[+] [BAŞARILI] Sistem en son kararlı anlık görüntüye ({os.path.basename(latest_snapshot)}) başarıyla döndürüldü.")

        except Exception as e:
            logger.critical(f"Kritik Rollback Hatası: {str(e)}")
            print(f"[-] [KRİTİK HATA] Geri yükleme sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    restorer = SystemRestorer()
    # Güvenli kurtarma tetiklemesi (Tenant ID eşleşmesi zorunludur)
    restorer.auto_rollback_latest(target_tenant_id="tenant_alpha_01")
