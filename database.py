from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger("CyberGuardDB")

# PostgreSQL bağlantı dizesi (Environment üzerinden alınır, yoksa yerel varsayılan kullanılır)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/cyberguard_db"
)

try:
    # Bağlantı kopmalarına karşı pool_pre_ping aktif edildi
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("PostgreSQL veritabanı motoru başarıyla yapılandırıldı.")
except Exception as e:
    logger.critical(f"Veritabanı motoru başlatılamadı: {str(e)}")
    raise e

def get_db():
    """
    Her istek için güvenli bir veritabanı oturumu açar ve işlem bitince kapatır.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Veritabanı oturum hatası: {str(e)}")
        raise e
    finally:
        db.close()
