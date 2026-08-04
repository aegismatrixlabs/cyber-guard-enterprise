from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from cyberguard.core.database import engine, Base, SessionLocal
from cyberguard.core.auth import get_password_hash
from cyberguard.features.users.models import User
from cyberguard.features.billing.models import Subscription
from cyberguard.features.users.api import router as users_router
from cyberguard.features.assets.api import router as assets_router
from cyberguard.features.billing.api import router as billing_router
from cyberguard.features.legal.api import router as legal_router
from cyberguard.features.reporting.api import router as reporting_router
from cyberguard.features.scheduler.tasks import start_scheduler
from cyberguard.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AEGISMATRIX CyberGuard Enterprise")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users_router, prefix="/auth", tags=["Authentication"])
app.include_router(assets_router, prefix="/api", tags=["Assets"])
app.include_router(billing_router, prefix="/api", tags=["Billing"])
app.include_router(legal_router, prefix="/api", tags=["Legal Shield"])
app.include_router(reporting_router, prefix="/api", tags=["Reporting"])

@app.get("/", response_class=HTMLResponse)
async def root(): return HTMLResponse(content=open("templates/login.html", "r", encoding="utf-8").read())

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(): return RedirectResponse(url="/dashboard/home")

@app.get("/dashboard/{page:path}", response_class=HTMLResponse)
async def dashboard_page(page: str):
    # Ana tasarımı (Layout) ve istenen sayfayı birleştirip gönder.
    layout_html = open("templates/dashboard_layout.html", "r", encoding="utf-8").read()
    
    if not page or page == "/":
        page = "home"
    
    try:
        content_html = open(f"templates/dashboard/{page}.html", "r", encoding="utf-8").read()
    except FileNotFoundError:
        content_html = "<div class='text-[#ff5252] p-6 text-center'>Sayfa bulunamadı!</div>"
    
    # Layout içindeki placeholder'ı (main-content) sayfa içeriği ile değiştir.
    final_html = layout_html.replace('<div id="main-content"></div>', f'<div id="main-content">{content_html}</div>')
    return HTMLResponse(content=final_html)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(): return HTMLResponse(content=open("templates/admin_dashboard.html", "r", encoding="utf-8").read())

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(): return HTMLResponse(content=open("templates/forgot_password.html", "r", encoding="utf-8").read())

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(): return HTMLResponse(content=open("templates/reset_password.html", "r", encoding="utf-8").read())

@app.get("/register", response_class=HTMLResponse)
async def register_page(): return HTMLResponse(content=open("templates/register.html", "r", encoding="utf-8").read())

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "superadmin").first():
        db.add(User(username="superadmin", email="superadmin@cyberguard.local", hashed_password=get_password_hash("super123"), is_super_admin=True))
        db.commit()
        print("✅ Süper Admin oluşturuldu: superadmin / super123")
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(username="admin", email="admin@cyberguard.local", hashed_password=get_password_hash("admin123"), is_super_admin=False)
        db.add(admin_user); db.commit()
        print("✅ Kullanıcı oluşturuldu: admin / admin123")
        db.add(Subscription(username="admin", plan_name="Pro", status="ACTIVE", expires_at=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        print("✅ Admin kullanıcısına otomatik lisans verildi.")
    db.close()
    start_scheduler()
