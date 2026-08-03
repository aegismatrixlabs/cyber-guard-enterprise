import os
import sys

def execute_faz3_router_check():
    print("[*] AegisMatrix Faz 3: Modüler Router İzolasyonu Denetleniyor...")

    project_root = os.getcwd()
    routers_dir = os.path.join(project_root, "routers")
    expected_routers = ["auth.py", "assets.py", "operations.py", "__init__.py"]

    if os.path.exists(routers_dir):
        print("    [+] routers/ dizini mevcut.")
        for router in expected_routers:
            r_path = os.path.join(routers_dir, router)
            if os.path.exists(r_path):
                print(f"        [+] Router modülü doğrulandı: {router}")
            else:
                print(f"        [!] Uyarı: {router} dosyası eksik.")
    else:
        print("    [!] routers/ dizini bulunamadı!")

    print("[✔] Faz 3 Router Doğrulaması Tamamlandı.")

if __name__ == "__main__":
    execute_faz3_router_check()
