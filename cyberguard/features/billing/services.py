from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from cyberguard.core.database import SessionLocal
from cyberguard.features.billing.models import Subscription

def check_subscription(current_user):
    if current_user.is_super_admin: return True
    db = SessionLocal()
    sub = db.query(Subscription).filter(Subscription.username == current_user.username).first()
    db.close()
    if not sub or sub.status != "ACTIVE":
        raise HTTPException(status_code=402, detail="Ticari Lisans Kapısı: Aboneliğiniz aktif değil.")
    return True

# Yeni eklenen: Kayıt olan kullanıcıya otomatik lisans verir
def create_free_trial(db: Session, username: str):
    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    db.add(Subscription(username=username, plan_name="Free Trial", status="ACTIVE", expires_at=expires_at))
    db.commit()
