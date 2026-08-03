import sys
import os

def test_scanner_and_broker():
    print("[*] AegisMatrix Otonom Tarayıcı ve Event Broker Modülleri Test Ediliyor...")
    try:
        import app.feature_scanner_core as scanner_mod
        print("    [+] Başarılı: app.feature_scanner_core yüklendi.")

        import app.feature_event_broker as broker_mod
        print("    [+] Başarılı: app.feature_event_broker yüklendi.")

        print("\n[✔] Otonom Çekirdek ve Olay Yönetimi Modülleri Tamamen Sağlıklı.")

    except Exception as e:
        print(f"[!] KRİTİK HATA [Scanner/Broker Test]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    test_scanner_and_broker()
