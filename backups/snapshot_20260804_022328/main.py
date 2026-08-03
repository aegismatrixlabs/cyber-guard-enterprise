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

# --- PDF İÇİN REPORTLAB KÜTÜPHANELERİ ---
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

# --- JWT GÜVENLİK AYARLARI ---
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
        raise HTTPException(status_code=402, detail="Ticari Lisans Kapısı: Aboneliğiniz aktif değil. Lütfen bir plan satın alın.")
    return True

def log_audit(username: str, action: str):
    db = SessionLocal()
    log = AuditLog(username=username, action=action, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(log); db.commit(); db.close()

# --- ROTALAR ---
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/login.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

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

def scan_url(url: str):
    try:
        r = requests.get(url, timeout=5)
        return ("ACTIVE", "LOW") if r.status_code == 200 else ("INACTIVE", "HIGH")
    except: return ("INACTIVE", "HIGH")

@app.post("/api/assets")
async def create_asset(asset: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    check_subscription(current_user)
    durum, skor = scan_url(asset.get("url"))
    new_asset = Asset(url=asset.get("url"), status=durum, risk_score=skor, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), owner_username=current_user.username)
    db.add(new_asset)
    log_audit(current_user.username, f"Varlık tarandı: {asset.get('url')}")
    db.commit(); db.refresh(new_asset)
    return {"message": f"'{asset.get('url')}' tarandı.", "status": durum, "risk_score": skor}

@app.get("/api/assets")
async def get_assets(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    check_subscription(current_user)
    assets = db.query(Asset).filter(Asset.owner_username == current_user.username).order_by(Asset.id.desc()).all()
    return [{"id": a.id, "url": a.url, "status": a.status, "risk_score": a.risk_score, "created_at": a.created_at} for a in assets]

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

# --- YENİ DOĞRULAMA SİSTEMİ (DOSYA TABANLI) ---
@app.post("/api/verify-domain")
async def verify_domain_access(verify_req: dict, current_user = Depends(get_current_user)):
    raw_domain = verify_req.get("domain", "").strip()
    if not raw_domain: raise HTTPException(status_code=400, detail="URL gerekli.")
    
    # URL'yi normallleştir (Protokolü ve sonda '/' işaretini kaldır)
    domain = re.sub(r'^https?://', '', raw_domain).rstrip('/')
    
    # 16 haneli rastgele güvenli bir doğrulama kodu üret
    verification_token = secrets.token_hex(8)
    
    # Doğrulama dosyasını kontrol et (.well-known dizini standarttır)
    verify_url = f"https://{domain}/.well-known/cyber-guard-verify.txt"
    try:
        # SSL doğrulamasını geçici olarak kapatıyoruz (wsl sorunları için)
        resp = requests.get(verify_url, timeout=5, verify=False)
        if resp.status_code == 200 and resp.text.strip() == verification_token:
            log_audit(current_user.username, f"Varlık sahipliği doğrulandı: {domain}")
            return {"status": "verified", "message": f"'{domain}' sahipliği başarıyla doğrulandı!", "owner": current_user.username}
    except Exception as e:
        pass # Doğrulama başarısız oldu, devam et ve talimatları göster
    
    # Doğrulama başarısız olduysa, müşteriye yapması gerekeni anlatan net bir talimat gönder
    raise HTTPException(
        status_code=403,
        detail=f"⚠️ Doğrulama dosyası bulunamadı!\n\nSahipliği doğrulamak için lütfen sitenize aşağıdaki dosyayı ekleyin:\n\nDosya Yolu: /.well-known/cyber-guard-verify.txt\nDosya İçeriği: {verification_token}\n\n(Dosyayı ekledikten sonra tekrar 'Sahipliği Doğrula' butonuna basın)."
    )

# --- TÜRKÇE DESTEKLİ PDF RAPORU ---
@app.get("/api/report")
async def download_report(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assets = db.query(Asset).filter(Asset.owner_username == current_user.username).order_by(Asset.id.desc()).all()
    logs = db.query(AuditLog).filter(AuditLog.username == current_user.username).order_by(AuditLog.id.desc()).limit(5).all()
    
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(font_path): font_path = "./DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        turkce_font = 'DejaVu'
    else:
        turkce_font = 'Helvetica'

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
    data = [["ID", "URL", "Durum", "Risk Skoru"]]
    for a in assets: data.append([str(a.id), a.url, a.status, a.risk_score])
    
    table = Table(data, colWidths=[1.5*cm, 9*cm, 2.5*cm, 2.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#171b2b')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), turkce_font), ('FONTNAME', (0,1), (-1,-1), turkce_font),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Son Gerçekleşen İşlemler (Logs)", ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName=turkce_font)))
    log_text = "".join([f"{l.timestamp} - {l.action}\n" for l in logs])
    story.append(Paragraph(log_text, ParagraphStyle(name='Normal', parent=styles['Normal'], fontName=turkce_font)))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=aegismatrix_raporu_{datetime.now().strftime('%Y%m%d')}.pdf"})

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123")))
        db.commit()
        print("✅ Kullanıcı oluşturuldu: admin / admin123")
    db.close()
