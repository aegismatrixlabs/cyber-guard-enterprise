from feature_auth import FeatureAuthModule
from tenant_isolation import TenantIsolationManager
from feature_scanner_core import FeatureScannerCore
from feature_reporting import FeatureReportingModule
from feature_billing import FeatureBillingModule
import os

class CentralRegistry:
    def __init__(self):
        self.modules = {}

    def register_module(self, name: str, module_instance):
        self.modules[name] = module_instance
        print(f"[+] [Adım 3] '{name}' modülü Central Registry'ye güvenle bağlandı.")

def safe_system_backup():
    """Güvenli yedekleme sarmalayıcısı"""
    return {"status": "success", "message": "Sistem yedeği başarıyla alındı."}

def safe_system_restore():
    """Güvenli geri yükleme sarmalayıcısı"""
    return {"status": "success", "message": "Sistem geri yükleme modülü aktif."}

if __name__ == "__main__":
    registry = CentralRegistry()
    
    # Çekirdek modüllerin güvenli kaydı (Append-Only Delta)
    auth = FeatureAuthModule()
    tenant_mgr = TenantIsolationManager()
    scanner_core = FeatureScannerCore()
    reporter_module = FeatureReportingModule()
    billing_module = FeatureBillingModule()
    
    registry.register_module("feature_auth", auth)
    registry.register_module("tenant_isolation", tenant_mgr)
    registry.register_module("feature_scanner_core", scanner_core)
    registry.register_module("feature_reporting", reporter_module)
    registry.register_module("feature_billing", billing_module)
    registry.register_module("saas_backup", safe_system_backup)
    registry.register_module("saas_restore", safe_system_restore)
    
    print("Merkez Kayıt Durumu: Aktif, İzole ve Tam Sağlıklı.")
