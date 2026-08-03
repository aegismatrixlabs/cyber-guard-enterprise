import os
import sys

def update_complete():
    print("[*] Dashboard Şablonu Tamamen Güncelleniyor...")
    path = "templates/dashboard.html"
    if not os.path.exists(path):
        print(f"[!] Hata: {path} bulunamadı!", file=sys.stderr)
        sys.exit(1)
        
    # Kusursuz CrowdStrike Tarzı Sol Menü Şablonu
    complete_html = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - AegisMatrix</title>
    <link rel="stylesheet" href="/static/enterprise_theme.css">
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        .sidebar {
            width: 240px;
            background-color: var(--bg-card);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 20px 10px;
            box-sizing: border-box;
            z-index: 10;
        }
        .main-content {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            background-color: var(--bg-primary);
        }
        .nav-link {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 14px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 6px;
            margin-bottom: 4px;
            font-weight: 500;
            font-size: 14px;
            transition: background 0.2s, color 0.2s;
        }
        .nav-link:hover, .nav-dropdown:hover > .nav-link {
            background-color: var(--bg-hover);
            color: var(--text-primary);
        }
        /* CrowdStrike Mega-Menu Dropdown */
        .nav-dropdown {
            position: relative;
        }
        .nav-dropdown-content {
            display: none;
            padding-left: 15px;
            margin-top: 4px;
            margin-bottom: 6px;
        }
        .nav-dropdown:hover .nav-dropdown-content {
            display: block;
        }
        .dropdown-item {
            display: block;
            padding: 6px 10px;
            color: var(--text-secondary);
            font-size: 13px;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s, color 0.2s;
        }
        .dropdown-item:hover {
            background-color: var(--bg-hover);
            color: var(--accent-color);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
        }
        .table-container {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            font-size: 13px;
        }
        th {
            color: var(--text-secondary);
            font-weight: 600;
        }
    </style>
</head>
<body>

    <!-- Sol Menü / Sidebar -->
    <div class="sidebar">
        <div style="padding: 10px 14px; font-size: 18px; font-weight: bold; color: var(--accent-color); letter-spacing: 1px; margin-bottom: 20px;">
            AEGIS<span style="color: var(--text-primary);">MATRIX</span>
        </div>
        
        <a href="/dashboard" class="nav-link" style="background: var(--bg-hover); color: var(--text-primary);">
            <span>🛡️ Kontrol Paneli</span>
        </a>
        
        <!-- Varlık Yönetimi Açılır Menü -->
        <div class="nav-dropdown">
            <a href="/assets" class="nav-link">
                <span>🎯 Varlık Yönetimi</span>
                <span>▾</span>
            </a>
            <div class="nav-dropdown-content">
                <a href="/assets" class="dropdown-item">• Bulut Varlıkları</a>
                <a href="/assets" class="dropdown-item">• Endpoint Envanteri</a>
                <a href="/assets" class="dropdown-item">• IAM & Kimlikler</a>
            </div>
        </div>

        <a href="#" class="nav-link">
            <span>📜 RoE Sözleşmesi</span>
        </a>

        <!-- Tehdit Avcılığı Açılır Menü -->
        <div class="nav-dropdown">
            <a href="#" class="nav-link">
                <span>⚡ Tehdit Avcılığı</span>
                <span>▾</span>
            </a>
            <div class="nav-dropdown-content">
                <a href="#" class="dropdown-item">• Syslog Analizi</a>
                <a href="#" class="dropdown-item">• YARA Av Kuralları</a>
                <a href="#" class="dropdown-item">• Davranışsal Av</a>
            </div>
        </div>

        <a href="#" class="nav-link">
            <span>🔍 Zafiyet Tarayıcı</span>
        </a>
        
        <a href="#" class="nav-link">
            <span>🤖 AI Triage & Öncelik</span>
        </a>

        <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-secondary);">
            <span>🟢 Çevrimiçi (SOC-01)</span>
            <a href="/logout" style="color: var(--accent-color); text-decoration: none;">Çıkış Yap</a>
        </div>
    </div>

    <!-- Ana İçerik Alanı -->
    <div class="main-content">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <div>
                <h1 style="margin: 0 0 5px 0; font-size: 24px; font-weight: 600;">Otonom Güvenlik Operasyon Merkezi</h1>
                <p style="margin: 0; color: var(--text-secondary); font-size: 14px;">AegisMatrix Labs Kurumsal Ar-Ge ve İzleme Paneli</p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #10b981; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600;">
                STATUS: PRODUCTION READY
            </div>
        </div>

        <!-- Metrik Kartları -->
        <div class="metric-grid">
            <div class="metric-card">
                <div style="color: var(--text-secondary); font-size: 13px; margin-bottom: 8px;">Aktif Varlıklar</div>
                <div style="font-size: 28px; font-weight: 700;">2</div>
            </div>
            <div class="metric-card">
                <div style="color: var(--text-secondary); font-size: 13px; margin-bottom: 8px;">AI Triage Kuyruğu</div>
                <div style="font-size: 28px; font-weight: 700; color: #60a5fa;">1</div>
            </div>
            <div class="metric-card">
                <div style="color: var(--text-secondary); font-size: 13px; margin-bottom: 8px;">RoE Yasal Onay</div>
                <div style="font-size: 14px; font-weight: 600; color: var(--accent-color); margin-top: 6px;">BEKLİYOR</div>
            </div>
            <div class="metric-card">
                <div style="color: var(--text-secondary); font-size: 13px; margin-bottom: 8px;">Tespit Edilen Tehditler</div>
                <div style="font-size: 28px; font-weight: 700; color: var(--accent-color);">2</div>
            </div>
        </div>

        <!-- Son Güvenlik Olayları Tablosu -->
        <div class="table-container">
            <h3 style="margin-top: 0; margin-bottom: 15px; font-size: 16px;">Son Güvenlik Olayları</h3>
            <table>
                <thead>
                    <tr>
                        <th>MODÜL / İŞLEM</th>
                        <th>HEDEF / KAYNAK</th>
                        <th>DURUM / TEHDİT SEVİYESİ</th>
                        <th>ZAMAN DAMGASI</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Tehdit Avcılığı</td>
                        <td style="color: #60a5fa;">firewall_syslog</td>
                        <td><span style="background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">HIGH (BLOCK)</span></td>
                        <td style="color: var(--text-secondary);">Az önce</td>
                    </tr>
                    <tr>
                        <td>AI Triage</td>
                        <td style="color: #60a5fa;">api.aegismatrixlabs.com</td>
                        <td><span style="background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">MITIGATED</span></td>
                        <td style="color: var(--text-secondary);">10 dk önce</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(complete_html)
    print("    [+] Başarılı: dashboard.html CrowdStrike mega-menu mimarisiyle yeniden yazıldı.")

if __name__ == "__main__":
    update_complete()
