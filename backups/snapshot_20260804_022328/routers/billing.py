from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Subscription, AuditLog
from routers.auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- YENİ ABONELİK BAŞLATMA (Demo) ---
@router.post("/subscription/activate")
async def activate_subscription(plan: str = "Pro", db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Aboneliği kontrol et, varsa güncelle, yoksa oluştur
    existing = db.query(Subscription).filter(Subscription.username == current_user.username).first()
    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    
    if existing:
        existing.plan_name = plan
        existing.status = "ACTIVE"
        existing.expires_at = expires_at
    else:
        new_sub = Subscription(username=current_user.username, plan_name=plan, status="ACTIVE", expires_at=expires_at)
        db.add(new_sub)
    
    # Audit Log
    log = AuditLog(username=current_user.username, action=f"Abonelik aktifleştirildi: {plan} (30 gün)", timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(log)
    
    db.commit()
    return {"message": f"{plan} plan aboneliği aktifleştirildi! 30 gün boyunca tarama yapabilirsiniz.", "expires_at": expires_at}

# --- ABONELİK DURUMU KONTROLÜ ---
def check_subscription(current_user):
    db = SessionLocal()
    sub = db.query(Subscription).filter(Subscription.username == current_user.username).first()
    db.close()
    
    if not sub or sub.status != "ACTIVE":
        raise HTTPException(status_code=402, detail="Ticari Lisans Kapısı: Aboneliğiniz aktif değil. Lütfen bir plan satın alın (402 Payment Required).")
    return True
