import shutil
import datetime
import os
import subprocess

def create_snapshot():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    src = "main.py"
    dst = os.path.join(backup_dir, f"main_{timestamp}.bak")
    
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"[SUCCESS] AegisMatrix Snapshot başarıyla oluşturuldu: {dst}")
    else:
        print(f"[ERROR] {src} dosyası bulunamadı!")

def git_sync():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "AegisMatrix: Lemon Squeezy Webhook imza doğrulama ve abonelik senkronizasyonu eklendi."], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[SUCCESS] Git versiyonlama ve GitHub'a yükleme işlemi başarıyla tamamlandı.")
    except Exception as e:
        print(f"[INFO] Git işlem detayları veya hata oluştu (Uzak repo bağlı olmayabilir): {str(e)}")

if __name__ == "__main__":
    create_snapshot()
    git_sync()
