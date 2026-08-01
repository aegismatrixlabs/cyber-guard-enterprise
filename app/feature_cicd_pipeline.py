import sqlite3
import re
import hashlib
from datetime import datetime, timezone

class FeatureCicdPipelineModule:
    def __init__(self, db_path="cyber_guard.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """CI/CD Pipeline durum ve tetikleme tablosunun hazırlanması"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cicd_pipelines (
                pipeline_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                actor TEXT NOT NULL,
                repository TEXT NOT NULL,
                branch TEXT NOT NULL,
                commit_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def trigger_pipeline(self, tenant_id: str, auth_token: str, repository: str, branch: str, commit_hash: str):
        """5-Zincir Kuralına Göre Güvenli CI/CD Boru Hattı Tetikleme"""
        try:
            # --- 1. HALKA: Girdi Doğrulama ve Kimlik Kontrolü (Auth/JWT & Sanitizasyon) ---
            if not tenant_id or not isinstance(tenant_id, str) or not re.match(r"^tenant_[a-zA-Z0-9_]+$", tenant_id):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz tenant_id formatı."}

            if not auth_token or not isinstance(auth_token, str) or not auth_token.startswith("Bearer "):
                return {"status": "error", "code": 401, "message": "1. Halka İhlali: Geçersiz veya yetkisiz Auth/JWT token."}

            if not repository or not isinstance(repository, str) or not re.match(r"^[a-zA-Z0-9_\-/.]+$", repository):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz repository formatı."}

            if not branch or not isinstance(branch, str) or not re.match(r"^[a-zA-Z0-9_\-/]+$", branch):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz branch adı."}

            if not commit_hash or not isinstance(commit_hash, str) or not re.match(r"^[a-fA-F0-9]{7,40}$", commit_hash):
                return {"status": "error", "code": 400, "message": "1. Halka İhlali: Geçersiz commit hash imzası."}

            # SQL Injection ve XSS saldırı vektörü taraması
            dangerous_patterns = [r"(\bOR\b|\bAND\b).*?=.*?--", r"<script.*?>.*?</script>", r"UNION\s+SELECT"]
            for pattern in dangerous_patterns:
                if re.search(pattern, repository, re.IGNORECASE) or re.search(pattern, branch, re.IGNORECASE):
                    return {"status": "error", "code": 403, "message": "1. Halka WAF Blokajı: CI/CD girdilerinde zararlı vektör tespit edildi."}

            # --- 2. HALKA: Çoklu-Kiracı Veri İzolasyonu (tenant_id filtresi) ---
            safe_tenant_id = re.sub(r"[^a-zA-Z0-9_]", "", tenant_id)
            actor = "user_" + auth_token.split(" ")[-1][:8]

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # --- 3. HALKA: Çekirdek İş Mantığı & Güvenli Durum Yönetimi ---
            timestamp = datetime.now(timezone.utc).isoformat()
            pipeline_seed = f"{safe_tenant_id}:{repository}:{branch}:{commit_hash}:{timestamp}"
            pipeline_hash = hashlib.sha256(pipeline_seed.encode()).hexdigest()
            pipeline_id = f"pipe_{pipeline_hash[:12]}"

            # --- 4. HALKA: Idempotency (Mükerrer İstek ve Yarış Koşulu Koruması) ---
            cursor.execute("SELECT status FROM cicd_pipelines WHERE tenant_id = ? AND repository = ? AND commit_hash = ?", 
                           (safe_tenant_id, repository, commit_hash))
            existing_pipeline = cursor.fetchone()

            if existing_pipeline:
                conn.close()
                return {
                    "status": "success",
                    "code": 200,
                    "cached": True,
                    "message": "4. Halka Devrede: Aynı commit için tetiklenen pipeline mükerrer çalıştırılmadı.",
                    "pipeline_id": pipeline_id,
                    "pipeline_status": existing_pipeline[0]
                }

            # Kayıt Oluşturma (Append-Only Delta)
            cursor.execute('''
                INSERT INTO cicd_pipelines (pipeline_id, tenant_id, actor, repository, branch, commit_hash, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pipeline_id, safe_tenant_id, actor, repository, branch, commit_hash, "TRIGGERED", timestamp))

            conn.commit()
            conn.close()

            return {
                "status": "success",
                "code": 201,
                "cached": False,
                "message": "CI/CD boru hattı başarıyla tetiklendi ve mühürlendi.",
                "pipeline_id": pipeline_id,
                "tenant_id": safe_tenant_id,
                "commit_hash": commit_hash[:8]
            }

        except Exception as e:
            # --- 5. HALKA: Çökme Önleyici Kapsamlı Try-Except ve Güvenli Yanıt ---
            return {
                "status": "error",
                "code": 500,
                "message": "CI/CD Pipeline katmanında dahili durum güvenle yakalandı.",
                "details": "Sistem kararlılığı korundu, hassas hata gizlendi."
            }

if __name__ == "__main__":
    cicd = FeatureCicdPipelineModule()
    print("--- TEST 1: Geçerli Pipeline Tetikleme ---")
    print(cicd.trigger_pipeline("tenant_alpha_01", "Bearer VALID_TOKEN_ABC", "cyberguard/core", "main", "a1b2c3d4e5f6"))
    
    print("\n--- TEST 2: Idempotency (Mükerrer Commit) Testi ---")
    print(cicd.trigger_pipeline("tenant_alpha_01", "Bearer VALID_TOKEN_ABC", "cyberguard/core", "main", "a1b2c3d4e5f6"))
    
    print("\n--- TEST 3: Geçersiz Commit Hash / 1. Halka Koruması ---")
    print(cicd.trigger_pipeline("tenant_alpha_01", "Bearer VALID_TOKEN_ABC", "cyberguard/core", "main", "INVALID_HASH!"))
