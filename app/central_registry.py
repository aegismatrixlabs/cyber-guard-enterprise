import sys
import os

# Ensure app path is in system path for safe module loading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tenant_isolation import TenantIsolationManager

class CentralRegistry:
    """
    CyberGuard Enterprise Append-Only Delta Registry.
    Bütün modülleri ana sisteme zarar vermeden güvenle kaydeder ve yönetir.
    """
    def __init__(self):
        self.modules = {}
        self._register_core_modules()

    def _register_core_modules(self):
        # Append-Only Delta: Modül güvenle kayıt defterine eklenir
        self.modules["tenant_isolation"] = TenantIsolationManager()

    def get_module(self, module_name: str):
        return self.modules.get(module_name)

if __name__ == "__main__":
    registry = CentralRegistry()
    tenant_mgr = registry.get_module("tenant_isolation")
    if tenant_mgr:
        print("[BAŞARILI] tenant_isolation modülü CentralRegistry üzerinden güvenle çağrıldı.")
