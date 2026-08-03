import os
import shutil
import sys

def execute_deep_cleanup():
    print("[*] AegisMatrix Derin Temizlik ve Tekilleştirme Başlatılıyor...")
    project_root = os.getcwd()

    # 1. Geçici setup/faz dosyalarını arşivleme
    temp_files = [
        "cleanup_faz1.py",
        "setup_faz2.py",
        "setup_faz3.py",
        "setup_faz4.py",
        "setup_faz5.py"
    ]

    backup_archive_dir = os.path.join(project_root, "backups", "legacy_setup_scripts")
    if not os.path.exists(backup_archive_dir):
        os.makedirs(backup_archive_dir, exist_ok=True)

    for file_name in temp_files:
        file_path = os.path.join(project_root, file_name)
        if os.path.exists(file_path):
            shutil.move(file_path, os.path.join(backup_archive_dir, file_name))
            print(f"    [+] Arşivlendi: {file_name}")

    # 2. Mükerrer kök dosyalarını temizleme
    redundant_root_files = [
        "saas_backup_manager.py",
        "central_registry.py"
    ]

    for r_file in redundant_root_files:
        root_path = os.path.join(project_root, r_file)
        app_path = os.path.join(project_root, "app", r_file)

        if os.path.exists(root_path) and os.path.exists(app_path):
            os.remove(root_path)
            print(f"    [+] Mükerrer kök dosyası temizlendi: {r_file}")

    print("[✔] Derin Temizlik Başarıyla Tamamlandı.")

if __name__ == "__main__":
    execute_deep_cleanup()
