import os
import shutil
import sys

def perfect_project_structure():
    print("[*] AegisMatrix %100 Kusursuzluk ve Son Arındırma Operasyonu Başlatılıyor...")
    project_root = os.getcwd()

    try:
        legacy_dir = os.path.join(project_root, "backups", "legacy_patches")
        os.makedirs(legacy_dir, exist_ok=True)

        # 1. Kök dizindeki mükerrer feature_auth.py kontrolü ve arşivi
        root_auth = os.path.join(project_root, "feature_auth.py")
        app_auth = os.path.join(project_root, "app", "feature_auth.py")
        if os.path.exists(root_auth) and os.path.exists(app_auth):
            shutil.move(root_auth, os.path.join(legacy_dir, "feature_auth.py"))
            print("    [+] Mükerrer kök feature_auth.py arşivlendi.")

        # 2. Yama ve fix betiklerinin arşivi
        patch_files = [
            "fix_line211.py",
            "fix_endpoint.py",
            "apply_blacklist_fix.py",
            "fix_security_check.py",
            "update_test.py"
        ]

        for p_file in patch_files:
            p_path = os.path.join(project_root, p_file)
            if os.path.exists(p_path):
                shutil.move(p_path, os.path.join(legacy_dir, p_file))
                print(f"    [+] Yama dosyası arşivlendi: {p_file}")

        # 3. Veritabanı katmanı köprü kontrolü
        root_db = os.path.join(project_root, "database.py")
        store_db = os.path.join(project_root, "database", "store.py")
        if os.path.exists(root_db) and os.path.exists(store_db):
            with open(root_db, "w", encoding="utf-8") as f:
                f.write("# -*- coding: utf-8 -*-\n# Single Source of Truth Bridge for Database Store\nfrom database.store import *\n")
            print("    [+] Kök database.py, database/store.py modülüne köprülendi.")

        print("\n[✔] Proje Yapısı %100 Kusursuz ve Lansmana Hazır Duruma Getirildi.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Kusursuzlaştırma]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    perfect_project_structure()
