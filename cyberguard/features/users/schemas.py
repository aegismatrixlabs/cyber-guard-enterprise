from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmailRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- YENİ EKLENEN ŞİFRE DEĞİŞTİRME MODELİ ---
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
