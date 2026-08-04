from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_super_admin = Column(Boolean, default=False) # Yeni alan

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    status = Column(String, default="PENDING")
    risk_score = Column(String, default="PENDING")
    ssl_expiry_days = Column(Integer, default=-1)
    security_headers_status = Column(String, default="N/A")
    open_ports = Column(String, default="N/A")
    created_at = Column(String)
    owner_username = Column(String, ForeignKey("users.username"))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    action = Column(String)
    timestamp = Column(String)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), unique=True)
    plan_name = Column(String)
    status = Column(String, default="INACTIVE")
    expires_at = Column(String)
