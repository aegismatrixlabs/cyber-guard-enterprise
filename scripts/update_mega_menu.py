import os
import sys

def apply_mega_menu():
    print("[*] AegisMatrix CrowdStrike Tarzı Mega-Menu Mimarisi Ekleniyor...")
    try:
        css_path = "static/enterprise_theme.css"
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            
            mega_menu_css = """
/* CrowdStrike-Style Mega-Menu Dropdown */
.nav-dropdown {
    position: relative;
}
.nav-dropdown-content {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    min-width: 260px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
    padding: 10px;
    z-index: 1000;
}
.nav-dropdown:hover .nav-dropdown-content {
    display: block;
}
.dropdown-item {
    padding: 8px 12px;
    border-radius: 6px;
    transition: background-color 0.2s, color 0.2s;
    color: var(--text-secondary);
    text-decoration: none;
    display: block;
    font-size: 13px;
    font-weight: 500;
}
.dropdown-item:hover {
    background-color: var(--bg-hover);
    color: var(--text-primary);
}
"""
            if "nav-dropdown" not in css_content:
                with open(css_path, "a", encoding="utf-8") as f:
                    f.write("\n" + mega_menu_css)
                print("    [+] Başarılı: enterprise_theme.css içine mega-menu stilleri eklendi.")
            else:
                print("    [*] Bilgi: Mega-menu stilleri zaten mevcut.")
                
        print("\n[✔] Profesyonel Açılır Menü Mimarisi Başarıyla Tamamlandı.")
        
    except Exception as e:
        print(f"[!] KRİTİK HATA [Mega Menu]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    apply_mega_menu()
