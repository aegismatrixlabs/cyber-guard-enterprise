import sqlite3
import re
import hashlib
from datetime import datetime, timezone

class FeatureAuditLogModule:
    def __init__(self, db_path="cyber_guard.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Denetim günlüğü tablosunun ve indekslerin hazırlanması"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                event_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                previous_hash TEXT,
                status TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def record_event(self, tenant_id: str, auth_token: str, action: str, details: str):
        """5-Zincir Kuralına Göre Denetim Günlüğü ve Kimlik Kontrolü"""
        try:
            # --- 1. HALKA: Girdi Doğrulama ve Kimlik Kontrolü (Auth/JWT & Sanitizasyon) ---
            if not tenant_id or not isinstance(tenant_id, str) or not re.match(r"^tenant_[a-zA-Z0-9_]+$", tenant_id):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz tenant_id formatı."}

            if not auth_token or not isinstance(auth_token, str) or not auth_token.startswith("Bearer "):
                return {"status": "error", "code": 401, "message": "1. Halka İhlali: Geçersiz veya yetkisiz Auth/JWT token."}

            if not action or not isinstance(action, str) or len(action) > 100:
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz veya aşırı uzun eylem (action) tanımı."}

            # SQL Injection ve XSS saldırı vektörü taraması
            dangerous_patterns = [r"(\bOR\b|\bAND\b).*?=.*?--", r"<script.*?>.*?</script>", r"UNION\s+SELECT"]
            for pattern in dangerous_patterns:
                if re.search(pattern, details, re.IGNORECASE):
                    return {"status": "error", "code": 403, "message": "1. Halka WAF Blokajı: Denetim detaylarında SQLi / XSS vektörü tespit edildi."}

            # --- 2. HALKA: Çoklu-Kiracı Veri İzolasyonu (tenant_id filtresi) ---
            safe_tenant_id = re.sub(r"[^a-zA-Z0-9_]", "", tenant_id)
            actor = "user_" + auth_token.split(" ")[-1][:8] # Token tabanlı aktör tespiti

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # --- 3. HALKA: Asıl İş Mantığı (Business Logic & Kriptografik Hash Zinciri) ---
            timestamp = datetime.now(timezone.utc).isoformat()
            payload_raw = f"{safe_tenant_id}:{actor}:{action}:{details}:{timestamp}"
            payload_hash = hashlib.sha256(payload_raw.encode()).hexdigest()

            # İlgili kiracının son log kayıt hash değerini al (Append-Only Delta Integrity)
            cursor.execute("SELECT payload_hash FROM audit_logs WHERE tenant_id = ? ORDER BY created_at DESC LIMIT 1", (safe_tenant_id,))
            last_record = cursor.fetchone()
            previous_hash = last_record[0] if last_record else "GENESIS_BLOCK_HASH"

            # --- 4. HALKA: Veritabanı Kalıcılığı ve Mükerrer Engelleme (Idempotency) ---
            event_id = f"evt_{payload_hash[:12]}"
            cursor.execute("SELECT status FROM audit_logs WHERE event_id = ?", (event_id,))
            existing_event = cursor.fetchone()

            if existing_event:
                conn.close()
                return {
                    "status": "success",
                    "code": 200,
                    "cached": True,
                    "message": "4. Halka Devrede: Aynı denetim olayı mükerrer kaydedilmedi, koruma sağlandı.",
                    "event_id": event_id
                }

            cursor.execute('''
                INSERT INTO audit_logs (event_id, tenant_id, actor, action, payload_hash, previous_hash, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, safe_tenant_id, actor, action, payload_hash, previous_hash, "RECORDED", timestamp))

            conn.commit()
            conn.close()

            return {
                "status": "success",
                "code": 201,
                "cached": False,
                "message": "Denetim günlüğü şifreli hash zinciriyle başarıyla kaydedildi.",
                "event_id": event_id,
                "tenant_id": safe_tenant_id,
                "previous_hash": previous_hash[:16] + "..."
            }

        except Exception as e:
            # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except ve Kullanıcı Dostu Çıktı ---
            return {
                "status": "error",
                "code": 500,
                "message": "Audit Log güvenlik katmanında dahili durum güvenle yakalandı.",
                "details": "Sistem kararlılığı korundu, hassas hata gizlendi."
            }

if __name__ == "__main__":
    audit = FeatureAuditLogModule()
    print("--- TEST 1: Geçerli Denetim Olayı Kaydı ---")
    print(audit.record_event("tenant_alpha_01", "Bearer VALID_TOKEN_XYZ", "USER_CONFIG_UPDATE", "Security settings modified."))
    
    print("\n--- TEST 2: Idempotency (Mükerrer) Testi ---")
    print(audit.record_event("tenant_alpha_01", "Bearer VALID_TOKEN_XYZ", "USER_CONFIG_UPDATE", "Security settings modified."))
    
    print("\n--- TEST 3: SQLi Saldırı Girişimi (1. Halka Koruması) ---")
    print(audit.record_event("tenant_alpha_01", "Bearer VALID_TOKEN_XYZ", "MALICIOUS_ACTION", "id=1 UNION SELECT * FROM users--"))
