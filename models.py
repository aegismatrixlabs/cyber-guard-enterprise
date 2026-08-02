from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="company", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="SOC Analyst")  # Admin, SOC Analyst, Auditor
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    company = relationship("Company", back_populates="users")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ip_address = Column(String, index=True, nullable=False)
    asset_type = Column(String, default="Server")  # Server, Gateway, Cloud
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    company = relationship("Company", back_populates="assets")
    scans = relationship("ScanLog", back_populates="asset", cascade="all, delete-orphan")

class ScanLog(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    scan_type = Column(String, nullable=False)  # Vulnerability, Cloud Config, RCE Check
    status = Column(String, default="Completed")  # Pending, Running, Completed, Failed
    vulnerability_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    asset = relationship("Asset", back_populates="scans")
