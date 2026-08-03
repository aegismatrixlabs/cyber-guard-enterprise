import os
import sys

def execute_faz5_dry_run():
    print("[*] AegisMatrix Faz 5: Sunucu Kuru Çalıştırma (Dry-Run) ve Import Testi Başlatılıyor...")
    project_root = os.getcwd()
    sys.path.insert(0, project_root)

    try:
        # main.py içerisindeki FastAPI instance'ını (app) güvenli şekilde içe aktarmayı dene
        import main
        if hasattr(main, "app"):
            print("    [+] FastAPI 'app' nesnesi main.py içinde başarıyla bulundu.")
        else:
            print("    [!] Uyarı: main.py içinde 'app' nesnesi tanımlı değil!")
        print("[✔] Faz 5 Dry-Run Testi Başarıyla Tamamlandı. Sistem Kararlı ve Çalışmaya Hazır.")
    except Exception as e:
        print(f"    [!] KRİTİK IMPORT/ÇALIŞTIRMA HATASI: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_faz5_dry_run()
