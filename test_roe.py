import requests

BASE_URL = "http://127.0.0.1:8000"

def test_roe_workflow():
    print("--- 1. RoE Durum Kontrolü (Onaysız) ---")
    res = requests.get(f"{BASE_URL}/api/roe/status?email=default_user@aegismatrixlabs.com")
    print(res.status_code, res.json())
    assert res.json().get("roe_accepted") == False

    print("\n--- 2. RoE Onayı Olmadan Tarama Testi (403 Bekleniyor) ---")
    res = requests.post(f"{BASE_URL}/api/scans", json={"target": "192.168.1.50"})
    print(res.status_code, res.json())
    assert res.status_code == 403

    print("\n--- 3. RoE Sözleşmesini İmzalama ---")
    payload = {
        "accepted": True,
        "full_name": "Necdet Çelik",
        "company_title": "AegisMatrix Labs CEO"
    }
    res = requests.post(f"{BASE_URL}/api/roe/accept", json=payload)
    print(res.status_code, res.json())
    assert res.status_code == 200

    print("\n--- 4. RoE Sonrası Tarama Testi (201 Bekleniyor) ---")
    res = requests.post(f"{BASE_URL}/api/scans", json={"target": "192.168.1.50"})
    print(res.status_code, res.json())
    assert res.status_code == 201

    print("\nTÜM ROE TESTLERİ BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    test_roe_workflow()
