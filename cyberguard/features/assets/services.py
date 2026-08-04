import requests
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse

def deep_scan_url(url: str):
    try:
        r = requests.get(url, timeout=5)
        durum = "ACTIVE" if r.status_code == 200 else "INACTIVE"
        headers_dict = dict(r.headers)
    except:
        durum = "INACTIVE"
        headers_dict = {}

    ssl_days = -1
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                ssl_days = (expiry_date - datetime.now()).days
    except: pass

    headers_status = "N/A"
    if durum == "ACTIVE":
        required_headers = ['X-Frame-Options', 'Content-Security-Policy', 'Strict-Transport-Security']
        found_headers = [h for h in required_headers if h in headers_dict]
        headers_status = "SECURE" if len(found_headers) >= 2 else "MISSING"

    open_ports = []
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        for port in [80, 443, 22, 21]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex((hostname, port)) == 0: open_ports.append(str(port))
            sock.close()
    except: pass

    if durum == "INACTIVE": risk_skoru = "HIGH"
    elif ssl_days < 15 and ssl_days != -1: risk_skoru = "HIGH"
    elif headers_status == "MISSING": risk_skoru = "MEDIUM"
    else: risk_skoru = "LOW"

    return {"status": durum, "risk_score": risk_skoru, "ssl_days": ssl_days, "headers_status": headers_status, "open_ports": ", ".join(open_ports) if open_ports else "N/A"}
