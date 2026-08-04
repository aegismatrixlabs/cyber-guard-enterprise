from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Subscription, Asset, AuditLog
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sadece Süper Admin'in erişebileceği bir yardımcı fonksiyon
def verify_super_admin(current_user):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Bu sayfaya erişim yetkiniz yok (Sadece Süper Admin).")

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
            "is_super_admin": u.is_super_admin,
            "license_status": sub.status if sub else "NONE"
        })
    return result

@router.put("/admin/users/{user_id}/license")
async def toggle_user_license(user_id: int, action: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    verify_super_admin(current_user)
    new_status = action.get("status")
    if new_status not in ["ACTIVE", "INACTIVE"]:
        raise HTTPException(status_code=400, detail="Geçersiz lisans durumu.")
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    
    if target_user.is_super_admin:
        raise HTTPException(status_code=400, detail="Süper Admin'in lisansı değiştirilemez.")

    sub = db.query(Subscription).filter(Subscription.username == target_user.username).first()
    if sub:
        sub.status = new_status
        sub.plan_name = "Pro" if new_status == "ACTIVE" else "None"
    else:
        new_sub = Subscription(username=target_user.username, plan_name="Pro", status=new_status, expires_at=(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.add(new_sub)

    # Denetim Logu ekle
    log = AuditLog(username=current_user.username, action=f"Admin, {target_user.username} kullanıcısının lisansını {new_status} yaptı.", timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(log)
    
    db.commit()
    return {"message": f"{target_user.username} lisansı {new_status} olarak güncellendi."}

@router.get("/admin/stats")
async def get_system_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    verify_super_admin(current_user)
    total_users = db.query(User).count()
    total_assets = db.query(Asset).count()
    active_licenses = db.query(Subscription).filter(Subscription.status == "ACTIVE").count()
    return {"total_users": total_users, "total_assets": total_assets, "active_licenses": active_licenses}
