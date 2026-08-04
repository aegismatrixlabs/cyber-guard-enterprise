from cyberguard.core.database import SessionLocal
from cyberguard.features.assets.models import Asset
from cyberguard.features.assets.services import deep_scan_url
from cyberguard.features.billing.models import Subscription
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# 1. Her 10 dakikada bir yapılan Derin Tarama
def scheduled_scan():
    print(f"🔁 [Scheduler] Derin tarama başlatılıyor...")
    db = SessionLocal()
    try:
        all_assets = db.query(Asset).all()
        if not all_assets: return
        for asset in all_assets:
            scan_result = deep_scan_url(asset.url)
            asset.status, asset.risk_score, asset.ssl_expiry_days, asset.security_headers_status, asset.open_ports = (
                scan_result["status"], scan_result["risk_score"], scan_result["ssl_days"],
                scan_result["headers_status"], scan_result["open_ports"]
            )
        db.commit()
        print(f"✅ [Scheduler] {len(all_assets)} varlık tarandı.")
    except Exception as e: print(f"❌ [Scheduler] Hata: {e}")
    finally: db.close()

# 2. Her gece 00:00'da çalışacak Lisans Bitiş Kontrolü (YENİ)
def check_expired_licenses():
    print(f"⏰ [Scheduler] Lisans bitiş kontrolü başlatılıyor: {datetime.now()}")
    db = SessionLocal()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Süresi dolan lisansları bul ve INACTIVE yap
        expired_subs = db.query(Subscription).filter(Subscription.expires_at <= now_str, Subscription.status == "ACTIVE").all()
        for sub in expired_subs:
            sub.status = "INACTIVE"
            print(f"⛔ [Scheduler] Kullanıcı '{sub.username}' lisansı süresi dolduğu için INACTIVE yapıldı.")
        db.commit()
        print(f"✅ [Scheduler] Lisans kontrolü tamamlandı. {len(expired_subs)} lisans pasifleştirildi.")
    except Exception as e: print(f"❌ [Scheduler] Lisans kontrolü hatası: {e}")
    finally: db.close()

# Zamanlayıcıyı başlatan fonksiyon
def start_scheduler():
    scheduler = BackgroundScheduler()
    # 10 dakikada bir çalışan tarama
    scheduler.add_job(scheduled_scan, trigger=IntervalTrigger(minutes=10), id='auto_scan_job', replace_existing=True)
    # Her gece 00:00'da çalışan lisans bitiş kontrolü
    scheduler.add_job(check_expired_licenses, trigger=CronTrigger(hour=0, minute=0), id='expiry_check_job', replace_existing=True)
    scheduler.start()
    print("✅ [Scheduler] Zamanlayıcı başlatıldı! (Tarama: 10 dk, Lisans Kontrolü: Her gece 00:00)")
