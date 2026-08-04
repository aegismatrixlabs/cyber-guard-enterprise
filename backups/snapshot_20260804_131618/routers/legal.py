from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routers.auth import get_current_user
import sqlite3

router = APIRouter()

# Doğrulama için gelen veri modeli
class DomainVerifyRequest(BaseModel):
    domain: str

# --- VARLIK SAHİPLİĞİ DOĞRULAMA VE KAYIT ---
@router.post("/verify-domain")
async def verify_domain_access(verify_req: DomainVerifyRequest, current_user = Depends(get_current_user)):
    """
    Bir domainin kullanıcıya ait olup olmadığını doğrular.
    (Gerçek hayatta DNS TXT kaydı kontrolü veya belirli bir dosyanın sunucuda var olup olmadığına bakılır.)
    """
    
    # Demo amacıyla, sistemin sahiplik doğrulamasını geçmesi için URL'nin sonuna 'cyberguard' eklenmesini istiyoruz.
    # Örneğin: https://github.com/cyberguard
    if not verify_req.domain.endswith("/cyberguard") and "cyberguard" not in verify_req.domain:
        raise HTTPException(status_code=403, detail="Hukuki Koruma (Legal Shield): Bu varlık size ait değil! (Doğrulama token'ı eksik)")
    
    # Doğrulama başarılıysa bir mesaj dön
    return {"status": "verified", "message": f"'{verify_req.domain}' sahipliği doğrulandı, taramaya izin veriliyor.", "owner": current_user.username}
