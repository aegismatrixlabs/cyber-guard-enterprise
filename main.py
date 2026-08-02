from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

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
    description="Core backend infrastructure for autonomous threat detection and SOC operations."
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

    logger.info(f"Yeni kullanıcı kaydedildi: {payload.email} (Şirket: {payload.company_name})")
    return {
        "success": True,
        "message": "Kayıt işlemi başarıyla tamamlandı.",
        "email": payload.email,
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

# --- YENİ: Kurumsal Varlık Yönetimi (Asset Management) ---

@app.post("/api/assets", status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreateRequest, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Sadece giriş yapmış kullanıcıların, kendi şirketine ait varlık (sunucu/IP) eklemesini sağlar.
    """
    new_asset = models.Asset(
        name=payload.name,
        ip_address=payload.ip_address,
        asset_type=payload.asset_type,
        company_id=current_user.company_id
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    logger.info(f"Yeni varlık eklendi: {payload.name} ({payload.ip_address}) - Şirket ID: {current_user.company_id}")
    return {
        "success": True,
        "message": "Varlık başarıyla kaydedildi.",
        "asset_id": new_asset.id,
        "name": new_asset.name,
        "ip_address": new_asset.ip_address
    }

@app.get("/api/assets")
async def list_assets(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Giriş yapan kullanıcının şirketine ait tüm varlıkları listeler (Multi-tenancy izolasyonu).
    """
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
