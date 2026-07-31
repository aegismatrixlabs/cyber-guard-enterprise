import sys
import os

# app klasörünün import edilebilmesi için path eklenmesi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feature_auth import FeatureAuthModule

def run_sandbox_tests():
    print("[*] CyberGuard Enterprise - feature_auth.py Sandbox Testleri Başlatılıyor...\n")
    auth = FeatureAuthModule()

    # TEST 1: Başarılı Kimlik Doğrulama (Tüm halkalar başarılı)
    print("--- TEST 1: Başarılı Giriş Senaryosu ---")
    res1 = auth.authenticate_user(
        email="admin@cyberguard.internal",
        password="SecurePassword123!",
        tenant_id="tenant_alpha_01",
        data_tenant_id="tenant_alpha_01",
        idempotency_key="test_key_001"
    )
    print("Sonuç:", res1)
    assert res1["status"] == "success", "Test 1 Başarısız!"
    print("[✓] Test 1 Başarılı.\n")

    # TEST 2: 1. Halka - Geçersiz Girdi / E-posta Formatı Doğrulaması
    print("--- TEST 2: Geçersiz E-posta (1. Halka Korunumu) ---")
    res2 = auth.authenticate_user(
        email="invalid-email-format",
        password="SecurePassword123!",
        tenant_id="tenant_alpha_01",
        data_tenant_id="tenant_alpha_01",
        idempotency_key="test_key_002"
    )
    print("Sonuç:", res2)
    assert res2["status"] == "error" and "Geçersiz e-posta" in res2["message"], "Test 2 Başarısız!"
    print("[✓] Test 2 Başarılı (Hata kontrollü yakalandı).\n")

    # TEST 3: 2. Halka - Çoklu-Kiracı (Tenant) İzolasyon İhlali
    print("--- TEST 3: Tenant İzolasyon İhlali (2. Halka Korunumu) ---")
    res3 = auth.authenticate_user(
        email="admin@cyberguard.internal",
        password="SecurePassword123!",
        tenant_id="tenant_alpha_01",
        data_tenant_id="tenant_beta_02",  # Uyuşmayan tenant id
        idempotency_key="test_key_003"
    )
    print("Sonuç:", res3)
    assert res3["status"] == "error" and "Yetkisiz kaynak" in res3["message"], "Test 3 Başarısız!"
    print("[✓] Test 3 Başarılı (İzolasyon ihlali engellendi).\n")

    # TEST 4: 4. Halka - Mükerrer İstek (Idempotency) Koruması
    print("--- TEST 4: Mükerrer İstek Koruması (4. Halka Korunumu) ---")
    # Aynı idempotency_key ile hemen tekrar istek atılıyor
    res4 = auth.authenticate_user(
        email="admin@cyberguard.internal",
        password="SecurePassword123!",
        tenant_id="tenant_alpha_01",
        data_tenant_id="tenant_alpha_01",
        idempotency_key="test_key_001"  # Test 1'de kullanılan anahtar
    )
    print("Sonuç:", res4)
    assert res4["status"] == "error" and "Mükerrer işlem" in res4["message"], "Test 4 Başarısız!"
    print("[✓] Test 4 Başarılı (Race condition/mükerrer istek engellendi).\n")

    print("[+] TÜM SANDBOX TESTLERİ BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    run_sandbox_tests()
