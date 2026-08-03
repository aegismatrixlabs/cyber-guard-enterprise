import os
import shutil
import sys

def archive_root_files():
    print("[*] AegisMatrix Kök Dizin Arındırma ve Modül Gölgeleme (Import Shadowing) Önleme Operasyonu Başlatılıyor...")
    project_root = os.getcwd()

    legacy_dir = os.path.join(project_root, "backups", "legacy_patches")
    os.makedirs(legacy_dir, exist_ok=True)

    target_files = [
        "database.py",
        "models.py",
        "auth.py",
        "security_filter.py",
        "final_sweep.py"
    ]

    try:
        for file_name in target_files:
            src_path = os.path.join(project_root, file_name)
            if os.path.exists(src_path):
                dest_path = os.path.join(legacy_dir, file_name)
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(src_path, dest_path)
                print(f"    [+] Arşive taşındı: {file_name} -> backups/legacy_patches/")
            else:
                print(f"    [!] Bulunamadı / Zaten taşınmış: {file_name}")

        print("\n[✔] Kök Dizin Sterilizasyonu Başarıyla Tamamlandı.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Archive Root Files]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    archive_root_files()
