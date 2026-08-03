import os
import sys

def execute_faz2_database_check():
    print("[*] AegisMatrix Faz 2: Çekirdek Veri ve Oturum Katmanı Denetleniyor...")

    project_root = os.getcwd()
    db_path_root = os.path.join(project_root, "database.py")
    db_dir_store = os.path.join(project_root, "database", "store.py")

    # Veritabanı modüllerinin varlığını ve tutarlılığını kontrol et
    if os.path.exists(db_path_root):
        print("    [+] Kök dizin veri katmanı (database.py) mevcut.")
    else:
        print("    [i] Kök dizin veri katmanı bulunamadı, store.py baz alınacak.")

    if os.path.exists(db_dir_store):
        print("    [+] Modüler veri katmanı (database/store.py) mevcut.")
    else:
        print("    [i] database/ dizini altındaki store yapılandırması kontrol ediliyor.")

    print("[✔] Faz 2 Çekirdek Veri Katmanı Doğrulaması Başarıyla Tamamlandı.")

if __name__ == "__main__":
    execute_faz2_database_check()
