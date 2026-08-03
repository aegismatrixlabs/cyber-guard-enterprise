import os
import sys

def inject_html():
    print("[*] Dashboard Şablonuna Mega-Menu HTML Yapısı Entegre Ediliyor...")
    try:
        dashboard_path = "templates/dashboard.html"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, "r", encoding="utf-8") as f:
                html = f.read()
            
            # Eğer zaten eklenmediyse sol menüye dropdown yapısını ekle
            target_str = '<a href="/assets"'
            replacement = '''<div class="nav-dropdown" style="display:inline-block; width:100%;">
            <a href="/assets"'''
            
            if "nav-dropdown" not in html and target_str in html:
                # Örnek olarak Varlık Yönetimi linkini dropdown wrapper içine alıyoruz
                html = html.replace(target_str, '<div class="nav-dropdown"><a href="/assets" style="display:block;">Varlık Yönetimi ▾</a><div class="nav-dropdown-content"><a href="/assets" class="dropdown-item">Bulut Varlıkları</a><a href="/assets" class="dropdown-item">Endpoint Envanteri</a><a href="/assets" class="dropdown-item">IAM & Kimlikler</a></div></div>')
                
                with open(dashboard_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print("    [+] Başarılı: dashboard.html içine açılır menü HTML blokları eklendi.")
            else:
                print("    [*] Bilgi: HTML yapısı zaten mevcut veya hedef etiket bulunamadı.")
                
        print("\n[✔] Entegrasyon Tamamlandı. Sayfayı yenileyebilirsin.")
    except Exception as e:
        print(f"[!] KRİTİK HATA [HTML Inject]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    inject_html()
