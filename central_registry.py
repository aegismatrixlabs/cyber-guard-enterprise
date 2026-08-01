from feature_auth import FeatureAuthModule
from saas_backup_manager import create_system_snapshot
from saas_system_restore import restore_system_snapshot
from tenant_isolation import TenantIsolationManager

class CentralRegistry:
    def __init__(self):
        self.modules = {}

    def register_module(self, name: str, module_instance):
        self.modules[name] = module_instance
        print(f"[+] [Adım 3] '{name}' modülü Central Registry'ye güvenle bağlandı.")

if __name__ == "__main__":
    registry = CentralRegistry()
    auth = FeatureAuthModule()
    registry.register_module("feature_auth", auth)
    registry.register_module("saas_backup", create_system_snapshot)
    registry.register_module("saas_restore", restore_system_snapshot)
    registry.register_module("tenant_isolation", tenant_mgr)
    print("Merkez Kayıt Durumu: Aktif ve Sağlıklı.")
