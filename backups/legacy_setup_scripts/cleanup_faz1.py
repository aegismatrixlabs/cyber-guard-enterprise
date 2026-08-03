import os
import shutil
import sys

def execute_faz1_cleanup():
    print("[*] AegisMatrix Faz 1: Dizin Temizliği ve Tekilleştirme Başlatıldı...")
    project_root = os.getcwd()
    nested_app_path = os.path.join(project_root, "app", "app")

    if os.path.exists(nested_app_path) and os.path.isdir(nested_app_path):
        print(f"[!] Hatalı iç içe dizin tespit edildi: {nested_app_path}")
        for item in os.listdir(nested_app_path):
            src_item = os.path.join(nested_app_path, item)
            dst_item = os.path.join(project_root, "app", item)
            if not os.path.exists(dst_item):
                shutil.move(src_item, dst_item)
                print(f"    [+] Taşındı: {item} -> app/")
        shutil.rmtree(nested_app_path)
        print("[+] Hatalı ./app/app/ dizini temizlendi.")
    else:
        print("[+] İç içe ./app/app/ dizini bulunamadı. Yapı temiz.")
    print("[✔] Faz 1 Tamamlandı.")

if __name__ == "__main__":
    execute_faz1_cleanup()
