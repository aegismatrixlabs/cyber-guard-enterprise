import sys
import os

# Doğru modül arama yolunu (app dizinini) kök dizin olarak sabitleme
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(current_dir)

from saas_backup_manager import SaaSBackupManager
from saas_system_restore import SaaSSystemRestoreModule

class SystemRouterDelta:
    def __init__(self):
        self.registry = {}
        self.backup_manager = SaaSBackupManager()
        self.system_restorer = SaaSSystemRestoreModule()

    def register_delta_modules(self) -> None:
        """Append-Only Delta kuralına göre yedekleme ve kurtarma modüllerini merkezi kayda ekler."""
        self.registry["saas_backup_manager"] = {
            "instance": self.backup_manager,
            "status": "active_delta",
            "security_chain": "5-Chain Enforced"
        }
        self.registry["saas_system_restore"] = {
            "instance": self.system_restorer,
            "status": "active_delta",
            "security_chain": "5-Chain Enforced"
        }
        print("[+] [DELTA ENTEGRASYONU] saas_backup_manager ve saas_system_restore merkezi sisteme güvenle mühürlendi.")

if __name__ == "__main__":
    router = SystemRouterDelta()
    router.register_delta_modules()
    print("Aktif Delta Kayıtları:", list(router.registry.keys()))
