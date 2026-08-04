from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from cyberguard.core.database import get_db
from cyberguard.core.auth import get_current_user
from cyberguard.features.users.models import User
from cyberguard.features.billing.models import Subscription

router = APIRouter()

@router.post("/subscription/activate")
async def activate_subscription(plan: str = "Pro", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_super_admin: return {"message": "Süper Admin aboneliği gerektirmez."}
    existing = db.query(Subscription).filter(Subscription.username == current_user.username).first()
    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    if existing:
        existing.plan_name, existing.status, existing.expires_at = plan, "ACTIVE", expires_at
    else:
        db.add(Subscription(username=current_user.username, plan_name=plan, status="ACTIVE", expires_at=expires_at))
    db.commit()
    return {"message": f"{plan} plan aboneliği aktifleştirildi!"}
