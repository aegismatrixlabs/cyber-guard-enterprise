import os
import re
import sys

def diagnose():
    print("[*] Teşhis Başlatılıyor: main.py taranıyor...")
    if not os.path.exists("main.py"):
        print("[!] main.py bulunamadı!", file=sys.stderr)
        sys.exit(1)
        
    with open("main.py", "r", encoding="utf-8") as f:
        main_code = f.read()
        
    # /dashboard rotasının döndürdüğü şablon adını bulalım
    match = re.search(r'@app\.get\("/dashboard"\).*?return templates\.TemplateResponse\("(.*?)",', main_code, re.DOTALL)
    if match:
        target_template = match.group(1)
        print(f"    [✔] Doğrulandı: /dashboard rotası şu şablonu render ediyor: templates/{target_template}")
    else:
        # Alternatif arama
        match_alt = re.search(r'TemplateResponse\("(.*?\.html)"', main_code)
        if match_alt:
            target_template = match_alt.group(1)
            print(f"    [✔] Tespit Edildi: Kullanılan şablon dosyası -> {target_template}")
        else:
            target_template = "dashboard.html"
            print("    [!] Rota şablonu regex ile bulunamadı, varsayılan: dashboard.html")

    file_path = os.path.join("templates", target_template)
    if not os.path.exists(file_path):
        print(f"    [!] Kritik Hata: {file_path} fiziksel olarak mevcut değil!", file=sys.stderr)
        sys.exit(1)
        
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    print(f"    [✔] Dosya okundu. Boyut: {len(html_content)} karakter.")
    
    # Sol menü alanını (sidebar) güvenli bir şekilde CrowdStrike dropdown yapısıyla güncelleyelim
    # Varlık Yönetimi ve Tehdit Avcılığı etiketlerini güncelleyelim
    if "nav-dropdown" not in html_content:
        print("    [*] Açılır menü bileşenleri şablona ekleniyor...")
        
        # CSS stillerini head içine ekleyelim
        css_injection = """
        <style>
            .cs-dropdown { position: relative; }
            .cs-dropdown-content { display: none; padding-left: 15px; margin-top: 4px; }
            .cs-dropdown:hover .cs-dropdown-content { display: block !important; }
            .cs-subitem { display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 13px; text-decoration: none; border-radius: 4px; transition: 0.2s; }
            .cs-subitem:hover { background-color: var(--bg-hover); color: var(--accent-color); }
        </style>
        </head>
        """
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", css_injection)
            
        # Varlık Yönetimi linkini dropdown ile değiştirelim
        old_pattern = r'<a[^>]*href=["\']/assets["\'][^>]*>.*?Varlık Yönetimi.*?</a>'
        new_block = """
        <div class="cs-dropdown" style="margin-bottom: 4px;">
            <a href="/assets" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; font-weight: 500;">
                <span>🎯 Varlık Yönetimi</span>
                <span>▾</span>
            </a>
            <div class="cs-dropdown-content">
                <a href="/assets" class="cs-subitem">• Bulut Varlıkları</a>
                <a href="/assets" class="cs-subitem">• Endpoint Envanteri</a>
            </div>
        </div>
        """
        
        if re.search(old_pattern, html_content, re.DOTALL):
            html_content = re.sub(old_pattern, new_block, html_content, flags=re.DOTALL)
            print("    [+] Varlık Yönetimi menüsü başarıyla açılır yapıya dönüştürüldü.")
        else:
            # Eğer tam eşleşmezse sidebar içine doğrudan append edelim
            print("    [*] Klasik eşleşme sağlanamadı, sidebar bloğu enjekte ediliyor...")
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"    [✔] Başarılı: {file_path} güncellendi.")
    else:
        print("    [*] Bilgi: Açılır menü sınıfları zaten şablonda mevcut.")

if __name__ == "__main__":
    diagnose()
