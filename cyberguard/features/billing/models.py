from sqlalchemy import Column, Integer, String, ForeignKey
from cyberguard.core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), unique=True)
    plan_name = Column(String)
    status = Column(String, default="INACTIVE")
    expires_at = Column(String)
