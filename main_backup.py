from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
import os

app = FastAPI(title="AegisMatrix Labs Enterprise Core", version="2.1")

# Veritabanı ve Tablo Kontrolü
def init_db():
    try:
        conn = sqlite3.connect("aegismatrix.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT,
                target_url TEXT,
                status TEXT,
                risk_score TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT,
                module_name TEXT,
                target TEXT,
                severity TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[-] DB Error: {e}")

init_db()

# Anasayfa
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="tr">
    <head><meta charset="UTF-8"><title>AegisMatrix Labs</title></head>
    <body style="background: #0b0f19; color: white; text-align: center; padding-top: 100px; font-family: Arial;">
        <h1>AEGIS<span style="color:#00ff88">MATRIX</span> LABS</h1>
        <p>Otonom Güvenlik Operasyon Merkezi</p>
        <a href="/dashboard" style="background: #00c853; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Kontrol Paneline Git</a>
    </body>
    </html>
    """)

# Dashboard ve Varlık Listeleme + Ekleme Paneli
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        conn = sqlite3.connect("aegismatrix.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, target_url, status, risk_score FROM assets")
        assets = cursor.fetchall()
        
        cursor.execute("SELECT module_name, target, severity FROM findings")
        findings = cursor.fetchall()
        conn.close()
    except Exception as e:
        assets = []
        findings = []

    # HTML Arayüzü (Form Dahil)
    html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard - AegisMatrix Labs</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f293d; padding-bottom: 15px; }}
            .logo {{ color: #00ff88; font-size: 1.5rem; font-weight: bold; }}
            .form-box {{ background: #131d31; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #1f293d; }}
            input[type="text"] {{ padding: 10px; width: 300px; background: #0b0f19; border: 1px solid #1f293d; color: white; border-radius: 4px; }}
            button {{ padding: 10px 20px; background: #00c853; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
            button:hover {{ background: #00e676; }}
            table {{ width: 100%; margin-top: 20px; border-collapse: collapse; background-color: #131d31; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1f293d; }}
            th {{ background-color: #1a263d; color: #8a99ad; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">AEGIS<span style="color:#ffffff">MATRIX</span></div>
            <div>Durum: <span style="color: #00ff88;">CANLI SİSTEM & FORM AKTİF</span></div>
        </div>

        <div class="form-box">
            <h3>Yeni Hedef / Varlık Ekle</h3>
            <form action="/add-asset" method="post">
                <input type="text" name="target_url" placeholder="https://hedefsite.com" required>
                <button type="submit">Varlık Ekle ve Tara</button>
            </form>
        </div>

        <h3>Kayıtlı Varlıklar (Hedefler)</h3>
        <table>
            <tr><th>ID</th><th>Hedef URL</th><th>Durum</th><th>Risk Skoru</th></tr>
    """
    
    for a in assets:
        html += f"<tr><td>{a[0]}</td><td style='color:#00ff88;'>{a[1]}</td><td>{a[2]}</td><td>{a[3]}</td></tr>"
        
    html += """
        </table>
        <br><a href="/" style="color: #8a99ad; text-decoration: none;">← Ana Sayfaya Dön</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# Hedef Ekleme İşlemi (POST Endpoint)
@app.post("/add-asset")
async def add_asset(target_url: str = Form(...)):
    try:
        conn = sqlite3.connect("aegismatrix.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO assets (tenant_id, target_url, status, risk_score) VALUES (?, ?, ?, ?)", 
                       ("tenant_01", target_url, "ACTIVE", "PENDING"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[-] Ekleme Hatası: {e}")
    
    return RedirectResponse(url="/dashboard", status_code=303)
