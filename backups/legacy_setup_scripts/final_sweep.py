import os
import shutil
import sys

def execute_final_sweep():
    print("[*] AegisMatrix Son Temizlik ve Süpürme Operasyonu Başlatılıyor...")
    project_root = os.getcwd()

    try:
        # 1. Split-brain riskine karşı app/ içindeki mükerrer veritabanını temizleme
        app_db = os.path.join(project_root, "app", "cyber_guard.db")
        if os.path.exists(app_db):
            os.remove(app_db)
            print("    [+] Mükerrer alt veritabanı temizlendi: app/cyber_guard.db")

        # 2. Kök dizindeki geçici betikleri arşive taşıma
        legacy_dir = os.path.join(project_root, "backups", "legacy_setup_scripts")
        os.makedirs(legacy_dir, exist_ok=True)

        sweep_scripts = [
            "execute_blueprint.py",
            "deep_cleanup.py",
            "perfect_cleanup.py"
        ]

        for script in sweep_scripts:
            script_path = os.path.join(project_root, script)
            if os.path.exists(script_path):
                shutil.move(script_path, os.path.join(legacy_dir, script))
                print(f"    [+] Betik arşive taşındı: {script}")

        print("\n[✔] Son Temizlik Operasyonu Başarıyla Tamamlandı.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Final Sweep]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    execute_final_sweep()
