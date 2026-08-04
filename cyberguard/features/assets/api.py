from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer
from cyberguard.core.database import get_db
from cyberguard.core.auth import get_current_user
from cyberguard.core.cache import get_cache
from cyberguard.features.users.models import User
from cyberguard.features.assets.models import Asset
from cyberguard.features.assets.services import deep_scan_url
from cyberguard.features.billing.services import check_subscription

router = APIRouter()

@router.post("/assets")
async def create_asset(asset: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_subscription(current_user)
    url = asset.get("url")
    scan_result = deep_scan_url(url)
    new_asset = Asset(
        url=url, status=scan_result["status"], risk_score=scan_result["risk_score"],
        ssl_expiry_days=scan_result["ssl_days"], security_headers_status=scan_result["headers_status"],
        open_ports=scan_result["open_ports"], created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        owner_username=current_user.username
    )
    db.add(new_asset)
    db.commit(); db.refresh(new_asset)
    return {"message": f"'{url}' tarandı.", "status": scan_result["status"], "risk_score": scan_result["risk_score"]}

@router.get("/assets")
async def get_assets(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    search: str = Query(None, description="Aranacak URL"),
    skip: int = Query(0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(10, description="Getirilecek kayıt sayısı")
):
    check_subscription(current_user)
    query = db.query(Asset).filter(Asset.owner_username == current_user.username)
    if search:
        query = query.filter(Asset.url.contains(search))
    total = query.count()
    assets = query.order_by(Asset.id.desc()).offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "items": assets}

@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_subscription(current_user)
    db.query(Asset).filter(Asset.id == asset_id, Asset.owner_username == current_user.username).delete()
    db.commit()
    return {"message": "Varlık başarıyla silindi."}

# --- REDIS İLE ÖNBELLEĞE ALINMIŞ İSTATİSTİKLER ---
@router.get("/assets/stats")
@cached(ttl=60, cache=Cache.REDIS, key_builder=lambda f, user: f"stats:{user.username}", serializer=JsonSerializer(), alias="default")
async def get_asset_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(Asset).filter(Asset.owner_username == current_user.username).count()
    active = db.query(Asset).filter(Asset.owner_username == current_user.username, Asset.status == "ACTIVE").count()
    return {"total": total, "active": active}

# --- LOGLARI ÇEKEN ENDPOINT (Doğru Router'a Taşındı) ---
from cyberguard.features.users.models import AuditLog

@router.get("/logs")
async def get_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.username == current_user.username).order_by(AuditLog.id.desc()).limit(5).all()
    return [{"id": l.id, "username": l.username, "action": l.action, "timestamp": l.timestamp} for l in logs]
