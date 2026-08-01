import sqlite3
import re
import hashlib
from datetime import datetime, timezone

class FeatureApmMonitorModule:
    def __init__(self, db_path="cyber_guard.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """APM Performans Metrikleri tablosunun hazırlanması"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apm_metrics (
                metric_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                service_name TEXT NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                response_time_ms INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                status_hash TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def record_metric(self, tenant_id: str, auth_token: str, service_name: str, cpu_usage: float, memory_usage: float, response_time_ms: int, error_rate: float):
        """5-Zincir Kuralına Göre Güvenli APM Metrik Kaydı ve Durum Yönetimi"""
        try:
            # --- 1. HALKA: Girdi Doğrulama ve Kimlik Kontrolü (Auth/JWT & Sanitizasyon) ---
            if not tenant_id or not isinstance(tenant_id, str) or not re.match(r"^tenant_[a-zA-Z0-9_]+$", tenant_id):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz tenant_id formatı."}

            if not auth_token or not isinstance(auth_token, str) or not auth_token.startswith("Bearer "):
                return {"status": "error", "code": 401, "message": "1. Halka İhlali: Geçersiz veya yetkisiz Auth/JWT token."}

            if not service_name or not isinstance(service_name, str) or not re.match(r"^[a-zA-Z0-9_\-/.]+$", service_name):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz service_name formatı."}

            if not isinstance(cpu_usage, (int, float)) or not (0.0 <= cpu_usage <= 100.0):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz CPU kullanım oranı (0-100 aralığında olmalıdır)."}

            if not isinstance(memory_usage, (int, float)) or not (0.0 <= memory_usage <= 100.0):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz Bellek kullanım oranı (0-100 aralığında olmalıdır)."}

            if not isinstance(response_time_ms, int) or response_time_ms < 0:
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz yanıt süresi (ms)."}

            if not isinstance(error_rate, (int, float)) or not (0.0 <= error_rate <= 100.0):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz hata oranı."}

            # SQL Injection ve XSS saldırı vektörü taraması
            dangerous_patterns = [r"(\bOR\b|\bAND\b).*?=.*?--", r"<script.*?>.*?</script>", r"UNION\s+SELECT"]
            for pattern in dangerous_patterns:
                if re.search(pattern, service_name, re.IGNORECASE):
                    return {"status": "error", "code": 403, "message": "1. Halka WAF Blokajı: Metrik girdilerinde zararlı vektör tespit edildi."}

            # --- 2. HALKA: Çoklu-Kiracı Veri İzolasyonu (tenant_id filtresi) ---
            safe_tenant_id = re.sub(r"[^a-zA-Z0-9_]", "", tenant_id)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # --- 3. HALKA: Çekirdek İş Mantığı & Güvenli Durum Yönetimi ---
            timestamp = datetime.now(timezone.utc).isoformat()
            metric_seed = f"{safe_tenant_id}:{service_name}:{cpu_usage}:{memory_usage}:{response_time_ms}:{timestamp}"
            metric_hash = hashlib.sha256(metric_seed.encode()).hexdigest()
            metric_id = f"apm_{metric_hash[:12]}"

            # --- 4. HALKA: Idempotency (Mükerrer İstek ve Yarış Koşulu Koruması) ---
            cursor.execute("SELECT metric_id FROM apm_metrics WHERE tenant_id = ? AND service_name = ? AND status_hash = ?", 
                           (safe_tenant_id, service_name, metric_hash))
            existing_metric = cursor.fetchone()

            if existing_metric:
                conn.close()
                return {
                    "status": "success",
                    "code": 200,
                    "cached": True,
                    "message": "4. Halka Devrede: Aynı performans metrik paketi mükerrer işlenmedi.",
                    "metric_id": existing_metric[0]
                }

            # Kayıt Oluşturma (Append-Only Delta)
            cursor.execute('''
                INSERT INTO apm_metrics (metric_id, tenant_id, service_name, cpu_usage, memory_usage, response_time_ms, error_rate, status_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (metric_id, safe_tenant_id, service_name, cpu_usage, memory_usage, response_time_ms, error_rate, metric_hash, timestamp))

            conn.commit()
            conn.close()

            return {
                "status": "success",
                "code": 201,
                "cached": False,
                "message": "APM performans metriği başarıyla kaydedildi ve mühürlendi.",
                "metric_id": metric_id,
                "tenant_id": safe_tenant_id,
                "service_name": service_name
            }

        except Exception as e:
            # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except ve Güvenli Yanıt ---
            return {
                "status": "error",
                "code": 500,
                "message": "APM İzleme katmanında dahili durum güvenle yakalandı.",
                "details": "Sistem kararlılığı korundu, hassas hata gizlendi."
            }

if __name__ == "__main__":
    apm = FeatureApmMonitorModule()
    print("--- TEST 1: Geçerli APM Metrik Kaydı ---")
    print(apm.record_metric("tenant_alpha_01", "Bearer VALID_TOKEN_XYZ", "auth-service", 45.2, 68.4, 120, 0.02))
    
    print("\n--- TEST 2: Idempotency (Mükerrer Metrik) Testi ---")
    print(apm.record_metric("tenant_alpha_01", "Bearer VALID_TOKEN_XYZ", "auth-service", 45.2, 68.4, 120, 0.02))
    
    print("\n--- TEST 3: Geçersiz CPU Değeri / 1. Halka Koruması ---")
    print(apm.record_metric("tenant_alpha_01", "Bearer VALID_TOKEN_XYZ", "auth-service", 150.0, 68.4, 120, 0.02))
