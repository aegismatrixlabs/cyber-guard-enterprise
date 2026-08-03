with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Hatalı olan satır bloklarını tamamen temizleyelim
if "target_string = f\"" in content:
    # Eski hatalı bloğu güvenli fonksiyon çağrısı ile değiştirelim
    old_block = """    target_string = f"{asset.ip_address} {asset.name}".lower()
    blacklisted_extensions = [".gov", ".mil", ".edu.tr", "gov.tr", "mil.tr"]
    if any(ext in target_string for ext in blacklisted_extensions):
        raise HTTPException(
            status_code=400,
            detail="Güvenlik Politikası İhlali: .gov, .mil veya yasaklı kritik varlık uzantılarına izin verilmemektedir."
        )"""
        
    new_block = """    if check_blacklisted_target(asset.ip_address, asset.name):
        raise HTTPException(
            status_code=400,
            detail="Güvenlik Politikası İhlali: .gov, .mil veya yasaklı kritik varlık uzantılarına izin verilmemektedir."
        )"""
        
    content = content.replace(old_block, new_block)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("211. satırdaki hata temizlendi ve güvenli fonksiyona bağlandı.")
else:
    print("Blok zaten temizlenmiş veya farklı formatta.")
