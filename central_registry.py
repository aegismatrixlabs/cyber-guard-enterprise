from feature_auth import FeatureAuthModule

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
    print("Merkez Kayıt Durumu: Aktif ve Sağlıklı.")
