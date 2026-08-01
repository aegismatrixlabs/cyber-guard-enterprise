from feature_auth import FeatureAuthModule
from saas_backup_manager import create_system_snapshot
from saas_system_restore import restore_system_snapshot
from tenant_isolation import TenantIsolationManager
from feature_scanner_core import FeatureScannerCore
from feature_reporting import FeatureReportingModule
from feature_billing import FeatureBillingModule
from api_gateway_waf import ApiGatewayWafModule

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
    registry.register_module("feature_scanner_core", scanner_core)
    registry.register_module("feature_reporting", reporter_module)
    registry.register_module("feature_billing", billing_module)
    registry.register_module("api_gateway_waf", waf_module)
    print("Merkez Kayıt Durumu: Aktif ve Sağlıklı.")
