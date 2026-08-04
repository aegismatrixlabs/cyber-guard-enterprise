from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from cyberguard.core.database import SessionLocal
from cyberguard.features.users.models import User
from cyberguard.features.billing.models import Subscription
from cyberguard.core.auth import get_current_user
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def verify_super_admin(current_user):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Sadece Süper Admin erişebilir.")

@router.get("/admin/users")
async def get_all_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    verify_super_admin(current_user)
    users = db.query(User).all()
    result = []
    for u in users:
        sub = db.query(Subscription).filter(Subscription.username == u.username).first()
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_super_admin": u.is_super_admin,
            "license_status": sub.status if sub else "NONE",
            "last_login": u.last_login,
            "last_ip": u.last_ip
        })
    return result

@router.put("/admin/users/{user_id}/license")
async def toggle_user_license(user_id: int, action: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    verify_super_admin(current_user)
    new_status = action.get("status")
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user: raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    if target_user.is_super_admin: raise HTTPException(status_code=400, detail="Süper Admin lisansı değiştirilemez.")
    sub = db.query(Subscription).filter(Subscription.username == target_user.username).first()
    if sub:
        sub.status = new_status
        sub.plan_name = "Pro" if new_status == "ACTIVE" else "None"
    else:
        db.add(Subscription(username=target_user.username, plan_name="Pro", status=new_status, expires_at=(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    db.commit()
    return {"message": f"{target_user.username} lisansı {new_status} olarak güncellendi."}

@router.get("/admin/stats")
async def get_system_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    verify_super_admin(current_user)
    return {
        "total_users": db.query(User).count(),
        "total_assets": db.query(Asset).count(),
        "active_licenses": db.query(Subscription).filter(Subscription.status == "ACTIVE").count()
    }
