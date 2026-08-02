from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List
from datetime import datetime
import uvicorn

app = FastAPI(title="AegisMatrix Core Security API - Enterprise Pages Module")

fake_users_db = {}
fake_assets_db = []
fake_scans_db = []
fake_roe_approvals = {}
fake_support_messages: List[Dict[Any, Any]] = []

class RegisterModel(BaseModel):
    email: str
    password: str

class LoginModel(BaseModel):
    email: str
    password: str

class RoeAcceptModel(BaseModel):
    accepted: bool
    full_name: str
    company_title: str

class ContactMessageModel(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(user: RegisterModel):
    if user.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi ile kayıtlı bir kullanıcı zaten mevcut."
        )
    fake_users_db[user.email] = user.password
    return {"success": True, "message": "Kayıt başarılı."}

@app.post("/api/login")
async def login(user: LoginModel):
    if user.email not in fake_users_db or fake_users_db[user.email] != user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz e-posta veya şifre."
        )
    return {"success": True, "access_token": "fake-jwt-token-aegismatrix"}

@app.get("/api/roe/status")
async def get_roe_status(email: str):
    approval = fake_roe_approvals.get(email)
    if not approval:
        return {"success": True, "roe_accepted": False, "message": "RoE sözleşmesi henüz onaylanmamış."}
    return {"success": True, "roe_accepted": True, "data": approval}

@app.post("/api/roe/accept", status_code=status.HTTP_200_OK)
async def accept_roe(request: Request, payload: RoeAcceptModel):
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    if not payload.accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sistemi kullanabilmek için Rules of Engagement (RoE) sözleşmesini kabul etmelisiniz."
        )
        
    approval_record = {
        "full_name": payload.full_name,
        "company_title": payload.company_title,
        "ip_address": client_ip,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "APPROVED"
    }
    
    fake_roe_approvals["default_user@aegismatrixlabs.com"] = approval_record
    
    return {
        "success": True,
        "message": "Rules of Engagement (RoE) yasal sözleşmesi başarıyla onaylandı.",
        **approval_record
    }

# --- Kurumsal Sayfalar & Resmi İletişim Entegrasyonu ---

@app.get("/api/pages/about", status_code=status.HTTP_200_OK)
async def get_about_page():
    return {
        "success": True,
        "company": "AegisMatrix Labs",
        "domain": "aegismatrixlabs.com",
        "official_contact_email": "aegismatrixlabs@gmail.com",
        "mission": "Next-Gen Autonomous SOC and Cyber Intelligence Framework.",
        "founded": "July 2026"
    }

@app.get("/api/pages/privacy", status_code=status.HTTP_200_OK)
async def get_privacy_policy():
    return {
        "success": True,
        "title": "Gizlilik Politikası ve Veri Güvenliği",
        "contact": "aegismatrixlabs@gmail.com",
        "details": "AegisMatrix Labs, müşteri verilerini ISO 27001 ve SOC 2 standartlarına uygun olarak şifreler ve izole eder."
    }

@app.get("/api/pages/help", status_code=status.HTTP_200_OK)
async def get_help_center():
    return {
        "success": True,
        "support_email": "aegismatrixlabs@gmail.com",
        "documentation_url": "https://aegismatrixlabs.com/docs",
        "faq": [
            {"q": "Varlık doğrulama nasıl yapılır?", "a": "DNS TXT veya HTTP dosya doğrulaması ile."},
            {"q": "Tarama başlatma şartları nelerdir?", "a": "Rules of Engagement (RoE) onaylanmalıdır."}
        ]
    }

@app.post("/api/pages/contact", status_code=status.HTTP_201_CREATED)
async def submit_contact_message(payload: ContactMessageModel):
    message_entry = {
        "id": len(fake_support_messages) + 1,
        "name": payload.name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "target_inbox": "aegismatrixlabs@gmail.com",
        "timestamp": datetime.utcnow().isoformat()
    }
    fake_support_messages.append(message_entry)
    return {
        "success": True,
        "message": "Destek talebiniz başarıyla alınmıştır. Talebiniz doğrudan aegismatrixlabs@gmail.com adresine yönlendirilmiştir.",
        "ticket_id": message_entry["id"]
    }

@app.post("/api/scans", status_code=status.HTTP_201_CREATED)
async def create_scan(request: Request, payload: Dict[Any, Any]):
    roe_checked = fake_roe_approvals.get("default_user@aegismatrixlabs.com")
    if not roe_checked or not roe_checked.get("roe_accepted", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Güvenlik İhlali: Tarama başlatmadan önce Rules of Engagement (RoE) sözleşmesini imzalamalısınız."
        )
        
    scan_id = len(fake_scans_db) + 1
    new_scan = {"scan_id": scan_id, "status": "initiated", **payload}
    fake_scans_db.append(new_scan)
    return {"success": True, "message": "Otonom tarama başarıyla başlatıldı.", **new_scan}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
