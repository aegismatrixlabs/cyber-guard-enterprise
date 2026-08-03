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

def git_commit_changes():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "AegisMatrix: Kurumsal kimlik ve Lemon Squeezy Checkout entegrasyonu tamamlandı."], check=True)
        print("[SUCCESS] Git versiyonlama ve commit işlemi başarıyla tamamlandı.")
    except Exception as e:
        print(f"[INFO] Git commit atlantı veya hata oluştu: {str(e)}")

if __name__ == "__main__":
    create_snapshot()
    git_commit_changes()
