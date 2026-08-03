import os

path = "templates/dashboard.html"
if not os.path.exists(path):
    print("Hata: templates/dashboard.html bulunamadı!")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
found = False

for line in lines:
    if "Varlık Yönetimi" in line and not found:
        found = True
        # Doğrudan satır içi stillerle tam çalışan CrowdStrike açılır menü bloğunu ekliyoruz
        indent = line[:len(line) - len(line.lstrip())]
        dropdown_block = f"""{indent}<div class="sidebar-dropdown" style="position: relative; margin-bottom: 4px;">
{indent}    <a href="/assets" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary, #94a3b8); text-decoration: none; border-radius: 6px; font-weight: 500; transition: 0.2s;">
{indent}        <span>🎯 Varlık Yönetimi</span>
{indent}        <span>▾</span>
{indent}    </a>
{indent}    <div class="sidebar-submenu" style="display: none; padding-left: 15px; margin-top: 2px; margin-bottom: 4px;">
{indent}        <a href="/assets" style="display: block; padding: 6px 10px; color: var(--text-secondary, #94a3b8); font-size: 13px; text-decoration: none; border-radius: 4px;">• Bulut Varlıkları</a>
{indent}        <a href="/assets" style="display: block; padding: 6px 10px; color: var(--text-secondary, #94a3b8); font-size: 13px; text-decoration: none; border-radius: 4px;">• Endpoint Envanteri</a>
{indent}    </div>
{indent}</div>
{indent}<style>
{indent}    .sidebar-dropdown:hover .sidebar-submenu {{ display: block !important; }}
{indent}    .sidebar-dropdown:hover > a {{ background-color: var(--bg-hover, #1e293b); color: var(--text-primary, #f8fafc); }}
{indent}</style>
"""
        new_lines.append(dropdown_block)
    else:
        # Eğer daha önce eklenmiş mükerrer satırlar varsa atlayalım
        if "sidebar-dropdown" in line and found:
            continue
        new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("[✔] Başarılı: Varlık Yönetimi satırı doğrudan açılır menü ile değiştirildi.")
