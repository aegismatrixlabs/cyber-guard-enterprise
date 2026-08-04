from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from cyberguard.core.database import get_db
from cyberguard.core.auth import get_current_user, create_access_token, verify_password, get_password_hash
from cyberguard.features.users.models import User
from cyberguard.features.users.schemas import Token, UserCreate, EmailRequest, ResetPasswordRequest, PasswordChangeRequest
from cyberguard.features.billing.services import create_free_trial
from cyberguard.features.users.email import send_reset_email

router = APIRouter()

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı veya email zaten kayıtlı.")
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(new_user)
    db.commit(); db.refresh(new_user)
    create_free_trial(db, new_user.username)
    return {"message": "Hesap başarıyla oluşturuldu! 30 günlük deneme lisansınız aktif edildi."}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email, "is_super_admin": current_user.is_super_admin}

@router.post("/forgot-password")
async def forgot_password(request: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return {"message": "Eğer bu e-posta ile kayıtlı bir hesap varsa, şifre sıfırlama talimatları gönderilmiştir."}
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    db.commit()
    if send_reset_email(user.email, token):
        return {"message": "Şifre sıfırlama bağlantısı e-postanıza gönderildi."}
    else:
        raise HTTPException(status_code=500, detail="E-posta gönderilirken bir hata oluştu.")

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Geçersiz veya kullanılmış token.")
    expiry = datetime.strptime(user.reset_token_expiry, "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expiry:
        raise HTTPException(status_code=400, detail="Token süresi dolmuş. Lütfen tekrar şifre sıfırlama isteği gönderin.")
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"message": "Şifreniz başarıyla sıfırlandı. Yeni şifrenizle giriş yapabilirsiniz."}

# --- DÜZELTİLEN ŞİFRE DEĞİŞTİRME ENDPOINT'İ ---
@router.put("/users/me/password")
async def change_password(data: PasswordChangeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Eski şifreniz hatalı.")
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Şifreniz başarıyla güncellendi."}
