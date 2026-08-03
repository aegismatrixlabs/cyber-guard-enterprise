# Bu script test_api.py dosyasına kara liste testini ekler
with open("test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Eğer test zaten eklenmediyse ekleyelim
if "Blacklist" not in content:
    target_str = "    # 3. Varlık Ekleme"
    new_test_block = """    # 3.1 Kara Liste (Blacklist / .gov / .mil) Negatif Testi
    blacklisted_payload = {
        "name": "Secret-State-Gateway",
        "ip_address": "target.gov",
        "asset_type": "Cloud Server"
    }
    response = requests.post(f"{BASE_URL}/api/assets", json=blacklisted_payload, headers=headers)
    print(f"3.1 Kara Liste Varlık Ekleme Durum Kodu: {response.status_code}")
    print(f"   Yanıt: {response.json()}")
    assert response.status_code == 400, "Sistem kritik .gov uzantılı varlığa izin verdi!"
    print("   ✅ Kara liste filtresi başarıyla engelledi (.gov uzantısı yasaklı).\\n")

    # 3. Varlık Ekleme"""
    
    content = content.replace(target_str, new_test_block)
    with open("test_api.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("test_api.py dosyasına kara liste testi başarıyla eklendi.")
else:
    print("Kara liste testi zaten mevcut.")
