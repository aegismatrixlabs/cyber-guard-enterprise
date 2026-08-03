import os
import sys

def inject_theme_and_run():
    print("[*] AegisMatrix Kurumsal Tema Şablona Entegre Ediliyor...")
    try:
        dashboard_path = "templates/dashboard.html"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            css_tag = '<link rel="stylesheet" href="/static/enterprise_theme.css">'
            if css_tag not in content:
                if "</head>" in content:
                    content = content.replace("</head>", f"    {css_tag}\n</head>")
                else:
                    content = css_tag + "\n" + content
                
                with open(dashboard_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("    [+] Başarılı: enterprise_theme.css dashboard.html dosyasına eklendi.")
            else:
                print("    [*] Bilgi: Kurumsal tema şablonda zaten tanımlı.")
        else:
            print(f"    [!] Uyarı: {dashboard_path} bulunamadı, şablon atlandı.")
            
        print("\n[✔] Kurumsal Panel Hazır! Sunucu başlatılıyor...")
        
    except Exception as e:
        print(f"[!] KRİTİK HATA [Theme Link]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    inject_theme_and_run()
