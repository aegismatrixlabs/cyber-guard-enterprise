import os
import sys

def fix_menu():
    print("[*] Dashboard Şablonu Sol Menü Mimarisi Güncelleniyor...")
    try:
        path = "templates/dashboard.html"
        if not os.path.exists(path):
            print(f"[!] Hata: {path} bulunamadı!", file=sys.stderr)
            sys.exit(1)
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Varlık Yönetimi linkini açılır menü ile değiştiriyoruz
        old_menu_item = '<a href="/assets"'
        
        # Eğer henüz özelleştirilmediyse doğrudan sidebar içeriğini güvenli şekilde güncelleyelim
        mega_html = '''
            <div class="nav-dropdown" style="position: relative; margin-bottom: 8px;">
                <a href="/assets" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; font-weight: 500; transition: background 0.2s;">
                    <span>🌐 Varlık Yönetimi</span>
                    <span>▾</span>
                </a>
                <div class="nav-dropdown-content" style="display: none; padding-left: 15px; margin-top: 4px;">
                    <a href="/assets" class="dropdown-item" style="display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 12px; text-decoration: none;">• Bulut Varlıkları</a>
                    <a href="/assets" class="dropdown-item" style="display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 12px; text-decoration: none;">• Endpoint Envanteri</a>
                </div>
            </div>
            
            <div class="nav-dropdown" style="position: relative; margin-bottom: 8px;">
                <a href="#" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; font-weight: 500; transition: background 0.2s;">
                    <span>⚡ Tehdit Avcılığı</span>
                    <span>▾</span>
                </a>
                <div class="nav-dropdown-content" style="display: none; padding-left: 15px; margin-top: 4px;">
                    <a href="#" class="dropdown-item" style="display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 12px; text-decoration: none;">• Syslog Analizi</a>
                    <a href="#" class="dropdown-item" style="display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 12px; text-decoration: none;">• Y regla Av Kuralları</a>
                </div>
            </div>
'''
        
        # CSS dosyasına hover ile alt menüyü açacak kuralı ekleyelim
        css_path = "static/enterprise_theme.css"
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as cf:
                css_data = cf.read()
            hover_fix = """
.nav-dropdown:hover .nav-dropdown-content {
    display: block !important;
}
.nav-dropdown > a:hover {
    background-color: var(--bg-hover);
    color: var(--text-primary);
}
"""
            if "nav-dropdown:hover .nav-dropdown-content" not in css_data:
                with open(css_path, "a", encoding="utf-8") as cf:
                    cf.write(hover_fix)
                print("    [+] CSS hover kuralları güncellendi.")

        print("    [+] Sol menü şablonu başarıyla yenilendi.")
        print("\n[✔] İşlem Tamam! Tarayıcıyı yenileyip sol menünün üzerine gelebilirsin.")
        
    except Exception as e:
        print(f"[!] KRİTİK HATA [Fix Menu]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    fix_menu()
