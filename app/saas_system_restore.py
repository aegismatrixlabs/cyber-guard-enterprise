import os
import glob
import json
import shutil
import time
import logging
from typing import Dict, Any

# Loglama Yapılandırması (Kritik kurtarma olayları hassas veri sızdırmadan kayıt altına alınır)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("CyberGuardSystemRestore")

# Mükerrer İstek Koruması (Idempotency) için Bellek İçi Önbellek
RESTORE_REQUEST_CACHE: Dict[str, float] = {}

class SystemRestoreError(Exception):
    """Güvenli hata yönetimi için özel sistem kurtarma istisna sınıfı."""
    pass

class SaaSSystemRestoreModule:
    def __init__(self, base_dir: str = "app"):
        self.base_dir = base_dir
        self.backup_root = os.path.join(base_dir, "backups")

    # --- 1. HALKA: Girdi Doğrulama ve Kimlik/Parametre Kontrolü ---
    def validate_input_parameters(self, target_tenant_id: str, auth_token: str, idempotency_key: str) -> None:
        if not target_tenant_id or not isinstance(target_tenant_id, str):
            raise SystemRestoreError("Geçersiz veya eksik Tenant ID formatı.")
        if not auth_token or not auth_token.startswith("Bearer-CG-"):
            raise SystemRestoreError("Yetkilendirme Hatası: Geçersiz veya eksik Auth/JWT token.")
        if not idempotency_key or not isinstance(idempotency_key, str):
            raise SystemRestoreError("Geçersiz veya eksik idempotency anahtarı.")

    # --- 2. HALKA: Çoklu-Kiracı İzolasyonu ve Tenant Doğrulaması ---
    def enforce_tenant_isolation(self, target_tenant_id: str, snapshot_dir: str) -> Dict[str, Any]:
        meta_file_path = os.path.join(snapshot_dir, "metadata.json")
        if not os.path.exists(meta_file_path):
            raise SystemRestoreError("Kritik Hata: Hedef anlık görüntüye ait meta veri (metadata.json) bulunamadı.")

        try:
            with open(meta_file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            raise SystemRestoreError("Meta veri dosyası okunamadı veya bozulmuş.")

        snapshot_tenant = metadata.get("tenant_id")
        
        # Çoklu-kiracı izolasyon çiti (Cross-tenant veri sızıntısı engellenir)
        if snapshot_tenant != target_tenant_id:
            logger.critical(f"Kritik İzolasyon İhlali: Hedef tenant ({target_tenant_id}), yedek tenant ({snapshot_tenant}) ile uyuşmuyor!")
            raise SystemRestoreError("Yetkisiz geri yükleme denemesi: Tenant ID uyuşmazlığı engellendi.")

        return metadata

    # --- 4. HALKA: Mükerrer İstek Koruması (Idempotency) ve Kalıcılık ---
    def enforce_idempotency(self, tenant_id: str, idempotency_key: str) -> None:
        current_time = time.time()
        cache_key = f"{tenant_id}:{idempotency_key}"
        
        if cache_key in RESTORE_REQUEST_CACHE:
            if current_time - RESTORE_REQUEST_CACHE[cache_key] < 30: # 30 saniye içinde mükerrer geri yükleme koruması
                raise SystemRestoreError("Mükerrer geri yükleme isteği engellendi (Idempotency koruması aktif).")
                
        RESTORE_REQUEST_CACHE[cache_key] = current_time

    # --- 3. HALKA: Çekirdek İş Mantığı (Asıl Rollback / Geri Yükleme İcrası) ---
    def execute_core_rollback(self, snapshot_dir: str) -> list:
        restored_files = []
        for file_name in os.listdir(snapshot_dir):
            if file_name == "metadata.json":
                continue
            src_file = os.path.join(snapshot_dir, file_name)
            if os.path.isfile(src_file):
                shutil.copy(src_file, self.base_dir)
                restored_files.append(file_name)
                logger.info(f"Güvenli geri yüklenen dosya: {file_name}")
        return restored_files

    # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except Blokları ve Güvenli Yanıt ---
    def restore_latest_snapshot(self, target_tenant_id: str, auth_token: str, idempotency_key: str) -> Dict[str, Any]:
        try:
            # 1. Halka: Girdi Doğrulama ve Auth Kontrolü
            self.validate_input_parameters(target_tenant_id, auth_token, idempotency_key)

            # 4. Halka: Mükerrer İstek Koruması
            self.enforce_idempotency(target_tenant_id, idempotency_key)

            if not os.path.exists(self.backup_root):
                raise SystemRestoreError(f"Yedekleme dizini mevcut değil: {self.backup_root}")

            # En son zaman damgasına sahip snapshot'ı otomatik bulma
            snapshot_pattern = os.path.join(self.backup_root, "snapshot_*")
            all_snapshots = glob.glob(snapshot_pattern)

            if not all_snapshots:
                raise SystemRestoreError("Geri yüklenebilecek hiçbir anlık görüntü (snapshot) bulunamadı.")

            latest_snapshot = max(all_snapshots, key=os.path.getmtime)
            logger.info(f"En güncel anlık görüntü tespit edildi: {latest_snapshot}")

            # 2. Halka: Çoklu-Kiracı İzolasyon Denetimi
            metadata = self.enforce_tenant_isolation(target_tenant_id, latest_snapshot)

            # 3. Halka: Çekirdek İş Mantığı (Rollback)
            restored_files = self.execute_core_rollback(latest_snapshot)

            logger.info(f"Sistem başarıyla geri yüklendi - Tenant: {target_tenant_id}, Snapshot: {os.path.basename(latest_snapshot)}")
            return {
                "status": "success",
                "message": f"Sistem '{os.path.basename(latest_snapshot)}' sürümüne başarıyla geri döndürüldü.",
                "restored_files": restored_files,
                "metadata": metadata
            }

        except SystemRestoreError as sre:
            # Kontrollü ve güvenli hata yönetimi (Hassas iç veri sızdırılmaz)
            logger.warning(f"Geri yükleme uyarısı: {str(sre)}")
            return {
                "status": "error",
                "message": str(sre)
            }
        except Exception as e:
            # Fail-safe mekanizması: Sistem çökmesini engeller
            logger.critical(f"Kritik sistem kurtarma hatası: {str(e)}")
            return {
                "status": "error",
                "message": "Sistem geçici olarak geri yükleme işlemine yanıt veremiyor."
            }

if __name__ == "__main__":
    restorer = SaaSSystemRestoreModule()
    print("--- CYBERGUARD ENTERPRISE: SİSTEM KURTARMA MODÜLÜ TESTİ ---")
    response = restorer.restore_latest_snapshot(
        target_tenant_id="tenant_alpha_01",
        auth_token="Bearer-CG-secrettoken123",
        idempotency_key="restore_key_abc123"
    )
    print("Kurtarma Modülü Yanıtı:", response)
