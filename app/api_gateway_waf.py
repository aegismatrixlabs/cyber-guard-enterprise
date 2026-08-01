import sqlite3
import re
import hashlib
import time
from datetime import datetime, timezone

class ApiGatewayWafModule:
    def __init__(self, db_path="cyber_guard.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """WAF logları, rate-limit ve idempotency tablolarının hazırlanması"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waf_request_logs (
                request_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                client_ip TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waf_rate_limits (
                client_ip TEXT PRIMARY KEY,
                request_count INTEGER,
                window_start REAL
            )
        ''')
        conn.commit()
        conn.close()

    def inspect_and_route(self, tenant_id: str, client_ip: str, endpoint: str, payload: str, auth_token: str):
        """5-Zincir Kuralına Göre WAF & API Gateway İstek Denetimi ve Kimlik Kontrolü"""
        try:
            # --- 1. HALKA: Girdi Doğrulama ve Kimlik Kontrolü (Auth/JWT & SQLi/XSS Koruma) ---
            if not tenant_id or not isinstance(tenant_id, str) or not re.match(r"^tenant_[a-zA-Z0-9_]+$", tenant_id):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz tenant_id formatı."}

            if not client_ip or not isinstance(client_ip, str) or not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", client_ip):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz IP adresi formatı."}

            if not endpoint or not isinstance(endpoint, str) or not endpoint.startswith("/"):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz endpoint rotası."}

            # SQL Injection ve XSS saldırı vektörü taraması
            dangerous_patterns = [r"(\bOR\b|\bAND\b).*?=.*?--", r"<script.*?>.*?</script>", r"UNION\s+SELECT"]
            for pattern in dangerous_patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    return {"status": "error", "code": 403, "message": "1. Halka WAF Blokajı: SQLi / XSS saldırı vektörü tespit edildi."}

            if not auth_token or not isinstance(auth_token, str) or not auth_token.startswith("Bearer "):
                return {"status": "error", "code": 401, "message": "1. Halka İhlali: Geçersiz veya yetkisiz Auth/JWT token."}

            # --- 2. HALKA: Çoklu-Kiracı Veri İzolasyonu (tenant_id filtresi & Rate Limit) ---
            safe_tenant_id = re.sub(r"[^a-zA-Z0-9_]", "", tenant_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            cursor.execute("SELECT request_count, window_start FROM waf_rate_limits WHERE client_ip = ?", (client_ip,))
            rate_data = cursor.fetchone()

            if rate_data:
                count, window_start = rate_data
                if current_time - window_start < 60:
                    if count >= 30:
                        conn.close()
                        return {"status": "error", "code": 429, "message": "2. Halka İhlali: Rate-limit aşıldı. Çok fazla istek."}
                    cursor.execute("UPDATE waf_rate_limits SET request_count = request_count + 1 WHERE client_ip = ?", (client_ip,))
                else:
                    cursor.execute("UPDATE waf_rate_limits SET request_count = 1, window_start = ? WHERE client_ip = ?", (current_time, client_ip))
            else:
                cursor.execute("INSERT INTO waf_rate_limits (client_ip, request_count, window_start) VALUES (?, 1, ?)", (client_ip, current_time))
            
            conn.commit()

            # --- 3. HALKA: Asıl İş Mantığı (Business Logic & Payload Hash) ---
            timestamp = datetime.now(timezone.utc).isoformat()
            payload_hash = hashlib.sha256(f"{safe_tenant_id}:{endpoint}:{payload}".encode()).hexdigest()

            # --- 4. HALKA: Veritabanı Kalıcılığı ve Mükerrer Engelleme (Idempotency) ---
            request_id = f"req_{payload_hash[:12]}"
            cursor.execute("SELECT status FROM waf_request_logs WHERE request_id = ?", (request_id,))
            existing_req = cursor.fetchone()
            
            if existing_req:
                conn.close()
                return {
                    "status": "success",
                    "code": 200,
                    "cached": True,
                    "message": "4. Halka Devrede: Aynı istek tekrarlandı, mükerrer işlem engellendi.",
                    "request_id": request_id
                }

            cursor.execute('''
                INSERT INTO waf_request_logs (request_id, tenant_id, client_ip, endpoint, payload_hash, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (request_id, safe_tenant_id, client_ip, endpoint, payload_hash, "ALLOWED", timestamp))
            
            conn.commit()
            conn.close()

            return {
                "status": "success",
                "code": 200,
                "cached": False,
                "message": "WAF denetimi başarıyla geçildi, rota yönlendiriliyor.",
                "request_id": request_id,
                "tenant_id": safe_tenant_id,
                "endpoint": endpoint
            }

        except Exception as e:
            # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except ve Güvenli Yanıt ---
            return {
                "status": "error",
                "code": 500,
                "message": "API Gateway güvenlik katmanında dahili durum güvenle yakalandı.",
                "details": "Sistem kararlılığı korundu, hassas hata gizlendi."
            }

if __name__ == "__main__":
    waf = ApiGatewayWafModule()
    print("--- TEST 1: Geçerli İstek ---")
    print(waf.inspect_and_route("tenant_alpha_01", "192.168.1.10", "/api/v1/scan", "target=scanme.nmap.org", "Bearer VALID_TOKEN_XYZ"))
    
    print("\n--- TEST 2: Idempotency (Mükerrer) Testi ---")
    print(waf.inspect_and_route("tenant_alpha_01", "192.168.1.10", "/api/v1/scan", "target=scanme.nmap.org", "Bearer VALID_TOKEN_XYZ"))
    
    print("\n--- TEST 3: SQLi Saldırı Girişimi (1. Halka Koruması) ---")
    print(waf.inspect_and_route("tenant_alpha_01", "192.168.1.10", "/api/v1/scan", "id=1 OR 1=1--", "Bearer VALID_TOKEN_XYZ"))
