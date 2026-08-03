from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
from models import User, Subscription, Asset, AuditLog
from schemas import Token
import requests
import os
import secrets
import re
import ssl
import socket
import json
from urllib.parse import urlparse

# --- PDF ---
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

SECRET_KEY = "CyberGuard_Enterprise_Super_Secret_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password, hashed_password): return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password): return pwd_context.hash(password)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db(): db = SessionLocal(); yield db; db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Geçersiz kimlik bilgileri", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError: raise credentials_exception
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None: raise credentials_exception
    return user

def check_subscription(current_user):
    db = SessionLocal()
    sub = db.query(Subscription).filter(Subscription.username == current_user.username).first()
    db.close()
    if not sub or sub.status != "ACTIVE":
        raise HTTPException(status_code=402, detail="Ticari Lisans Kapısı: Aboneliğiniz aktif değil.")
    return True

def log_audit(username: str, action: str):
    db = SessionLocal()
    log = AuditLog(username=username, action=action, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(log); db.commit(); db.close()

# --- DERİN TARAMA MOTORU (MODÜL 10) ---
def deep_scan_url(url: str):
    # 1. Standart HTTP/HTTPS erişim testi
    try:
        r = requests.get(url, timeout=5)
        durum = "ACTIVE" if r.status_code == 200 else "INACTIVE"
        headers_dict = dict(r.headers)
    except:
        durum = "INACTIVE"
        headers_dict = {}

    # 2. SSL Sertifika Kontrolü
    ssl_days = -1
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                ssl_days = (expiry_date - datetime.now()).days
    except:
        ssl_days = -1

    # 3. Güvenlik Başlıkları (Headers) Kontrolü
    headers_status = "N/A"
    if durum == "ACTIVE":
        required_headers = ['X-Frame-Options', 'Content-Security-Policy', 'Strict-Transport-Security']
        found_headers = [h for h in required_headers if h in headers_dict]
        if len(found_headers) >= 2:
            headers_status = "SECURE"
        else:
            headers_status = "MISSING"

    # 4. Açık Port Kontrolü (Basit TCP, hız için timeout çok düşük)
    open_ports = []
    common_ports = [80, 443, 22, 21]
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((hostname, port))
            if result == 0:
                open_ports.append(str(port))
            sock.close()
    except:
        pass

    # 5. Genel Risk Skoru Hesaplaması
    if durum == "INACTIVE":
        risk_skoru = "HIGH"
    elif ssl_days < 15 and ssl_days != -1:
        risk_skoru = "HIGH"
    elif headers_status == "MISSING":
        risk_skoru = "MEDIUM"
    else:
        risk_skoru = "LOW"

    return {
        "status": durum,
        "risk_score": risk_skoru,
        "ssl_days": ssl_days,
        "headers_status": headers_status,
        "open_ports": ", ".join(open_ports) if open_ports else "N/A"
    }

# --- ROTALAR ---
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/login.html", "r", encoding="utf-8") as f: return HTMLResponse(content=f.read())

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    with open("templates/dashboard.html", "r", encoding="utf-8") as f: return HTMLResponse(content=f.read())

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()
    db.close()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")
    log_audit(form_data.username, "Kullanıcı giriş yaptı.")
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer"}

@app.post("/api/subscription/activate")
async def activate_subscription(plan: str = "Pro", db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(Subscription).filter(Subscription.username == current_user.username).first()
    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    if existing:
        existing.plan_name, existing.status, existing.expires_at = plan, "ACTIVE", expires_at
    else:
        db.add(Subscription(username=current_user.username, plan_name=plan, status="ACTIVE", expires_at=expires_at))
    log_audit(current_user.username, f"Abonelik aktif: {plan}")
    db.commit()
    return {"message": f"{plan} plan aboneliği aktifleştirildi! 30 gün boyunca tarama yapabilirsiniz.", "expires_at": expires_at}

@app.post("/api/assets")
async def create_asset(asset: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    check_subscription(current_user)
    url = asset.get("url")
    scan_result = deep_scan_url(url)
    new_asset = Asset(
        url=url, 
        status=scan_result["status"], 
        risk_score=scan_result["risk_score"],
        ssl_expiry_days=scan_result["ssl_days"],
        security_headers_status=scan_result["headers_status"],
        open_ports=scan_result["open_ports"],
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        owner_username=current_user.username
    )
    db.add(new_asset)
    log_audit(current_user.username, f"Varlık derin tarandı: {url}")
    db.commit(); db.refresh(new_asset)
    return {
        "message": f"'{url}' tarandı.", 
        "status": scan_result["status"], 
        "risk_score": scan_result["risk_score"],
        "ssl_days": scan_result["ssl_days"],
        "headers_status": scan_result["headers_status"],
        "open_ports": scan_result["open_ports"]
    }

@app.get("/api/assets")
async def get_assets(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    check_subscription(current_user)
    assets = db.query(Asset).filter(Asset.owner_username == current_user.username).order_by(Asset.id.desc()).all()
    return assets

@app.delete("/api/assets/{asset_id}")
async def delete_asset(asset_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    check_subscription(current_user)
    db.query(Asset).filter(Asset.id == asset_id, Asset.owner_username == current_user.username).delete()
    log_audit(current_user.username, f"Varlık silindi (ID: {asset_id})")
    db.commit()
    return {"message": "Varlık başarıyla silindi."}

@app.get("/api/logs")
async def get_logs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.username == current_user.username).order_by(AuditLog.id.desc()).limit(5).all()
    return [{"id": l.id, "username": l.username, "action": l.action, "timestamp": l.timestamp} for l in logs]

# --- DOĞRULAMA ---
@app.post("/api/verify-domain")
async def verify_domain_access(verify_req: dict, current_user = Depends(get_current_user)):
    raw_domain = verify_req.get("domain", "").strip()
    if not raw_domain: raise HTTPException(status_code=400, detail="URL gerekli.")
    domain = re.sub(r'^https?://', '', raw_domain).rstrip('/')
    verification_token = secrets.token_hex(8)
    verify_url = f"https://{domain}/.well-known/cyber-guard-verify.txt"
    try:
        resp = requests.get(verify_url, timeout=5, verify=False)
        if resp.status_code == 200 and resp.text.strip() == verification_token:
            log_audit(current_user.username, f"Varlık sahipliği doğrulandı: {domain}")
            return {"status": "verified", "message": f"'{domain}' sahipliği başarıyla doğrulandı!", "owner": current_user.username}
    except Exception as e: pass
    raise HTTPException(status_code=403, detail=f"⚠️ Doğrulama dosyası bulunamadı!\n\nSahipliği doğrulamak için lütfen sitenize aşağıdaki dosyayı ekleyin:\n\nDosya Yolu: /.well-known/cyber-guard-verify.txt\nDosya İçeriği: {verification_token}\n\n(Dosyayı ekledikten sonra tekrar 'Sahipliği Doğrula' butonuna basın).")

# --- PDF ---
@app.get("/api/report")
async def download_report(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assets = db.query(Asset).filter(Asset.owner_username == current_user.username).order_by(Asset.id.desc()).all()
    logs = db.query(AuditLog).filter(AuditLog.username == current_user.username).order_by(AuditLog.id.desc()).limit(5).all()
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(font_path): font_path = "./DejaVuSans.ttf"
    if os.path.exists(font_path): pdfmetrics.registerFont(TTFont('DejaVu', font_path)); turkce_font = 'DejaVu'
    else: turkce_font = 'Helvetica'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], textColor=colors.HexColor('#00ff88'), fontSize=20, spaceAfter=10, fontName=turkce_font)
    story.append(Paragraph("AEGISMATRIX - Varlık Güvenlik Raporu", title_style))
    story.append(Paragraph(f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle(name='Normal', parent=styles['Normal'], fontName=turkce_font)))
    story.append(Paragraph(f"Müşteri / Kullanıcı: {current_user.username}", ParagraphStyle(name='Normal', parent=styles['Normal'], fontName=turkce_font)))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Kayıtlı Varlıklar ve Risk Skorları", ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName=turkce_font)))
    data = [["ID", "URL", "Durum", "Risk", "SSL", "Headers"]]
    for a in assets: data.append([str(a.id), a.url, a.status, a.risk_score, f"{a.ssl_expiry_days}gün" if a.ssl_expiry_days>=0 else "N/A", a.security_headers_status])
    table = Table(data, colWidths=[1*cm, 5*cm, 2*cm, 2*cm, 2*cm, 3*cm])
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#171b2b')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,-1), turkce_font)]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Son Gerçekleşen İşlemler (Logs)", ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName=turkce_font)))
    log_text = "".join([f"{l.timestamp} - {l.action}\n" for l in logs])
    story.append(Paragraph(log_text, ParagraphStyle(name='Normal', parent=styles['Normal'], fontName=turkce_font)))
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=aegismatrix_raporu_{datetime.now().strftime('%Y%m%d')}.pdf"})

# --- MODÜL 8: ZAMANLAYICI (DEEP SCAN İLE BÜTÜNLEŞTİRİLDİ) ---
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def scheduled_scan():
    print(f"🔁 [Scheduler] Derin tarama döngüsü başlatılıyor: {datetime.now()}")
    db = SessionLocal()
    try:
        all_assets = db.query(Asset).all()
        if not all_assets: return
        for asset in all_assets:
            scan_result = deep_scan_url(asset.url)
            asset.status = scan_result["status"]
            asset.risk_score = scan_result["risk_score"]
            asset.ssl_expiry_days = scan_result["ssl_days"]
            asset.security_headers_status = scan_result["headers_status"]
            asset.open_ports = scan_result["open_ports"]
        db.commit()
        print(f"✅ [Scheduler] {len(all_assets)} varlık derin tarandı ve güncellendi.")
        log_audit("System", f"Otomatik derin tarama çalıştı: {len(all_assets)} varlık.")
    except Exception as e:
        db.rollback()
        print(f"❌ [Scheduler] Tarama sırasında hata: {e}")
        log_audit("System", f"Otomatik tarama hatası: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_scan, trigger=IntervalTrigger(minutes=10), id='auto_scan_job', replace_existing=True, misfire_grace_time=30)
    scheduler.start()
    print("✅ [Modül 8] Otomatik Tarama Zamanlayıcısı (Derin) başlatıldı! (Her 10 dakikada bir)")

@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123")))
        db.commit()
        print("✅ Kullanıcı oluşturuldu: admin / admin123")
    db.close()
