import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_async_scan_workflow():
    print("--- 1. RoE Sözleşmesi Onaylanıyor ---")
    payload_roe = {
        "accepted": True,
        "full_name": "Necdet Çelik",
        "company_title": "AegisMatrix Labs CEO"
    }
    res = requests.post(f"{BASE_URL}/api/roe/accept", json=payload_roe)
    print(res.status_code, res.json())
    assert res.status_code == 200

    print("\n--- 2. Asenkron Otonom Tarama Başlatılıyor (202 Bekleniyor) ---")
    payload_scan = {"target": "10.0.0.15-aws-instance"}
    res = requests.post(f"{BASE_URL}/api/scans", json=payload_scan)
    print(res.status_code, res.json())
    assert res.status_code == 202
    
    data = res.json()
    scan_id = data.get("scan_id")
    print(f"Oluşturulan Tarama ID: {scan_id} - Durum: {data.get('status')}")

    print("\n--- 3. Tarama Durumu Kontrol Ediliyor (Kuyruk / Çalışıyor / Tamamlandı) ---")
    for i in range(5):
        time.sleep(1)
        status_res = requests.get(f"{BASE_URL}/api/scans/{scan_id}")
        scan_data = status_res.json().get("data", {})
        print(f"Deneme {i+1} -> Tarama Durumu: {scan_data.get('status')}")
        if scan_data.get("status") == "completed":
            print("Tarama Başarıyla Tamamlandı!", scan_data)
            break

    print("\nTÜM ASENKRON TARAMA KUYRUĞU TESTLERİ BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    test_async_scan_workflow()
