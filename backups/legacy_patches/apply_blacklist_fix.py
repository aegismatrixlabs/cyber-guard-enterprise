import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# create_asset fonksiyonunun hemen girişine kara liste filtresini ekleyelim
target_line = '@app.post("/api/assets", status_code=201)\ndef create_asset('

filter_code = '''@app.post("/api/assets", status_code=201)
def create_asset(
    asset: AssetCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # AŞAMA 3.2: Kesin Kara Liste ve Kritik IP/Domain Filtresi (.gov, .mil vb.)
    target_string = f"{asset.ip_address} {asset.name}".lower()
    blacklisted_extensions = [".gov", ".mil", ".edu.tr", "gov.tr", "mil.tr"]
    
    if any(ext in target_string for ext in blacklisted_extensions):
        raise HTTPException(
            status_code=400,
            detail="Güvenlik Politikası İhlali: .gov, .mil veya yasaklı kritik varlık uzantılarına izin verilmemektedir."
        )
'''

# Eğer daha önce eklenmişse temizleyelim, yeniden ekleyelim
if "AŞAMA 3.2" in content:
    print("Zaten eklenmiş veya eski blok var, temizleniyor...")
    # Basitçe dosyanın orijinalini koruyup sadece fonksiyonu güncelleyelim
    print("Lütfen main.py dosyasını kontrol edin.")
else:
    if target_line in content:
        new_content = content.replace(target_line, filter_code)
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ Kara liste filtresi main.py dosyasına başarıyla eklendi!")
    else:
        print("❌ Hedef satır bulunamadı.")

