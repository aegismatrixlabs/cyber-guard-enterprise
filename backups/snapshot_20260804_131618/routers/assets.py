from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Asset, AuditLog
from schemas import AssetCreate
from routers.auth import get_current_user
from routers.billing import check_subscription  # Sihirli abonelik kontrol fonksiyonu
from datetime import datetime
import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def scan_url(url: str):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "ACTIVE", "LOW"
        else:
            return "INACTIVE", "HIGH"
    except requests.exceptions.RequestException:
        return "INACTIVE", "HIGH"

@router.post("/assets")
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # --- 4. MODÜL DEVREDE: Önce aboneliği kontrol et ---
    check_subscription(current_user) 
    # Eğer abonelik yoksa yukarıdaki satır 402 Hatası fırlatır ve kod buraya asla ulaşmaz!

    durum, risk_skoru = scan_url(asset.url)
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_asset = Asset(url=asset.url, status=durum, risk_score=risk_skoru, created_at=zaman, owner_username=current_user.username)
    db.add(new_asset)
    
    audit_log = AuditLog(username=current_user.username, action=f"Yeni varlık tarandı: {asset.url} (Lisanslı)", timestamp=zaman)
    db.add(audit_log)
    
    db.commit()
    db.refresh(new_asset)

    return {"message": f"'{asset.url}' tarandı.", "status": durum, "risk_score": risk_skoru}

@router.get("/assets")
async def get_assets(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Listeleme modülünde de abonelik kontrolü yapalım
    check_subscription(current_user)

    assets = db.query(Asset).filter(Asset.owner_username == current_user.username).order_by(Asset.id.desc()).all()
    return [{"id": a.id, "url": a.url, "status": a.status, "risk_score": a.risk_score, "created_at": a.created_at} for a in assets]
