import os
import sys

def apply_enterprise_ui():
    print("[*] AegisMatrix Kurumsal UI/UX Tasarım Sistemi Uygulanıyor...")
    
    # 1. Static CSS klasörünü kontrol et ve kurumsal tema dosyası oluştur
    os.makedirs("static", exist_ok=True)
    css_content = """
/* AegisMatrix Enterprise Dark Theme (CrowdStrike Inspired) */
:root {
    --bg-main: #0A0E17;
    --bg-card: #121824;
    --bg-hover: #1A2332;
    --border-color: #212D40;
    --text-primary: #F0F4F8;
    --text-secondary: #8A99AD;
    --accent-red: #D91424;
    --accent-red-hover: #F21D2F;
    --accent-green: #10B981;
    --accent-orange: #F59E0B;
}

body {
    background-color: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.enterprise-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease-in-out;
}

.enterprise-card:hover {
    border-color: rgba(217, 20, 36, 0.4);
}

.btn-enterprise-red {
    background-color: var(--accent-red);
    color: #FFFFFF;
    font-weight: 600;
    border-radius: 6px;
    transition: background-color 0.2s;
}

.btn-enterprise-red:hover {
    background-color: var(--accent-red-hover);
}

.ai-assistant-widget {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 360px;
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    z-index: 1000;
}
"""
    try:
        with open("static/enterprise_theme.css", "w", encoding="utf-8") as f:
            f.write(css_content)
        print("    [+] Başarılı: static/enterprise_theme.css oluşturuldu.")
        
        print("\n[✔] Kurumsal UI Tasarım Sistemi Başarıyla Entegre Edildi.")
    except Exception as e:
        print(f"[!] KRİTİK HATA [UI Update]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    apply_enterprise_ui()
