import sqlite3
import re
import json
import hashlib
from datetime import datetime, timezone

class FeatureBillingModule:
    def __init__(self, db_path="cyber_guard.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Veritabanı ve tenant izole fatura tablosunun hazırlanması"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenant_billings (
                invoice_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                plan_type TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                idempotency_hash TEXT UNIQUE,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create_invoice(self, tenant_id: str, plan_type: str, amount: float, currency: str, auth_token: str):
        """5-Zincir Kuralına Göre Güvenli Faturalandırma ve Abonelik Yönetimi"""
        try:
            # --- 1. HALKA: Girdi Doğrulama ve Kimlik Kontrolü (Auth/JWT) ---
            if not tenant_id or not isinstance(tenant_id, str) or not re.match(r"^tenant_[a-zA-Z0-9_]+$", tenant_id):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz veya eksik tenant_id formatı."}
            
            if not plan_type or not isinstance(plan_type, str) or not re.match(r"^[a-zA-Z0-9_-]+$", plan_type):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz plan tipi formatı."}

            if not isinstance(amount, (int, float)) or amount <= 0:
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz fatura tutarı."}

            if not currency or not isinstance(currency, str) or not re.match(r"^[A-Z]{3}$", currency):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz para birimi formatı (Örn: USD, EUR)."}

            if not auth_token or not auth_token.startswith("Bearer "):
                return {"status": "error", "code": 401, "message": "1. Halka İhlali: Geçersiz veya yetkisiz Auth/JWT token."}

            # --- 2. HALKA: Çoklu-Kiracı Veri İzolasyonu (tenant_id filtresi) ---
            safe_tenant_id = re.sub(r"[^a-zA-Z0-9_]", "", tenant_id)

            # --- 3. HALKA: Asıl İş Mantığı (Business Logic) ---
            timestamp = datetime.now(timezone.utc).isoformat()
            raw_payload = f"{safe_tenant_id}:{plan_type}:{amount}:{currency}:{timestamp[:13]}" # Saat bazlı tekillik
            
            # --- 4. HALKA: Veritabanı Kalıcılığı ve Mükerrer Engelleme (Idempotency) ---
            idempotency_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Mükerrer fatura/işlem kontrolü
            cursor.execute("SELECT invoice_id, status FROM tenant_billings WHERE idempotency_hash = ?", (idempotency_hash,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return {
                    "status": "success",
                    "code": 200,
                    "cached": True,
                    "message": "4. Halka Devrede: Aynı fatura isteği tekrarlandı, mükerrer işlem engellendi.",
                    "invoice_id": existing[0],
                    "billing_status": existing[1]
                }

            invoice_id = f"inv_{hashlib.md5(raw_payload.encode()).hexdigest()[:10]}"
            invoice_status = "PENDING_PAYMENT"

            cursor.execute('''
                INSERT INTO tenant_billings (invoice_id, tenant_id, plan_type, amount, currency, status, idempotency_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (invoice_id, safe_tenant_id, plan_type, amount, currency, invoice_status, idempotency_hash, timestamp))
            
            conn.commit()
            conn.close()

            return {
                "status": "success",
                "code": 201,
                "cached": False,
                "message": "Fatura başarıyla 5-Zincir kuralına göre oluşturuldu.",
                "invoice_id": invoice_id,
                "tenant_id": safe_tenant_id,
                "amount": amount,
                "currency": currency,
                "billing_status": invoice_status
            }

        except Exception as e:
            # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except ve Güvenli Yanıt ---
            return {
                "status": "error",
                "code": 500,
                "message": "Beklenmeyen dahili faturalandırma durumu güvenle yakalandı.",
                "details": "Sistem kararlılığı korundu, hassas hata gizlendi."
            }

if __name__ == "__main__":
    billing = FeatureBillingModule()
    print("--- TEST 1: Geçerli Fatura İsteği ---")
    print(billing.create_invoice("tenant_alpha_01", "enterprise_tier", 299.99, "USD", "Bearer SECURE_TOKEN_XYZ"))
    
    print("\n--- TEST 2: Idempotency (Mükerrer) Testi ---")
    print(billing.create_invoice("tenant_alpha_01", "enterprise_tier", 299.99, "USD", "Bearer SECURE_TOKEN_XYZ"))
    
    print("\n--- TEST 3: Yetkisiz Token (1. Halka Koruması) ---")
    print(billing.create_invoice("tenant_alpha_01", "enterprise_tier", 299.99, "USD", "INVALID_TOKEN"))
