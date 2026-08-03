import os
import re

path = "templates/dashboard.html"
if not os.path.exists(path):
    print("Hata: templates/dashboard.html bulunamadı!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Önceki bozuk/dağınık enjeksiyonları temizleyelim
# Eski Varlık Yönetimi satırlarını ve çöp tag'leri standart haline getirelim
content = re.sub(r'<!-- CrowdStrike.*?-->', '', content, flags=re.DOTALL)
content = re.sub(r'<div class="cs-menu-item">.*?</div>\s*</div>', '', content, flags=re.DOTALL)
content = re.sub(r'<div class="dropdown-container">.*?</div>\s*</div>', '', content, flags=re.DOTALL)

# 2. Temiz CSS stillerini <head> içine ekleyelim (Eğer yoksa)
clean_css = """
<style>
    /* Temiz ve Kararlı Sidebar Dropdown Mimarisi */
    .sidebar-dropdown { position: relative; width: 100%; margin-bottom: 4px; }
    .sidebar-dropdown-toggle { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary, #94a3b8); text-decoration: none; border-radius: 6px; font-weight: 500; transition: 0.2s; }
    .sidebar-dropdown-toggle:hover { background-color: var(--bg-hover, #1e293b); color: var(--text-primary, #f8fafc); }
    .sidebar-submenu { display: none; padding-left: 15px; margin-top: 2px; margin-bottom: 4px; }
    .sidebar-dropdown:hover .sidebar-submenu { display: block; }
    .sidebar-subitem { display: block; padding: 6px 10px; color: var(--text-secondary, #94a3b8); font-size: 13px; text-decoration: none; border-radius: 4px; transition: 0.2s; }
    .sidebar-subitem:hover { background-color: var(--bg-hover, #1e293b); color: var(--accent-color, #38bdf8); }
</style>
</head>
"""

if "sidebar-dropdown" not in content:
    if "</head>" in content:
        content = content.replace("</head>", clean_css)

# 3. Sidebar içindeki düz "Varlık Yönetimi" linkini bulup temiz dropdown yapısıyla değiştirelim
# HTML'de Varlık Yönetimi linkinin geçebileceği olası kalıpları hedefleyelim
target_patterns = [
    r'<a[^>]*href=["\']/assets["\'][^>]*>.*?Varlık Yönetimi.*?</a>',
    r'<a[^>]*>.*?Varlık Yönetimi.*?</a>'
]

replacement_html = """
    <div class="sidebar-dropdown">
        <a href="/assets" class="sidebar-dropdown-toggle">
            <span>🎯 Varlık Yönetimi</span>
            <span>▾</span>
        </a>
        <div class="sidebar-submenu">
            <a href="/assets" class="sidebar-subitem">• Bulut Varlıkları</a>
            <a href="/assets" class="sidebar-subitem">• Endpoint Envanteri</a>
        </div>
    </div>
"""

replaced = False
for pattern in target_patterns:
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement_html, content, count=1, flags=re.DOTALL)
        replaced = True
        break

if replaced:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[✔] Başarılı: Dosyadaki tüm karmaşa temizlendi ve temiz açılır menü eklendi.")
else:
    print("[!] Uyarı: 'Varlık Yönetimi' hedef kalıbı bulunamadı, manuel kontrol gerekiyor.")

