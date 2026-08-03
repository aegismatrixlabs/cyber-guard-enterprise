import os
import shutil
import sys

def execute_final_blueprint():
    print("[*] AegisMatrix Nihai Mimari (Final Blueprint) Geçişi Başlatılıyor...")
    project_root = os.getcwd()

    try:
        templates_dir = os.path.join(project_root, "templates")
        data_dir = os.path.join(project_root, "data")
        backups_dir = os.path.join(project_root, "backups")

        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(backups_dir, exist_ok=True)

        html_files = [
            "threat_intel.html", "reports.html", "settings.html", 
            "vulnerability_details.html", "cloud_security.html", 
            "compliance.html", "integrations.html", "login.html", 
            "index.html", "scans.html", "dashboard.html", 
            "assets.html", "incident_response.html"
        ]

        for html_file in html_files:
            src = os.path.join(project_root, html_file)
            if os.path.exists(src):
                shutil.move(src, os.path.join(templates_dir, html_file))
                print(f"    [+] Şablon taşındı: {html_file} -> templates/")

        root_db = os.path.join(project_root, "cyber_guard.db")
        target_db = os.path.join(data_dir, "cyber_guard.db")
        if os.path.exists(root_db) and not os.path.exists(target_db):
            shutil.move(root_db, target_db)
            print("    [+] Veritabanı konsolide edildi: cyber_guard.db -> data/")
        elif os.path.exists(root_db):
            os.remove(root_db)
            print("    [+] Mükerrer kök veritabanı temizlendi.")

        main_path = os.path.join(project_root, "main.py")
        if os.path.exists(main_path):
            with open(main_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "Jinja2Templates" in content and "directory=\".\"" in content:
                updated_content = content.replace("directory=\".\"", "directory=\"templates\"")
                with open(main_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print("    [+] main.py şablon dizin yolu 'templates' olarak güncellendi.")

        print("\n[✔] Final Blueprint Mimari Geçişi Başarıyla Tamamlandı.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Blueprint Migration]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    execute_final_blueprint()
