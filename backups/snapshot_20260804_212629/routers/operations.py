from fastapi import APIRouter, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional
from database.store import DATABASE

router = APIRouter(tags=["Operations"])

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in DATABASE["sessions"]:
        return RedirectResponse(url="/login", status_code=303)
    
    roe_badge = '<span class="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-xs font-semibold border border-emerald-500/20">ONAYLANDI</span>' if DATABASE["roe"]["status"] else '<span class="px-2.5 py-1 bg-rose-500/10 text-rose-400 rounded-full text-xs font-semibold border border-rose-500/20">BEKLİYOR</span>'
    threat_rows = "".join([f'<tr class="border-b border-slate-800 text-sm hover:bg-slate-900/50"><td class="py-3 px-4 text-slate-300">{log["module"]}</td><td class="py-3 px-4 font-mono text-emerald-400">{log["target"]}</td><td class="py-3 px-4"><span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">{log["status"]}</span></td><td class="py-3 px-4 text-slate-400">{log["time"]}</td></tr>' for log in DATABASE["threat_logs"]])
    
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head><meta charset="UTF-8"><title>Dashboard - AegisMatrix</title><script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen">
        <div class="flex h-screen overflow-hidden">
            <aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
                <div class="p-6">
                    <div class="flex items-center space-x-3 mb-8">
                        <div class="h-3 w-3 bg-emerald-500 rounded-full animate-pulse"></div>
                        <span class="text-xl font-bold tracking-wider text-white">AEGIS<span class="text-emerald-400">MATRIX</span></span>
                    </div>
                    <nav class="space-y-1.5">
                        <a href="/dashboard" class="flex items-center space-x-3 px-4 py-3 bg-slate-800 text-emerald-400 rounded-lg font-medium">🛡️ <span>Kontrol Paneli</span></a>
                        <a href="/assets-ui" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg transition">🎯 <span>Varlık Yönetimi</span></a>
                        <a href="/roe-ui" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg transition">📜 <span>RoE Sözleşmesi</span></a>
                        <a href="/threat-hunting-ui" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg transition">⚡ <span>Tehdit Avcılığı</span></a>
                        <a href="/scanner-ui" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg transition">🔍 <span>Zafiyet Tarayıcı</span></a>
                        <a href="/triage-ui" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg transition">🤖 <span>AI Triage & Öncelik</span></a>
                    </nav>
                </div>
                <div class="p-6 border-t border-slate-800 flex justify-between items-center text-xs">
                    <span class="text-emerald-400 font-medium">● Çevrimiçi (SOC-01)</span>
                    <a href="/logout" class="text-rose-400 hover:underline">Çıkış Yap</a>
                </div>
            </aside>
            <main class="flex-1 overflow-y-auto p-8">
                <header class="flex justify-between items-center mb-8">
                    <div>
                        <h1 class="text-2xl font-bold text-white">Otonom Güvenlik Operasyon Merkezi</h1>
                        <p class="text-sm text-slate-400">AegisMatrix Labs Kurumsal Ar-Ge ve İzleme Paneli</p>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 px-4 py-2 rounded-lg text-xs font-mono text-emerald-400">STATUS: PRODUCTION READY</div>
                </header>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
                        <p class="text-slate-400 text-sm">Aktif Varlıklar</p>
                        <h3 class="text-3xl font-bold text-white mt-2">{len(DATABASE["assets"])}</h3>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
                        <p class="text-slate-400 text-sm">AI Triage Kuyruğu</p>
                        <h3 class="text-3xl font-bold text-indigo-400 mt-2">{len(DATABASE["triage"])}</h3>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
                        <p class="text-slate-400 text-sm">RoE Yasal Onay</p>
                        <h3 class="text-xl font-bold text-white mt-2">{roe_badge}</h3>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
                        <p class="text-slate-400 text-sm">Tespit Edilen Tehditler</p>
                        <h3 class="text-3xl font-bold text-rose-400 mt-2">{len(DATABASE["threat_logs"])}</h3>
                    </div>
                </div>
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
                    <h3 class="text-lg font-semibold mb-4 text-white">Son Güvenlik Olayları</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                                    <th class="py-3 px-4">Modül / İşlem</th>
                                    <th class="py-3 px-4">Hedef / Kaynak</th>
                                    <th class="py-3 px-4">Durum / Tehdit Seviyesi</th>
                                    <th class="py-3 px-4">Zaman Damgası</th>
                                </tr>
                            </thead>
                            <tbody>{threat_rows}</tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    </body>
    </html>
    """

@router.get("/roe-ui", response_class=HTMLResponse)
async def roe_ui(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in DATABASE["sessions"]:
        return RedirectResponse(url="/login", status_code=303)
    is_approved = DATABASE["roe"]["status"]
    status_badge = '<span class="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-sm font-semibold border border-emerald-500/20">ONAYLANDI</span>' if is_approved else '<span class="px-3 py-1 bg-rose-500/10 text-rose-400 rounded-full text-sm font-semibold border border-rose-500/20">ONAY BEKLİYOR</span>'
    action_section = "" if is_approved else '<form action="/api/roe/accept" method="POST" class="space-y-4 pt-4 border-t border-slate-800"><button type="submit" class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-lg font-semibold transition cursor-pointer">RoE Sözleşmesini Onayla</button></form>'
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head><meta charset="UTF-8"><title>RoE - AegisMatrix</title><script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8">
        <div class="max-w-4xl mx-auto">
            <div class="flex justify-between items-center mb-8">
                <h1 class="text-2xl font-bold text-white">📜 RoE Sözleşmesi</h1>
                <a href="/dashboard" class="text-sm text-emerald-400 hover:underline">← Panele Dön</a>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl mb-8 shadow-lg flex justify-between items-center">
                <h3 class="text-lg font-semibold text-white">Onay Durumu</h3>
                {status_badge}
            </div>
            <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg space-y-4">
                <p class="text-sm text-slate-300">Bu sözleşme otonom testler için yasal kalkan oluşturur.</p>
                {action_section}
            </div>
        </div>
    </body>
    </html>
    """

