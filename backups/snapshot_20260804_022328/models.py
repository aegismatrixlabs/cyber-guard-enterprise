from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    status = Column(String, default="PENDING")
    risk_score = Column(String, default="PENDING")
    created_at = Column(String)
    owner_username = Column(String, ForeignKey("users.username"))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    action = Column(String)
    timestamp = Column(String)

# --- YENİ EKLENEN ABONELİK TABLOSU ---
class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), unique=True)
    plan_name = Column(String)  # Örnek: "Free", "Pro", "Enterprise"
    status = Column(String, default="INACTIVE") # ACTIVE veya INACTIVE
    expires_at = Column(String)
