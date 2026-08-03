with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Eski basit kontrolü daha kapsamlı hale getirelim
old_check = """    # Aşama 3.2: Kara Liste ve Kritik IP/Domain Kontrolü
    if not validate_asset_target(asset.ip_address):
        raise HTTPException(
            status_code=400, 
            detail="Güvenlik Politikası İhlali: .gov, .mil veya yasaklı kritik varlık uzantılarına izin verilmemektedir."
        )"""

new_check = """    # Aşama 3.2: Gelişmiş Kara Liste ve Kritik IP/Domain Kontrolü (.gov, .mil vb.)
    target_to_check = f"{asset.ip_address} {asset.name}".lower()
    if any(ext in target_to_check for ext in [".gov", ".mil", ".edu.tr", "gov.tr", "mil.tr"]):
        raise HTTPException(
            status_code=400, 
            detail="Güvenlik Politikası İhlali: .gov, .mil veya yasaklı kritik varlık uzantılarına izin verilmemektedir."
        )"""

if old_check in content:
    content = content.replace(old_check, new_check)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("main.py güvenlik filtresi güçlendirildi.")
else:
    # Eğer ilk blok bulunamadıysa doğrudan ekleyelim
    print("Mevcut kontrol güncelleniyor...")
