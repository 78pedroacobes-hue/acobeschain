from flask import Flask, jsonify, render_template_string
import datetime, hashlib, time
app = Flask(__name__)

# --- TOKENS DE HUESO ---
TOKENS = [
    {"simbolo": "AGC", "nombre": "Acobes Gold Coin", "rol": "Gobernanza / Apex - Oro", "supply": "168 Billones"},
    {"simbolo": "ASC", "nombre": "Acobes Silver Coin", "rol": "Soberano / Catalogo IP - Plata", "supply": "1.05 Trillones"},
    {"simbolo": "AQC", "nombre": "Acobes Quartz Coin", "rol": "Computo / Cuantico - Cuarzo", "supply": "6.3 Trillones"},
    {"simbolo": "ACC", "nombre": "Acobes Copper Coin", "rol": "Comercio / Fisico - Cobre", "supply": "42 Trillones"},
    {"simbolo": "ADC", "nombre": "Acobes Diamond Coin", "rol": "Digital / Micro-pagos - Diamante", "supply": "294 Trillones"},
    {"simbolo": "AC", "nombre": "Acobes Coin", "rol": "Gas / Utilidad Base", "supply": "1.26 Cuatrillones"},
]

# --- MUSICA EN LA CADENA - SOLO METADATA, NO ARCHIVOS PESADOS ---
# Baby, we NEVER put MP3s in Render. Only title + hash. That's why it loads.
MUSICA = [
    {"title": "Apocalipsis 13", "file": "Apocalipsis_13.mp3", "sha256": "pendiente", "plays": 0},
    {"title": "Lirios Del Sur - Corte Suprema Master", "file": "Lirios_Del_Sur_Corte_Suprema_Master.wav", "sha256": "pendiente", "plays": 0},
    {"title": "No Me Ronquen", "file": "No_me_ronquen.wav", "sha256": "pendiente", "plays": 0},
]

HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AcobesChain</title>
<style>body{background:#050505;color:#fff;font-family:Arial;text-align:center;padding:20px}.box{border:1px solid #00ffcc;padding:20px;border-radius:15px;max-width:700px;margin:20px auto}.boton{background:#00ffcc;color:#000;padding:12px 25px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:5px}</style>
</head><body><h1>ACOBESCHAIN</h1><p>Espejo de Agarta - Soberano</p>
<div class="box"><p>PUERTA: ABIERTA | VAULT: ACTIVO | CANALES: 21 / 21</p><p>CHAIN: acobes-mainnet-1 | DUENO: Pedro J. Acobes</p></div>
<a class="boton" href="/tokens">VER TOKENS</a><a class="boton" href="/musica">VER MUSICA</a><a class="boton" href="/api/cadena">VER CADENA</a>
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/tokens")
def tokens_page():
    h = "<h1>TOKENS SOBERANOS</h1><a href='/'>VOLVER</a><br><br>"
    for t in TOKENS:
        h += f"<div style='border:1px solid #00ffcc;padding:10px;margin:10px auto;max-width:500px;text-align:left'><b>{t['simbolo']} - {t['nombre']}</b><br>Rol: {t['rol']}<br>Supply: {t['supply']}</div>"
    return h

@app.route("/musica")
def musica_page():
    h = "<h1 style='text-align:center'>MUSICA - ACOBESCHAIN</h1><p style='text-align:center'>Solo metadata en cadena. Musica NO cargada en Render.</p><a href='/'>VOLVER</a><br><br>"
    for m in MUSICA:
        h += f"<div style='border:1px solid #00ffcc;padding:10px;margin:10px auto;max-width:500px;background:#111;color:#fff;text-align:left'><b>{m['title']}</b><br>File: {m['file']}<br>Hash: {m['sha256']}<br>Plays REALES: {m['plays']}</div>"
    return h

@app.route("/api/cadena")
def cadena():
    return jsonify({"nombre": "AcobesChain", "chain_id": "acobes-mainnet-1", "estado": "VISIBLE", "puerta": "ABIERTA", "hora": datetime.datetime.now().isoformat()})

@app.route("/api/musica")
def api_musica():
    return jsonify({"chain": "acobes-mainnet-1", "hub": "https://acobeschain.onrender.com", "total": len(MUSICA), "musica": MUSICA})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "cadena": "viva"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
