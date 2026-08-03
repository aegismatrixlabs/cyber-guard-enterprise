import os
import sys

def inspect_sidebar():
    print("[*] Doğrudan İnceleme Başlatıldı...")
    path = "templates/dashboard.html"
    if not os.path.exists(path):
        print(f"[!] Hata: {path} bulunamadı!", file=sys.stderr)
        sys.exit(1)
        
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    target_line_idx = -1
    for idx, line in enumerate(lines):
        if "Varlık Yönetimi" in line:
            target_line_idx = idx
            print(f"    [✔] 'Varlık Yönetimi' şu satırda bulundu (Satır {idx + 1}):")
            # Etrafındaki satırları da gösterelim
            start = max(0, idx - 2)
            end = min(len(lines), idx + 3)
            for i in range(start, end):
                print(f"        {i+1}: {lines[i].strip()}")
            break
            
    if target_line_idx == -1:
        print("[!] 'Varlık Yönetimi' metni dashboard.html içinde bulunamadı!", file=sys.stderr)
        sys.exit(1)

    # Şimdi bu satırı ve etrafındaki konteyneri CrowdStrike açılır menü yapısıyla güncelleyelim
    # Önce CSS stillerinin head içinde olduğundan emin olalım
    full_content = "".join(lines)
    
    dropdown_css = """
    <style>
        /* CrowdStrike Sidebar Dropdown Fix */
        .cs-menu-item { position: relative; width: 100%; }
        .cs-submenu { display: none; padding-left: 15px; margin-top: 4px; margin-bottom: 6px; }
        .cs-menu-item:hover .cs-submenu { display: block !important; }
        .cs-sublink { display: block; padding: 6px 10px; color: var(--text-secondary); font-size: 13px; text-decoration: none; border-radius: 4px; transition: 0.2s; }
        .cs-sublink:hover { background-color: var(--bg-hover); color: var(--accent-color); }
    </style>
    """
    
    if "cs-menu-item" not in full_content:
        if "</head>" in full_content:
            full_content = full_content.replace("</head>", dropdown_css + "\n</head>")
            
        # Varlık Yönetimi'nin bulunduğu satırı ve etiketini güvenli bir şekilde saralım
        # Satırı doğrudan değiştiriyoruz
        target_line = lines[target_line_idx]
        
        replacement_block = f"""
            <!-- CrowdStrike Açılır Varlık Yönetimi Menüsü -->
            <div class="cs-menu-item">
                {target_line.strip()}
                <div class="cs-submenu">
                    <a href="/assets" class="cs-sublink">• Bulut Varlıkları</a>
                    <a href="/assets" class="cs-sublink">• Endpoint Envanteri</a>
                    <a href="/assets" class="cs-sublink">• IAM & Kimlikler</a>
                </div>
            </div>
"""
        lines[target_line_idx] = replacement_block
        
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        print("    [✔] Başarılı: Doğru satır tespit edildi ve CrowdStrike açılır menü yapısı enjekte edildi.")
    else:
        print("    [*] Bilgi: Açılır menü sınıfları zaten eklenmiş.")

if __name__ == "__main__":
    inspect_sidebar()
