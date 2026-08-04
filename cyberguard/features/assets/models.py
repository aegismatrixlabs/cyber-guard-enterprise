from sqlalchemy import Column, Integer, String, ForeignKey
from cyberguard.core.database import Base

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
