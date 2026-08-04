import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AEGISMATRIX CyberGuard Enterprise"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CyberGuard_Enterprise_Super_Secret_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cyber_guard.db")
    
    # YENİ EKLENENLER
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:5000")
    
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.mailtrap.io")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 2525))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASS: str = os.getenv("EMAIL_PASS", "")

settings = Settings()
