with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Eğer filtre endpoint içinde çağrılmıyorsa ekleyelim
target_code = """@app.post("/api/assets", status_code=201)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):"""

replacement_code = """@app.post("/api/assets", status_code=201)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Aşama 3.2: Kara Liste ve Kritik IP/Domain Kontrolü
    if not validate_asset_target(asset.ip_address):
        raise HTTPException(
            status_code=400, 
            detail="Güvenlik Politikası İhlali: .gov, .mil veya yasaklı kritik varlık uzantılarına izin verilmemektedir."
        )"""

if "validate_asset_target(asset.ip_address)" not in content:
    content = content.replace(target_code, replacement_code)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("main.py içerisindeki varlık ekleme endpoint'ine güvenlik filtresi başarıyla entegre edildi.")
else:
    print("Filtre zaten endpoint'e eklenmiş.")
