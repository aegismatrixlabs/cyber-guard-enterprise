import sqlite3
from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('arge_lab.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zaman TEXT NOT NULL,
            icerik TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/gonder', methods=['POST'])
def gonder_veri():
    try:
        data = request.json
        mesaj = data.get('veri', '')
        zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('arge_lab.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO kayitlar (zaman, icerik) VALUES (?, ?)', (zaman, mesaj))
        conn.commit()
        conn.close()
        
        return jsonify({'durum': 'basarili', 'zaman': zaman, 'icerik': mesaj})
    except Exception as e:
        print(f"SUNUCU HATASI: {e}")
        return jsonify({'durum': 'hata', 'mesaj': str(e)}), 500

@app.route('/api/veriler', methods=['GET'])
def verileri_getir():
    conn = sqlite3.connect('arge_lab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT zaman, icerik FROM kayitlar ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    veri_listesi = []
    for row in rows:
        veri_listesi.append({'zaman': row[0], 'icerik': row[1]})
        
    return jsonify(veri_listesi)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
