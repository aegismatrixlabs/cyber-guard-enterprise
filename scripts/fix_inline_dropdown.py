import os
import sys

def apply_inline_fix():
    print("[*] Doğrudan Dahili (Inline) Mega-Menu Enjeksiyonu Başlatıldı...")
    path = "templates/dashboard.html"
    if not os.path.exists(path):
        print(f"[!] Hata: {path} bulunamadı!", file=sys.stderr)
        sys.exit(1)
        
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Eğer head etiketi varsa içine garantili CSS stillerini ekleyelim
    inline_styles = """
    <style>
        /* Kesin Çalışan Mega-Menu Stilleri */
        .dropdown-container { position: relative; width: 100%; }
        .dropdown-content { display: none; padding-left: 15px; margin-top: 4px; }
        .dropdown-container:hover .dropdown-content { display: block !important; }
        .dropdown-subitem { display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 13px; text-decoration: none; border-radius: 4px; }
        .dropdown-subitem:hover { background-color: var(--bg-hover); color: var(--accent-color); }
    </style>
    </head>
    """
    
    if "</head>" in html and "dropdown-container" not in html:
        html = html.replace("</head>", inline_styles)
        
        # Sol menüdeki Varlık Yönetimi linkini dropdown yapısıyla değiştirelim
        old_asset_link = '<a href="/assets"'
        new_asset_block = """
        <div class="dropdown-container">
            <a href="/assets" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; margin-bottom: 4px; font-weight: 500;">
                <span>🎯 Varlık Yönetimi</span>
                <span>▾</span>
            </a>
            <div class="dropdown-content">
                <a href="/assets" class="dropdown-subitem">• Bulut Varlıkları</a>
                <a href="/assets" class="dropdown-subitem">• Endpoint Envanteri</a>
            </div>
        </div>
        """
        
        # Varlık yönetimi yazısını içeren alanı güncelleyelim
        if 'Varlık Yönetimi' in html:
            import re
            # Mevcut Varlık Yönetimi linkini bulup dropdown ile değiştirelim
            html = re.sub(r'<a[^>]*>.*?Varlık Yönetimi.*?</a>', new_asset_block, html, flags=re.DOTALL)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("    [+] Başarılı: Dahili stiller ve açılır menü şablona işlendi.")
    else:
        print("    [*] Bilgi: Zaten eklenmiş veya head etiketi bulunamadı.")

if __name__ == "__main__":
    apply_inline_fix()
