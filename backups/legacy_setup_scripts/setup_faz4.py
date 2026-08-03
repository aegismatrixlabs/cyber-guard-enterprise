import os
import sys

def execute_faz4_health_check():
    print("[*] AegisMatrix Faz 4: Ana Uygulama (main.py) ve Sistem Sağlığı Denetleniyor...")

    project_root = os.getcwd()
    main_path = os.path.join(project_root, "main.py")

    if os.path.exists(main_path):
        print("    [+] Ana uygulama dosyası (main.py) doğrulandı.")
    else:
        print("    [!] Uyarı: main.py kök dizinde bulunamadı!")

    # FastAPI / Uvicorn bağımlılık kontrolü simülasyonu
    try:
        import fastapi
        import uvicorn
        print("    [+] FastAPI ve Uvicorn paketleri aktif.")
    except ImportError as e:
        print(f"    [!] Eksik paket bağımlılığı: {str(e)}")

    print("[✔] Faz 4 Sistem Sağlığı Doğrulaması Tamamlandı.")

if __name__ == "__main__":
    execute_faz4_health_check()
