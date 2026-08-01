import sqlite3
import threading
import uuid
import hashlib
import hmac
import time
from typing import Dict, Any, Optional

db_lock = threading.Lock()

class TenantIsolationManager:
    def __init__(self, db_path: str = "app/cyber_guard.db", secret_key: str = "cyber_guard_secret_master_key"):
        self.db_path = db_path
        self.secret_key = secret_key.encode('utf-8')
        self._init_db()

    def _init_db(self):
        with db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenant_isolated_store (
                    record_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    payload_key TEXT NOT NULL,
                    payload_value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    idempotency_hash TEXT UNIQUE NOT NULL
                )
            """)
            conn.commit()
            conn.close()

    def _generate_jwt_signature(self, tenant_id: str, payload_key: str) -> str:
        message = f"{tenant_id}:{payload_key}".encode('utf-8')
        return hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()

    def execute_isolated_operation(self, tenant_id: str, auth_token: str, payload_key: str, payload_value: str, idempotency_token: str) -> Dict[str, Any]:
        try:
            if not tenant_id or not isinstance(tenant_id, str) or len(tenant_id.strip()) == 0:
                return {"status": "error", "code": 400, "message": "Geçersiz veya eksik tenant_id."}
            
            if not auth_token or not isinstance(auth_token, str):
                return {"status": "error", "code": 401, "message": "Kimlik doğrulama token'ı eksik."}

            sanitized_tenant = tenant_id.strip()
            sanitized_key = str(payload_key).strip()
            sanitized_val = str(payload_value).strip()

            expected_sig = self._generate_jwt_signature(sanitized_tenant, sanitized_key)
            if not hmac.compare_digest(auth_token.strip(), expected_sig):
                return {"status": "error", "code": 403, "message": "Yetkilendirme hatası: Geçersiz imza veya token."}

            raw_hash_data = f"{sanitized_tenant}:{sanitized_key}:{idempotency_token}"
            idempotency_hash = hashlib.sha256(raw_hash_data.encode('utf-8')).hexdigest()

            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT record_id FROM tenant_isolated_store WHERE idempotency_hash = ?", 
                    (idempotency_hash,)
                )
                existing = cursor.fetchone()
                if existing:
                    conn.close()
                    return {
                        "status": "success", 
                        "code": 200,
                        "cached": True, 
                        "message": "İşlem daha önce gerçekleştirildi (Idempotent mükerrer engelleme aktif).",
                        "record_id": existing[0]
                    }

                record_id = str(uuid.uuid4())
                current_time = time.time()

                cursor.execute("""
                    INSERT INTO tenant_isolated_store (record_id, tenant_id, payload_key, payload_value, created_at, idempotency_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (record_id, sanitized_tenant, sanitized_key, sanitized_val, current_time, idempotency_hash))

                conn.commit()
                conn.close()

                return {
                    "status": "success",
                    "code": 201,
                    "cached": False,
                    "message": "İşlem başarıyla tamamlandı ve izole edildi.",
                    "tenant_id": sanitized_tenant,
                    "record_id": record_id
                }

        except Exception as e:
            return {
                "status": "error",
                "code": 500,
                "message": "Güvenli işlem sırasında sistem hatası oluştu. İstek güvenle izole edildi."
            }

    def query_tenant_records(self, tenant_id: str, auth_token: str) -> Dict[str, Any]:
        try:
            if not tenant_id or not auth_token:
                return {"status": "error", "code": 400, "message": "Tenant ID ve Auth Token zorunludur."}

            sanitized_tenant = tenant_id.strip()

            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT record_id, payload_key, payload_value, created_at FROM tenant_isolated_store WHERE tenant_id = ?",
                    (sanitized_tenant,)
                )
                rows = cursor.fetchall()
                conn.close()

                records = [{"record_id": r[0], "key": r[1], "value": r[2], "created_at": r[3]} for r in rows]
                return {
                    "status": "success",
                    "code": 200,
                    "tenant_id": sanitized_tenant,
                    "count": len(records),
                    "records": records
                }
        except Exception as e:
            return {"status": "error", "code": 500, "message": "Sorgulama sırasında güvenlik istisnası yakalandı."}

if __name__ == "__main__":
    manager = TenantIsolationManager()
    test_tenant = "tenant_alpha_01"
    test_key = "secure_cluster_config"
    test_val = "active_mode_v1"
    test_token = manager._generate_jwt_signature(test_tenant, test_key)
    idempotency_id = "idem_token_998877"

    print("--- TEST 1: Yeni İzole Kayıt ---")
    print(manager.execute_isolated_operation(test_tenant, test_token, test_key, test_val, idempotency_id))

    print("--- TEST 2: Idempotency Testi ---")
    print(manager.execute_isolated_operation(test_tenant, test_token, test_key, test_val, idempotency_id))

    print("--- TEST 3: İzolasyon Sorgusu ---")
    print(manager.query_tenant_records(test_tenant, test_token))
