from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List
from datetime import datetime
import ipaddress
import uvicorn

app = FastAPI(title="AegisMatrix Core Security API - Legal Shield & Ownership Module")

fake_users_db = {}
fake_assets_db = []
fake_scans_db = []
fake_roe_approvals = {}
fake_verified_assets = set()

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

class AssetVerifyModel(BaseModel):
    target: str # Domain veya IP
    verification_method: str # DNS_TXT veya HTTP_FILE

class ScanModel(BaseModel):
    target: str

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(user: RegisterModel):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Kullanıcı zaten mevcut.")
    fake_users_db[user.email] = user.password
    return {"success": True, "message": "Kayıt başarılı."}

@app.post("/api/login")
async def login(user: LoginModel):
    if user.email not in fake_users_db or fake_users_db[user.email] != user.password:
        raise HTTPException(status_code=400, detail="Geçersiz kimlik bilgileri.")
    return {"success": True, "access_token": "fake-jwt-token"}

@app.post("/api/roe/accept", status_code=status.HTTP_200_OK)
async def accept_roe(payload: RoeAcceptModel):
    if not payload.accepted:
        raise HTTPException(status_code=400, detail="RoE kabul edilmelidir.")
    approval_record = {
        "full_name": payload.full_name,
        "company_title": payload.company_title,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "APPROVED"
    }
    fake_roe_approvals["default_user@aegismatrixlabs.com"] = approval_record
    return {"success": True, "message": "RoE onaylandı.", **approval_record}

# --- Yasal Kalkan 3.2: Kritik IP / Kara Liste Filtresi (.gov, .mil vb.) ---
def check_blacklisted_target(target: str):
    target_lower = target.lower()
    if target_lower.endswith(".gov") or target_lower.endswith(".mil") or ".gov." in target_lower or ".mil." in target_lower:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yasal Sınır İhlali: .gov ve .mil uzantılı kritik devlet/askeri varlıkların taranması kesinlikle yasaktır."
        )
    
    # IP tabanlı kara liste kontrolü
    try:
        ip = ipaddress.ip_address(target)
        if ip.is_loopback or ip.is_private:
            return # Lokal testlere izin ver
    except ValueError:
        pass

# --- Yasal Kalkan 3.1: DNS TXT & HTTP Sahiplik Doğrulama ---
@app.post("/api/assets/verify", status_code=status.HTTP_200_OK)
async def verify_asset_ownership(payload: AssetVerifyModel):
    check_blacklisted_target(payload.target)
    
    method = payload.verification_method.upper()
    if method not in ["DNS_TXT", "HTTP_FILE"]:
        raise HTTPException(status_code=400, detail="Geçersiz doğrulama yöntemi. 'DNS_TXT' veya 'HTTP_FILE' kullanın.")
        
    # Simüle edilmiş sahiplik doğrulama (Başarılı kabul edilir)
    fake_verified_assets.add(payload.target)
    
    return {
        "success": True,
        "target": payload.target,
        "verification_method": method,
        "status": "VERIFIED",
        "message": f"{payload.target} varlığının sahipliği {method} protokolü ile doğrulandı."
    }

# --- Otonom Tarama Motoru (Sahiplik ve Kara Liste Korumalı) ---
@app.post("/api/scans", status_code=status.HTTP_202_ACCEPTED)
async def create_scan(payload: ScanModel, background_tasks: BackgroundTasks):
    roe_checked = fake_roe_approvals.get("default_user@aegismatrixlabs.com")
    if not roe_checked or not roe_checked.get("roe_accepted", True):
        raise HTTPException(status_code=403, detail="Tarama başlatmak için RoE onaylanmalıdır.")
        
    target = payload.target
    
    # 1. Kara liste kontrolü
    check_blacklisted_target(target)
    
    # 2. Sahiplik doğrulama kontrolü
    if target not in fake_verified_assets and target not in ["127.0.0.1", "localhost"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yasal Kalkan İhlali: Bu varlığın sahipliği doğrulanmamıştır. Önce /api/assets/verify ile doğrulayın."
        )
        
    scan_id = len(fake_scans_db) + 1
    new_scan = {"scan_id": scan_id, "target": target, "status": "queued", "created_at": datetime.utcnow().isoformat()}
    fake_scans_db.append(new_scan)
    
    return {"success": True, "message": "Tarama kuyruğa eklendi.", "scan_id": scan_id}

@app.get("/api/pages/about", status_code=status.HTTP_200_OK)
async def get_about_page():
    return {"success": True, "company": "AegisMatrix Labs", "mission": "Autonomous SOC"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
