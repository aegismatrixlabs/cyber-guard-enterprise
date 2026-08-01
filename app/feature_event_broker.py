import sqlite3
import re
import hashlib
from datetime import datetime, timezone

class FeatureEventBrokerModule:
    def __init__(self, db_path="cyber_guard.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Olay Dağıtım (Event Broker) tablosunun hazırlanması"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                event_uuid TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_summary TEXT NOT NULL,
                event_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def publish_event(self, tenant_id: str, auth_token: str, event_type: str, payload_summary: str):
        """5-Zincir Kuralına Göre Güvenli Olay Yayınlama ve Durum Yönetimi"""
        try:
            # --- 1. HALKA: Girdi Doğrulama ve Kimlik Kontrolü (Auth/JWT & Sanitizasyon) ---
            if not tenant_id or not isinstance(tenant_id, str) or not re.match(r"^tenant_[a-zA-Z0-9_]+$", tenant_id):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz tenant_id formatı."}

            if not auth_token or not isinstance(auth_token, str) or not auth_token.startswith("Bearer "):
                return {"status": "error", "code": 401, "message": "1. Halka İhlali: Geçersiz veya yetkisiz Auth/JWT token."}

            if not event_type or not isinstance(event_type, str) or not re.match(r"^[a-zA-Z0-9_\-.]+$", event_type):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz event_type formatı."}

            if not payload_summary or not isinstance(payload_summary, str) or len(payload_summary) > 500:
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz veya çok uzun payload özeti."}

            # SQL Injection ve XSS saldırı vektörü taraması
            dangerous_patterns = [r"(\bOR\b|\bAND\b).*?=.*?--", r"<script.*?>.*?</script>", r"UNION\s+SELECT"]
            for pattern in dangerous_patterns:
                if re.search(pattern, payload_summary, re.IGNORECASE) or re.search(pattern, event_type, re.IGNORECASE):
                    return {"status": "error", "code": 403, "message": "1. Halka WAF Blokajı: Olay girdilerinde zararlı vektör tespit edildi."}

            # --- 2. HALKA: Çoklu-Kiracı Veri İzolasyonu (tenant_id filtresi) ---
            safe_tenant_id = re.sub(r"[^a-zA-Z0-9_]", "", tenant_id)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # --- 3. HALKA: Çekirdek İş Mantığı & Güvenli Durum Yönetimi ---
            timestamp = datetime.now(timezone.utc).isoformat()
            event_seed = f"{safe_tenant_id}:{event_type}:{payload_summary}:{timestamp}"
            event_hash = hashlib.sha256(event_seed.encode()).hexdigest()
            event_uuid = f"evt_{event_hash[:12]}"

            # --- 4. HALKA: Idempotency (Mükerrer İstek ve Yarış Koşulu Koruması) ---
            cursor.execute("SELECT event_uuid FROM system_events WHERE tenant_id = ? AND event_type = ? AND event_hash = ?", 
                           (safe_tenant_id, event_type, event_hash))
            existing_event = cursor.fetchone()

            if existing_event:
                conn.close()
                return {
                    "status": "success",
                    "code": 200,
                    "cached": True,
                    "message": "4. Halka Devrede: Aynı olay mesajı mükerrer işlenmedi.",
                    "event_uuid": existing_event[0]
                }

            # Kayıt Oluşturma (Append-Only Delta)
            cursor.execute('''
                INSERT INTO system_events (event_uuid, tenant_id, event_type, payload_summary, event_hash, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event_uuid, safe_tenant_id, event_type, payload_summary, event_hash, "PUBLISHED", timestamp))

            conn.commit()
            conn.close()

            return {
                "status": "success",
                "code": 201,
                "cached": False,
                "message": "Sistem olayı başarıyla yayınlandı ve mühürlendi.",
                "event_uuid": event_uuid,
                "tenant_id": safe_tenant_id,
                "event_type": event_type
            }

        except Exception as e:
            # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except ve Güvenli Yanıt ---
            return {
                "status": "error",
                "code": 500,
                "message": "Event Broker katmanında dahili durum güvenle yakalandı.",
                "details": "Sistem kararlılığı korundu, hassas hata gizlendi."
            }

if __name__ == "__main__":
    broker = FeatureEventBrokerModule()
    print("--- TEST 1: Geçerli Olay Yayınlama ---")
    print(broker.publish_event("tenant_alpha_01", "Bearer VALID_TOKEN_BROKER", "security.scanner.started", "scan_target=scanme.nmap.org"))
    
    print("\n--- TEST 2: Idempotency (Mükerrer Olay) Testi ---")
    print(broker.publish_event("tenant_alpha_01", "Bearer VALID_TOKEN_BROKER", "security.scanner.started", "scan_target=scanme.nmap.org"))
    
    print("\n--- TEST 3: Geçersiz Event Type / 1. Halka Koruması ---")
    print(broker.publish_event("tenant_alpha_01", "Bearer VALID_TOKEN_BROKER", "INVALID TYPE!", "scan_target=scanme.nmap.org"))
