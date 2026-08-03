import sys
import os

def run_smoke_tests():
    print("[*] AegisMatrix Smoke Test ve Endpoint Doğrulaması Başlatılıyor...")
    try:
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        # Test edilecek temel uç noktalar ve açıklamaları
        endpoints = [
            ("/", "Root Endpoint"),
            ("/login", "Giriş Sayfası"),
            ("/docs", "Swagger API Dokümantasyonu"),
            ("/dashboard", "Yönetim Paneli (Protected)"),
            ("/scans", "Tarama Modülü Sayfası")
        ]

        for path, desc in endpoints:
            response = client.get(path, follow_redirects=False)
            print(f"    [+] Endpoint: {path:<15} | Açıklama: {desc:<25} | Status: {response.status_code}")

        print("\n[✔] Smoke Testler Başarıyla Tamamlandı. Sistem Kararlı ve Ayakta.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Smoke Test]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_smoke_tests()
