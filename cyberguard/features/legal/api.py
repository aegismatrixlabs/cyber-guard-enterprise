from fastapi import APIRouter, Depends, HTTPException
from cyberguard.core.auth import get_current_user
from cyberguard.features.users.models import User
import secrets
import requests
import re

router = APIRouter()

@router.post("/verify-domain")
async def verify_domain_access(verify_req: dict, current_user: User = Depends(get_current_user)):
    raw_domain = verify_req.get("domain", "").strip()
    if not raw_domain: raise HTTPException(status_code=400, detail="URL gerekli.")
    domain = re.sub(r'^https?://', '', raw_domain).rstrip('/')
    verification_token = secrets.token_hex(8)
    verify_url = f"https://{domain}/.well-known/cyber-guard-verify.txt"
    try:
        resp = requests.get(verify_url, timeout=5, verify=False)
        if resp.status_code == 200 and resp.text.strip() == verification_token:
            return {"status": "verified", "message": f"'{domain}' sahipliği başarıyla doğrulandı!"}
    except: pass
    raise HTTPException(status_code=403, detail=f"⚠️ Doğrulama dosyası bulunamadı! Dosya Yolu: /.well-known/cyber-guard-verify.txt Dosya İçeriği: {verification_token}")
