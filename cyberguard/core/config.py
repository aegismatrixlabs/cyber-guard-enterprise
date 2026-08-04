import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AEGISMATRIX CyberGuard Enterprise"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CyberGuard_Enterprise_Super_Secret_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./cyber_guard.db"
    
    # SMTP Ayarları (Mail için gerekli olan kısım)
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASS: str = os.getenv("EMAIL_PASS", "")

settings = Settings()
