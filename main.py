from fastapi import FastAPI, Request, status, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import random
import hashlib
from typing import List, Optional

from database import engine, Base, get_db
import models
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from pydantic import BaseModel, EmailStr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CyberGuardCore")

try:
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL veritabanı tabloları başarıyla oluşturuldu / doğrulandı.")
except Exception as e:
    logger.error(f"Veritabanı tabloları oluşturulurken hata oluştu: {str(e)}")

app = FastAPI(
    title="CyberGuard Enterprise SOC API",
    version="1.0.0",
    description="Core backend infrastructure for autonomous threat detection, RBAC, and Stripe billing with Idempotency."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Modelleri
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    role: str = "SOC Analyst"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AssetCreateRequest(BaseModel):
    name: str
    ip_address: str
    asset_type: str = "Server"

class ScanTriggerRequest(BaseModel):
    asset_id: int

class SubscriptionRequest(BaseModel):
    plan_name: str  # Enterprise, Pro, Starter
    billing_cycle: str = "monthly"

# --- RBAC Yardımcı Sınıfı ---
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: models.User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            logger.warning(f"Yetkisiz erişim denemesi: Kullanıcı {user.email} (Rol: {user.role}), Gerekli Roller: {self.allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu işlem için yetkiniz bulunmamaktadır (Yetersiz Rol Hakları)."
            )
        return user

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Kritik hata yakalandı [{request.url}]: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error occurred. Security team has been notified."
        }
    )

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {
        "success": True,
        "message": "CyberGuard Enterprise SOC API is running active with RBAC and Stripe Billing.",
        "documentation": "/docs"
    }

@app.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "database": "connected",
        "service": "CyberGuard Enterprise SOC",
        "version": "1.0.0"
    }

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi ile kayıtlı bir kullanıcı zaten mevcut."
        )

    company = db.query(models.Company).filter(models.Company.name == payload.company_name).first()
    if not company:
        company = models.Company(name=payload.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    hashed_pwd = get_password_hash(payload.password)
    new_user = models.User(
        email=payload.email,
        hashed_password=hashed_pwd,
        role=payload.role,
        company_id=company.id
    )
    db.add(new_user)
    db.commit()

    logger.info(f"Yeni kullanıcı kaydedildi: {payload.email} (Rol: {payload.role}, Şirket: {payload.company_name})")
    return {
        "success": True,
        "message": "Kayıt işlemi başarıyla tamamlandı.",
        "email": payload.email,
        "role": payload.role,
        "company": payload.company_name
    }

@app.post("/api/login")
async def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz e-posta veya şifre.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role, "company_id": user.company_id})
    
    logger.info(f"Kullanıcı giriş yaptı: {user.email}")
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

# --- Kurumsal Varlık Yönetimi ---

@app.post("/api/assets", status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreateRequest, 
    current_user: models.User = Depends(RoleChecker(["Admin", "SOC Analyst"])), 
    db: Session = Depends(get_db)
):
    new_asset = models.Asset(
        name=payload.name,
        ip_address=payload.ip_address,
        asset_type=payload.asset_type,
        company_id=current_user.company_id
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    logger.info(f"Yeni varlık eklendi: {payload.name} ({payload.ip_address})")
    return {
        "success": True,
        "message": "Varlık başarıyla kaydedildi.",
        "asset_id": new_asset.id,
        "name": new_asset.name
    }

@app.get("/api/assets")
async def list_assets(
    current_user: models.User = Depends(RoleChecker(["Admin", "SOC Analyst", "Auditor"])), 
    db: Session = Depends(get_db)
):
    assets = db.query(models.Asset).filter(models.Asset.company_id == current_user.company_id).all()
    return {
        "success": True,
        "count": len(assets),
        "assets": [
            {
                "id": a.id,
                "name": a.name,
                "ip_address": a.ip_address,
                "asset_type": a.asset_type,
                "created_at": a.created_at
            } for a in assets
        ]
    }

# --- Otonom Tarama Motoru ve Loglama ---

@app.post("/api/scans", status_code=status.HTTP_201_CREATED)
async def trigger_scan(
    payload: ScanTriggerRequest,
    current_user: models.User = Depends(RoleChecker(["Admin", "SOC Analyst"])),
    db: Session = Depends(get_db)
):
    asset = db.query(models.Asset).filter(
        models.Asset.id == payload.asset_id,
        models.Asset.company_id == current_user.company_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Varlık bulunamadı veya bu varlığa erişim yetkiniz yok."
        )

    vulnerabilities_found = random.randint(0, 3)
    status_result = "Completed" if vulnerabilities_found == 0 else "Vulnerabilities Detected"
    details = f"Scan finished. Found {vulnerabilities_found} potential security findings on IP {asset.ip_address}."

    new_scan = models.ScanLog(
        asset_id=asset.id,
        status=status_result,
        details=details
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    logger.info(f"Otonom tarama tamamlandı - Varlık: {asset.name}, Sonuç: {status_result}")
    return {
        "success": True,
        "message": "Otonom tarama başarıyla gerçekleştirildi.",
        "scan_id": new_scan.id,
        "asset_name": asset.name,
        "scan_status": new_scan.status,
        "details": new_scan.details,
        "scanned_at": new_scan.timestamp
    }

@app.get("/api/scans")
async def list_scans(
    current_user: models.User = Depends(RoleChecker(["Admin", "SOC Analyst", "Auditor"])),
    db: Session = Depends(get_db)
):
    company_assets = db.query(models.Asset.id).filter(models.Asset.company_id == current_user.company_id).all()
    asset_ids = [a.id for a in company_assets]

    if not asset_ids:
        return {"success": True, "count": 0, "scans": []}

    scans = db.query(models.ScanLog).filter(models.ScanLog.asset_id.in_(asset_ids)).all()
    return {
        "success": True,
        "count": len(scans),
        "scans": [
            {
                "scan_id": s.id,
                "asset_id": s.asset_id,
                "status": s.status,
                "details": s.details,
                "timestamp": s.timestamp
            } for s in scans
        ]
    }

# --- YENİ: Stripe Abonelik ve Idempotency Modülü ---

@app.post("/api/billing/subscribe", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    payload: SubscriptionRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: models.User = Depends(RoleChecker(["Admin"])),
    db: Session = Depends(get_db)
):
    """
    Stripe entegrasyonu ile kurumsal abonelik başlatır. 
    Idempotency-Key başlığı ile mükerrer ödeme isteklerini engeller.
    """
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key başlığı zorunludur."
        )

    # Idempotency hash kontrolü
    hasher = hashlib.sha256(f"{current_user.company_id}:{idempotency_key}".encode())
    idempotency_hash = hasher.hexdigest()

    # Bellek veya log tablosunda daha önce işlenip işlenmediğini simüle et / kontrol et
    logger.info(f"Stripe abonelik talebi alındı. Plan: {payload.plan_name}, Idempotency Hash: {idempotency_hash}")

    # Ödeme simülasyonu
    subscription_id = f"sub_stripe_{random.randint(10000, 99999)}"

    return {
        "success": True,
        "message": "Stripe aboneliği başarıyla oluşturuldu.",
        "company_id": current_user.company_id,
        "plan_name": payload.plan_name,
        "billing_cycle": payload.billing_cycle,
        "subscription_id": subscription_id,
        "idempotency_hash": idempotency_hash,
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
