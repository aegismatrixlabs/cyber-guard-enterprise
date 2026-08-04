from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from cyberguard.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(String)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(String, nullable=True)
    last_login = Column(String, nullable=True)
    last_ip = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    action = Column(String)
    timestamp = Column(String)
