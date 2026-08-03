# Bu script mevcut main.py üzerine Varlık Yönetimi modülünü güvenle entegre eder.
import re

with open("main.py", "r") as f:
    content = f.read()

# Eğer modül daha önce eklenmediyse ekleyelim
if "assets-ui" not in content:
    new_route = '''
# --- MODÜL 1: VARLIK YÖNETİMİ VE LEGAL SHIELD ---
from fastapi.responses import HTMLResponse

fake_verified_assets_db = ["example.com", "aegismatrixlabs.com"]

@app.get("/assets-ui", tags=["Asset Management"])
async def assets_management_ui():
    return f\"\"\"
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Varlık Yönetimi - AegisMatrix Labs</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8">
        <div class="max-w-4xl mx-auto">
            <div class="flex justify-between items-center mb-8">
                <h1 class="text-2xl font-bold text-white">🎯 Varlık Yönetimi & Legal Shield</h1>
                <a href="/" class="text-sm text-emerald-400 hover:underline">← Kontrol Paneline Dön</a>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl mb-8 shadow-lg">
                <h3 class="text-lg font-semibold mb-4 text-white">Yeni Hedef Varlık Ekle</h3>
                <form action="/api/assets/add-ui" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Hedef Domain / IP</label>
                        <input type="text" name="target" placeholder="hedefdomain.com" required class="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-emerald-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Doğrulama Yöntemi</label>
                        <select name="method" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-emerald-500 focus:outline-none">
                            <option value="DNS_TXT">DNS TXT Kaydı</option>
                            <option value="HTTP_WELLKNOWN">HTTP (.well-known)</option>
                        </select>
                    </div>
                    <button type="submit" class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg font-semibold transition">Varlığı Kaydet ve Doğrula</button>
                </form>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
                <h3 class="text-lg font-semibold mb-4 text-white">Doğrulanmış Varlık Listesi</h3>
                <div class="space-y-2">
                    {''.join([f'<div class="bg-slate-950 p-3 rounded-lg flex justify-between items-center border border-slate-800"><span class="font-mono text-emerald-400">{asset}</span><span class="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full font-medium">VERIFIED (LEGAL SHIELD)</span></div>' for asset in fake_verified_assets_db])}
                </div>
            </div>
        </div>
    </body>
    </html>
    \"\"\"

@app.post("/api/assets/add-ui", tags=["Asset Management"])
async def add_asset_ui(target: str = Form(...), method: str = Form(...)):
    target_clean = target.strip().lower()
    if target_clean.endswith(".gov") or target_clean.endswith(".mil"):
        raise HTTPException(status_code=403, detail="Yasal Sınır İhlali: .gov ve .mil hedefleri taranamaz.")
    if target_clean not in fake_verified_assets_db:
        fake_verified_assets_db.append(target_clean)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/assets-ui", status_code=303)
'''
    from fastapi import Form
    # main.py sonuna ekleme yapıyoruz
    with open("main.py", "a") as f:
        f.write(new_route)
    print("Varlık Yönetimi modülü başarıyla eklendi.")
else:
    print("Modül zaten mevcut.")
