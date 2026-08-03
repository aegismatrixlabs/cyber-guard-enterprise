import requests

BASE_URL = "http://127.0.0.1:8000"

def test_enterprise_pages():
    print("--- 1. Hakkımızda Sayfası Testi ---")
    res = requests.get(f"{BASE_URL}/api/pages/about")
    print(res.status_code, res.json())
    assert res.status_code == 200
    assert res.json().get("official_contact_email") == "aegismatrixlabs@gmail.com"

    print("\n--- 2. Gizlilik Politikası Testi ---")
    res = requests.get(f"{BASE_URL}/api/pages/privacy")
    print(res.status_code, res.json())
    assert res.status_code == 200

    print("\n--- 3. Yardım Merkezi Testi ---")
    res = requests.get(f"{BASE_URL}/api/pages/help")
    print(res.status_code, res.json())
    assert res.status_code == 200

    print("\n--- 4. İletişim Formu (Gmail Yönlendirme) Testi ---")
    payload = {
        "name": "Necdet Çelik",
        "email": "aegismatrixlabs@gmail.com",
        "subject": "Kurumsal Entegrasyon Destek",
        "message": "AegisMatrix Labs platformu için destek talebi oluşturulmuştur."
    }
    res = requests.post(f"{BASE_URL}/api/pages/contact", json=payload)
    print(res.status_code, res.json())
    assert res.status_code == 201
    assert "aegismatrixlabs@gmail.com" in res.json().get("message")

    print("\nTÜM KURUMSAL SAYFA TESTLERİ BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    test_enterprise_pages()
