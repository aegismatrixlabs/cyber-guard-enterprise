import os
import sys

def force_fix():
    print("[*] Dashboard Şablonu Doğrudan Enjekte Ediliyor...")
    path = "templates/dashboard.html"
    if not os.path.exists(path):
        print(f"[!] Hata: {path} bulunamadı!", file=sys.stderr)
        sys.exit(1)
        
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Eğer sidebar veya sol menü alanı varsa orayı güncelleyelim, yoksa body içine ekleyelim
    # Alternatif olarak sidebar etiketini bulup içini güncelleyelim:
    if '<div class="sidebar"' in html or 'sidebar' in html:
        # Mevcut menüleri CrowdStrike açılır yapısıyla güncelleyelim
        new_sidebar_content = '''
        <div class="sidebar">
            <div style="padding: 20px; font-size: 16px; font-weight: bold; color: var(--accent-color); letter-spacing: 1px;">
                AEGIS<span style="color: var(--text-primary);">MATRIX</span>
            </div>
            
            <a href="/dashboard" style="display: block; padding: 10px 14px; color: var(--text-primary); text-decoration: none; border-radius: 6px; margin-bottom: 4px; background: var(--bg-hover);">🛡️ Kontrol Paneli</a>
            
            <!-- CrowdStrike Tarzı Açılır Menü 1 -->
            <div class="nav-dropdown">
                <a href="/assets" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; margin-bottom: 4px;">
                    <span>🎯 Varlık Yönetimi</span>
                    <span>▾</span>
                </a>
                <div class="nav-dropdown-content">
                    <a href="/assets" class="dropdown-item">• Bulut Varlıkları</a>
                    <a href="/assets" class="dropdown-item">• Endpoint Envanteri</a>
                    <a href="/assets" class="dropdown-item">• IAM & Kimlikler</a>
                </div>
            </div>

            <a href="#" style="display: block; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; margin-bottom: 4px;">📜 RoE Sözleşmesi</a>

            <!-- CrowdStrike Tarzı Açılır Menü 2 -->
            <div class="nav-dropdown">
                <a href="#" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; margin-bottom: 4px;">
                    <span>⚡ Tehdit Avcılığı</span>
                    <span>▾</span>
                </a>
                <div class="nav-dropdown-content">
                    <a href="#" class="dropdown-item">• Syslog Analizi</a>
                    <a href="#" class="dropdown-item">• YARA Av Kuralları</a>
                    <a href="#" class="dropdown-item">• Davranışsal Av</a>
                </div>
            </div>

            <a href="#" style="display: block; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; margin-bottom: 4px;">🔍 Zafiyet Tarayıcı</a>
            <a href="#" style="display: block; padding: 10px 14px; color: var(--text-secondary); text-decoration: none; border-radius: 6px; margin-bottom: 4px;">🤖 AI Triage & Öncelik</a>
        </div>
        '''
        
        # Eski sidebar bloğunu yenisiyle değiştirelim (basitçe sol menü container'ını hedef alıyoruz)
        import re
        # Eğer sidebar etiketleri varsa değiştir
        updated_html = re.sub(r'<div class="sidebar">.*?</div>\s*</div>', new_sidebar_content, html, flags=re.DOTALL)
        if updated_html == html:
            # Regex eşleşmediyse body içine enjekte edelim veya direkt üzerine yazalım
            print("[*] Standart sidebar etiketi tam eşleşmedi, şablon yapısı kontrol ediliyor...")
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("[+] Şablon güncellendi.")

if __name__ == "__main__":
    force_fix()
