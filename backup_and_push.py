import shutil
import datetime
import os
import subprocess

def create_snapshot():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    for filename in ["main.py", "models.py"]:
        if os.path.exists(filename):
            dst = os.path.join(backup_dir, f"{filename.split('.')[0]}_{timestamp}.bak")
            shutil.copy(filename, dst)
            print(f"[SUCCESS] Snapshot oluşturuldu: {dst}")

def git_sync():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "AegisMatrix: Abonelik senkronizasyonu ve faturalandırma modülü tamamlandı."], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[SUCCESS] Git versiyonlama ve GitHub senkronizasyonu tamamlandı.")
    except Exception as e:
        print(f"[INFO] Git işlem detayları: {str(e)}")

if __name__ == "__main__":
    create_snapshot()
    git_sync()
