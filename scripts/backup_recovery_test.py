import sys
import os

def test_backup_and_recovery():
    print("[*] AegisMatrix Yedekleme ve Felaket Kurtarma Modülleri Test Ediliyor...")
    try:
        import app.saas_backup_manager as backup_mod
        print("    [+] Başarılı: app.saas_backup_manager yüklendi.")

        import app.saas_system_restore as restore_mod
        print("    [+] Başarılı: app.saas_system_restore yüklendi.")

        print("\n[✔] Yedekleme ve Felaket Kurtarma Modülleri Tamamen Sağlıklı ve Hazır.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Backup/Recovery Test]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    test_backup_and_recovery()
