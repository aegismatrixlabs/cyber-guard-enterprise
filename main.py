from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List
from datetime import datetime
import time
import uvicorn

app = FastAPI(
    title="AegisMatrix Core Security API - Hardened Production Module",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# CORS ve Güvenlik Sıkılaştırma Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aegismatrixlabs.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

fake_users_db = {}
fake_assets_db = []
fake_scans_db = []
fake_roe_approvals = {}
fake_cloud_audit_results = []
fake_reports_db = []

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

class CloudAuditModel(BaseModel):
    provider: str
    read_only_role_arn: str

class ReportExportModel(BaseModel):
    report_type: str
    reference_id: int

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

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

@app.post("/api/cloud/audit", status_code=status.HTTP_200_OK)
async def audit_cloud_environment(payload: CloudAuditModel):
    roe_checked = fake_roe_approvals.get("default_user@aegismatrixlabs.com")
    if not roe_checked or not roe_checked.get("roe_accepted", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Güvenlik İhlali: Bulut denetimi başlatmadan önce RoE sözleşmesini onaylamalısınız."
        )
        
    audit_findings = {
        "audit_id": len(fake_cloud_audit_results) + 1,
        "provider": payload.provider.upper(),
        "role_arn": payload.read_only_role_arn,
        "status": "COMPLETED",
        "timestamp": datetime.utcnow().isoformat(),
        "misconfigurations_detected": [
            {"resource": "S3-Bucket-Data-Store", "severity": "HIGH", "issue": "Public read permissions enabled."}
        ]
    }
    fake_cloud_audit_results.append(audit_findings)
    return {"success": True, **audit_findings}

def run_background_scan(scan_id: int, target: str):
    for scan in fake_scans_db:
        if scan["scan_id"] == scan_id:
            scan["status"] = "running"
            time.sleep(1)
            scan["status"] = "completed"
            scan["vulnerabilities_found"] = 1
            break

@app.post("/api/scans", status_code=status.HTTP_202_ACCEPTED)
async def create_scan(request: Request, payload: Dict[Any, Any], background_tasks: BackgroundTasks):
    roe_checked = fake_roe_approvals.get("default_user@aegismatrixlabs.com")
    if not roe_checked or not roe_checked.get("roe_accepted", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RoE gerekli.")
    scan_id = len(fake_scans_db) + 1
    target = payload.get("target", "unknown")
    new_scan = {"scan_id": scan_id, "target": target, "status": "queued", **payload}
    fake_scans_db.append(new_scan)
    background_tasks.add_task(run_background_scan, scan_id, target)
    return {"success": True, "scan_id": scan_id, "status": "queued"}

@app.post("/api/reports/export", status_code=status.HTTP_201_CREATED)
async def export_security_report(payload: ReportExportModel):
    roe_checked = fake_roe_approvals.get("default_user@aegismatrixlabs.com")
    if not roe_checked or not roe_checked.get("roe_accepted", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RoE gerekli.")
        
    report_id = len(fake_reports_db) + 1
    report_document = {
        "report_id": report_id,
        "company": "AegisMatrix Labs",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "READY_FOR_DOWNLOAD"
    }
    fake_reports_db.append(report_document)
    return {"success": True, **report_document}

@app.get("/api/pages/about", status_code=status.HTTP_200_OK)
async def get_about_page():
    return {
        "success": True,
        "company": "AegisMatrix Labs",
        "domain": "aegismatrixlabs.com",
        "official_contact_email": "aegismatrixlabs@gmail.com",
        "mission": "Next-Gen Autonomous SOC and Cyber Intelligence Framework."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