@router.post("/api/roe/accept")
async def roe_accept(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in DATABASE["sessions"]:
        return RedirectResponse(url="/login", status_code=303)
    DATABASE["roe"]["status"] = True
    DATABASE["roe"]["accepted_by"] = DATABASE["sessions"][session_token]
    DATABASE["roe"]["timestamp"] = str(datetime.utcnow())[:19]
    return RedirectResponse(url="/roe-ui", status_code=303)

@router.get("/threat-hunting-ui", response_class=HTMLResponse)
async def threat_ui(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in DATABASE["sessions"]:
        return RedirectResponse(url="/login", status_code=303)
    logs_html = "".join([f'<tr class="border-b border-slate-800 text-sm"><td class="py-3 px-4 text-slate-300">{l["module"]}</td><td class="py-3 px-4 font-mono text-emerald-400">{l["target"]}</td><td class="py-3 px-4 text-rose-400">{l["status"]}</td><td class="py-3 px-4 text-slate-400">{l["time"]}</td></tr>' for l in DATABASE["threat_logs"]])
    return f"""
    <!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>Tehdit Avcılığı</title><script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8"><div class="max-w-4xl mx-auto"><div class="flex justify-between items-center mb-8"><h1 class="text-2xl font-bold text-white">⚡ Tehdit Avcılığı</h1><a href="/dashboard" class="text-sm text-emerald-400 hover:underline">← Panele Dön</a></div>
    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg"><table class="w-full text-left"><tbody>{logs_html}</tbody></table></div></div></body></html>
    """

@router.get("/scanner-ui", response_class=HTMLResponse)
async def scanner_ui(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in DATABASE["sessions"]:
        return RedirectResponse(url="/login", status_code=303)
    scans_html = "".join([f'<tr class="border-b border-slate-800 text-sm"><td class="py-3 px-4 font-mono text-emerald-400">{s["target"]}</td><td class="py-3 px-4 text-slate-300">{s["type"]}</td><td class="py-3 px-4 text-emerald-400">{s["status"]}</td><td class="py-3 px-4 text-rose-400">{s["findings"]}</td></tr>' for s in DATABASE["scans"]])
    return f"""
    <!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>Zafiyet Tarayıcı</title><script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8"><div class="max-w-4xl mx-auto"><div class="flex justify-between items-center mb-8"><h1 class="text-2xl font-bold text-white">🔍 Zafiyet Tarayıcı</h1><a href="/dashboard" class="text-sm text-emerald-400 hover:underline">← Panele Dön</a></div>
    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg"><table class="w-full text-left"><tbody>{scans_html}</tbody></table></div></div></body></html>
    """

@router.get("/triage-ui", response_class=HTMLResponse)
async def triage_ui(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in DATABASE["sessions"]:
        return RedirectResponse(url="/login", status_code=303)
    triage_html = "".join([f'<tr class="border-b border-slate-800 text-sm"><td class="py-3 px-4 font-mono text-emerald-400">{t["target"]}</td><td class="py-3 px-4 text-slate-300">{t["finding"]}</td><td class="py-3 px-4 text-indigo-400 font-bold">{t["ai_score"]}</td><td class="py-3 px-4 text-emerald-400">{t["status"]}</td></tr>' for t in DATABASE["triage"]])
    return f"""
    <!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>AI Triage</title><script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script></head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8"><div class="max-w-4xl mx-auto"><div class="flex justify-between items-center mb-8"><h1 class="text-2xl font-bold text-white">🤖 AI Triage</h1><a href="/dashboard" class="text-sm text-emerald-400 hover:underline">← Panele Dön</a></div>
    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg"><table class="w-full text-left"><tbody>{triage_html}</tbody></table></div></div></body></html>
    """
