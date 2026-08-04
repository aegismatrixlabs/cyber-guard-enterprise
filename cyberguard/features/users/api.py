from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from cyberguard.core.database import get_db
from cyberguard.core.auth import get_current_user, create_access_token, verify_password, get_password_hash
from cyberguard.features.users.models import User
from cyberguard.features.users.schemas import Token, UserCreate, EmailRequest, ResetPasswordRequest, PasswordChangeRequest
from cyberguard.features.billing.services import create_free_trial
from cyberguard.features.users.email import send_verification_email, send_reset_email
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/register")
# # @limiter.limit("10/minute") # GECICI OLARAK DEVRE DISI # GECICI OLARAK DEVRE DISI  # Aynı IP'den 1 dakikada en fazla 5 kayıt
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı veya email zaten kayıtlı.")
    
    verification_token = secrets.token_urlsafe(32)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_verified=False,
        verification_token=verification_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Lisansı hemen verme! Doğrulama maili gönder.
    send_verification_email(new_user.email, verification_token)
    
    return {"message": "Hesap oluşturuldu! Lütfen e-posta adresinizi doğrulamak için gelen bağlantıya tıklayın."}

@router.get("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Geçersiz veya kullanılmış doğrulama token'ı.")
    
    if user.is_verified:
        return {"message": "Bu e-posta zaten doğrulanmış. Lütfen giriş yapın."}
    
    # Kullanıcıyı doğrula ve 30 günlük lisansı aktif et
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    # Şimdi lisansı ver
    create_free_trial(db, user.username)
    
    return {"message": "E-posta başarıyla doğrulandı! 30 günlük deneme lisansınız aktif edildi. Şimdi giriş yapabilirsiniz."}

@router.post("/token", response_model=Token)
# # @limiter.limit("10/minute") # GECICI OLARAK DEVRE DISI # GECICI OLARAK DEVRE DISI  # Aynı IP'den dakikada en fazla 10 giriş denemesi
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Hesabınız henüz doğrulanmamış. Lütfen e-posta adresinizi doğrulayın.")
    
    user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.commit()
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_super_admin": current_user.is_super_admin,
        "last_login": current_user.last_login,
        "last_ip": current_user.last_ip
    }

@router.post("/forgot-password")
async def forgot_password(request: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user: return {"message": "Eğer hesap varsa, talimatlar gönderildi."}
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    db.commit()
    if send_reset_email(user.email, token):
        return {"message": "Şifre sıfırlama bağlantısı gönderildi."}
    else: raise HTTPException(status_code=500, detail="E-posta hatası.")

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.token).first()
    if not user: raise HTTPException(status_code=400, detail="Geçersiz token.")
    expiry = datetime.strptime(user.reset_token_expiry, "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expiry: raise HTTPException(status_code=400, detail="Token süresi dolmuş.")
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"message": "Şifre sıfırlandı."}

@router.put("/users/me/password")
async def change_password(data: PasswordChangeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Eski şifreniz hatalı.")
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Şifre güncellendi."}

# --- EKSİK LOGLAR ENDPOINT'İ (DÜZELTME) ---
from cyberguard.features.users.models import AuditLog

