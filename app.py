from flask import Flask, jsonify
app = Flask(__name__)

TOKENS = [
    {"simbolo": "AGC", "nombre": "Acobes Gold Coin", "rol": "Gobernanza - Oro"},
    {"simbolo": "ASC", "nombre": "Acobes Silver Coin", "rol": "Soberano - Plata"},
    {"simbolo": "AQC", "nombre": "Acobes Quartz Coin", "rol": "Computo - Cuarzo"},
    {"simbolo": "ACC", "nombre": "Acobes Copper Coin", "rol": "Comercio - Cobre"},
    {"simbolo": "ADC", "nombre": "Acobes Diamond Coin", "rol": "Digital - Diamante"},
    {"simbolo": "AC", "nombre": "Acobes Coin", "rol": "Gas Base"},
]

MUSICA = [
    {"title": "Apocalipsis 13", "file": "Apocalipsis_13.mp3", "sha256": "pendiente", "plays": 0},
    {"title": "Lirios Del Sur - Corte Suprema Master", "file": "Lirios_Del_Sur_Corte_Suprema_Master.wav", "sha256": "pendiente", "plays": 0},
    {"title": "No Me Ronquen", "file": "No_me_ronquen.wav", "sha256": "pendiente", "plays": 0},
]

@app.route("/")
def home():
    return """<h1 style='text-align:center'>ACOBESCHAIN VIVA</h1>
    <p style='text-align:center'>Puerta ABIERTA | Vault ACTIVO | Pedro J. Acobes</p>
    <p style='text-align:center'><a href='/tokens'>TOKENS</a> | <a href='/musica'>MUSICA</a> | <a href='/health'>HEALTH</a></p>"""

@app.route("/tokens")
def tokens_page():
    h = "<h1>TOKENS SOBERANOS</h1><a href='/'>VOLVER</a><br><br>"
    for t in TOKENS:
        h += f"<div style='border:1px solid #00ffcc;padding:10px;margin:10px'><b>{t['simbolo']} - {t['nombre']}</b><br>Rol: {t['rol']}</div>"
    return h

@app.route("/musica")
def musica_page():
    h = "<h1 style='text-align:center'>MUSICA - ACOBESCHAIN</h1><p style='text-align:center'>Arquitectura Records LLC - Cadena Soberana</p><a href='/'>VOLVER</a><br><br>"
    for m in MUSICA:
        h += f"<div style='border:1px solid #00ffcc;padding:10px;margin:10px;background:#111;color:#fff'><b>{m['title']}</b><br>File: {m['file']}<br>Hash: {m['sha256']}<br>Plays: {m['plays']}</div>"
    return h

@app.route("/api/musica")
def api_musica():
    return jsonify({"chain": "acobes-mainnet-1", "total": len(MUSICA), "musica": MUSICA})

@app.route("/health")
def health():
    return {"status": "ok", "cadena": "viva"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
