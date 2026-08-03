import os

path = "templates/dashboard.html"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Sidebar veya Varlık Yönetimi geçişinin olduğu bölgeyi bulup yazdıralım
    start_pos = content.find("Varlık Yönetimi")
    if start_pos != -1:
        snippet = content[max(0, start_pos - 300):min(len(content), start_pos + 400)]
        print("--- Varlık Yönetimi Çevresindeki HTML Yapısı ---")
        print(snippet)
    else:
        print("Varlık Yönetimi bulunamadı.")
