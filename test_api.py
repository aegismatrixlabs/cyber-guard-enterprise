import requests
import json
import hmac
import hashlib

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("🚀 AEGIS_MATRIX | Varlık Sahiplik Doğrulama (Legal Shield) ve Entegrasyon Testi Başlıyor...\n")

    # 1. Kayıt Olma
    register_payload = {
        "email": "cevik@aegismatrixlabs.com",
        "password": "SecurePassword123!",
        "company_name": "AegisMatrix Labs Corp",
        "role": "Admin"
    }
    response = requests.post(f"{BASE_URL}/api/register", json=register_payload)
    print(f"1. Kayıt İşlemi Durum Kodu: {response.status_code}")
    assert response.status_code in [201, 400], "Kayıt aşamasında beklenmeyen hata!"
    print("   ✅ Kayıt testi başarılı.\n")

    # 2. Giriş Yapma (Login)
    login_payload = {
        "email": "cevik@aegismatrixlabs.com",
        "password": "SecurePassword123!"
    }
    response = requests.post(f"{BASE_URL}/api/login", json=login_payload)
    print(f"2. Giriş İşlemi Durum Kodu: {response.status_code}")
    data = response.json()
    assert response.status_code == 200, "Giriş başarısız!"
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Giriş başarılı, JWT alındı.\n")

    # 3. Varlık Ekleme
    asset_payload = {
        "name": "Production-Gateway",
        "ip_address": "127.0.0.1",
        "asset_type": "Cloud Server"
    }
    response = requests.post(f"{BASE_URL}/api/assets", json=asset_payload, headers=headers)
    print(f"3. Varlık Ekleme Durum Kodu: {response.status_code}")
    asset_data = response.json()
    assert response.status_code == 201
    asset_id = asset_data["asset_id"]
    print("   ✅ Varlık başarıyla eklendi (Doğrulanmamış).\n")

    # 4. Yasal Kalkan Negatif Testi (Doğrulanmadan ve Aboneliksiz Tarama Denemesi -> 402 veya 400 Bekleniyor)
    scan_payload = {"asset_id": asset_id}
    response = requests.post(f"{BASE_URL}/api/scans", json=scan_payload, headers=headers)
    print(f"4. Güvenlik Duvarı Negatif Testi Durum Kodu: {response.status_code}")
    print(f"   Yanıt: {response.json()}")
    assert response.status_code in [400, 402], "Güvenlik duvarı tarama izni verdi!"
    print("   ✅ Güvenlik duvarı başarıyla taramayı engelledi.\n")

    # 5. Lemon Squeezy Webhook ile Abonelik Aktivasyonu Simülasyonu
    webhook_payload = {
        "meta": {
            "event_name": "subscription_created",
            "variant_name": "Enterprise SOC Tier",
            "custom_data": {
                "company_id": 1
            }
        }
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    secret = "aegismatrix_secure_webhook_secret_key"
    signature = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    webhook_headers = {"X-Signature": signature, "Content-Type": "application/json"}

    response = requests.post(f"{BASE_URL}/api/webhooks/lemonsqueezy", data=raw_body, headers=webhook_headers)
    print(f"5. Webhook Abonelik Aktivasyonu Durum Kodu: {response.status_code}")
    assert response.status_code == 200
    print("   ✅ Abonelik webhook ile aktifleşti.\n")

    # 6. Şimdi tekrar tarama deneyelim (Bu sefer abonelik aktif ama varlık henüz DOĞRULANMADI -> 400 Bekleniyor)
    response = requests.post(f"{BASE_URL}/api/scans", json=scan_payload, headers=headers)
    print(f"6. Yasal Kalkan (Legal Shield) Negatif Testi Durum Kodu: {response.status_code}")
    print(f"   Yanıt: {response.json()}")
    assert response.status_code == 400, "Yasal kalkan doğrulanmamış varlığa tarama izni verdi!"
    print("   ✅ Legal Shield başarıyla engelledi (Varlık doğrulanmamış).\n")

    # 7. Varlık Doğrulama Talebi
    response = requests.post(f"{BASE_URL}/api/assets/{asset_id}/verify/request", headers=headers)
    print(f"7. Doğrulama Talebi Durum Kodu: {response.status_code}")
    assert response.status_code == 200
    print("   ✅ Doğrulama token'ı oluşturuldu.\n")

    # 8. Varlık Sahiplik Onayı (Confirm)
    response = requests.post(f"{BASE_URL}/api/assets/{asset_id}/verify/confirm", headers=headers)
    print(f"8. Doğrulama Onayı Durum Kodu: {response.status_code}")
    assert response.status_code == 200
    print("   ✅ Varlık sahipliği başarıyla doğrulandı.\n")

    # 9. Başarılı Otonom Tarama Testi (Abonelik aktif + Varlık doğrulanmış)
    response = requests.post(f"{BASE_URL}/api/scans", json=scan_payload, headers=headers)
    print(f"9. Başarılı Otonom Tarama Durum Kodu: {response.status_code}")
    print(f"   Yanıt: {response.json()}")
    assert response.status_code == 201
    print("   ✅ Otonom zafiyet taraması başarıyla tamamlandı.\n")

    # 10. ISO 27001 Denetim Günlükleri Kontrolü (Audit Trail)
    response = requests.get(f"{BASE_URL}/api/audit/logs", headers=headers)
    print(f"10. Denetim Günlükleri Durum Kodu: {response.status_code}")
    audit_data = response.json()
    print(f"    Toplam Log Sayısı: {audit_data.get('count')}")
    assert response.status_code == 200
    print("    ✅ ISO 27001 Denetim izi kayıtları başarıyla listelendi.\n")

    print("🎉 TÜM TESTLER BAŞARIYLA TAMAMLANDI! AegisMatrix Legal Shield ve Abonelik Mimarisi Kusursuz Çalışıyor.")

if __name__ == "__main__":
    run_tests()
