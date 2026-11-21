from flask import Flask, jsonify, render_template_string
import datetime
app = Flask(__name__)
try:
    from tokens import TOKENS, GENESIS, CATALOGO
except:
    TOKENS = []
    GENESIS = {"chain_id": "acobes-mainnet-1", "consensus": "Proof-of-Architect (DPoS)", "owner": "Pedro J. Acobes"}
    CATALOGO = []
CADENA = {"nombre": "AcobesChain", "dominio": "acobeschain.com", "origen": "Agarta - Consola Principal", "estado": "VISIBLE", "puerta": "ABIERTA", "vault": "ACTIVO", "canales": 21}
CANALES = [f"Canal {i+1:02d} - Activo" for i in range(21)]
HTML = """
<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AcobesChain - Puerta Abierta</title>
<style>body{background:#050505;color:#fff;font-family:Arial;text-align:center;padding:20px}h1{font-size:42px;letter-spacing:3px}.box{border:1px solid #00ffcc;padding:20px;border-radius:15px;max-width:700px;margin:20px auto}.boton{background:#00ffcc;color:#000;padding:12px 25px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:5px}.boton2{background:#fff;color:#000;padding:12px 25px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:5px}</style>
</head><body><h1>ACOBESCHAIN</h1><p>Espejo de Agarta en la Superficie - Soberano</p>
<div class="box"><p>PUERTA: ABIERTA | VAULT: ACTIVO | CANALES: 21 / 21</p><p>DOMINIO: acobeschain.com | CHAIN: acobes-mainnet-1</p><p>DUENO: Pedro J. Acobes - Acobes Industries Inc.</p><p id="hora"></p></div>
<a class="boton" href="/tokens">VER MIS TOKENS</a><a class="boton2" href="/catalogo">VER MI CATALOGO MUSICAL</a><br><br><a class="boton" href="/api/cadena">VER CADENA EN VIVO</a>
<script>document.getElementById('hora').innerText = new Date().toLocaleString();</script></body></html>
"""
TOKENS_HTML = """
<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Tokens - AcobesChain</title>
<style>body{background:#050505;color:#fff;font-family:Arial;text-align:center;padding:20px}.card{border:1px solid #00ffcc;padding:15px;border-radius:12px;margin:10px auto;max-width:600px;text-align:left}.boton{background:#00ffcc;color:#000;padding:10px 20px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:5px}</style>
</head><body><h1>TOKENS SOBERANOS - ACOBESCHAIN</h1><p>Chain: acobes-mainnet-1 | Consenso: Proof-of-Architect (DPoS) | Precio de Apertura - Mercado Propio</p><a class="boton" href="/">VOLVER A LA PUERTA</a>
{% for t in tokens %}<div class="card"><h2>{{t.simbolo}} - {{t.nombre}}</h2><p>Rol: {{t.rol}}</p><p>Supply Conceptual: {{t.supply}}</p><p>Precio Soberano: {{t.precio_conceptual}}</p><p>Red: AcobesChain - No Solana, No Ethereum</p></div>{% endfor %}
<p style="font-size:12px;opacity:0.7">Precio de Apertura de Mercado Propio AcobesChain. Valor Soberano Inmutable fijado en Genesis por Pedro J. Acobes, Arquitecto. Mercado interno soberano. Esta cadena no pide permiso a mercados externos.</p></body></html>
"""
CATALOGO_HTML = """
<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Catalogo - AcobesChain</title>
<style>body{background:#050505;color:#fff;font-family:Arial;text-align:center;padding:20px}.card{border:1px solid #ffcc00;padding:15px;border-radius:12px;margin:10px auto;max-width:600px;text-align:left}.boton{background:#00ffcc;color:#000;padding:10px 20px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:5px}</style>
</head><body><h1>CATALOGO MUSICAL - PEDRO J. ACOBES</h1><p>Arquitectura Records LLC | Soberano 100% del Catalogo</p><a class="boton" href="/">VOLVER A LA PUERTA</a>
{% for c in catalogo %}<div class="card"><h2>{{c.titulo}}</h2><p>Archivo: {{c.archivo}}</p><p>Dueno: Pedro J. Acobes | Estado: Master Propio</p></div>{% endfor %}</body></html>
"""
@app.route("/")
def home():
    return render_template_string(HTML)
@app.route("/tokens")
def tokens_page():
    return render_template_string(TOKENS_HTML, tokens=TOKENS)
@app.route("/catalogo")
def catalogo_page():
    return render_template_string(CATALOGO_HTML, catalogo=CATALOGO)
@app.route("/api/cadena")
def cadena():
    return jsonify({**CADENA, "hora_superficie": datetime.datetime.now().isoformat(), "canales": CANALES, "genesis": GENESIS})
@app.route("/api/tokens")
def api_tokens():
    return jsonify({"chain_id": GENESIS["chain_id"], "owner": GENESIS["owner"], "tokens": TOKENS, "nota": "Precio de Apertura - Mercado Propio"})
@app.route("/api/catalogo")
def api_catalogo():
    return jsonify({"artista": "Pedro J. Acobes", "sello": "Arquitectura Records LLC", "total": len(CATALOGO), "catalogo": CATALOGO})
@app.route("/api/puerta")
def puerta():
    return jsonify({"puerta": "ABIERTA", "mensaje": "La puerta de Agarta esta visible en la superficie"})
@app.route("/api/vault")
def vault():
    return jsonify({"vault": "ACTIVO", "mensaje": "Vault protegido - solo lectura publica"})
@app.route("/health")
def health():
    return jsonify({"status": "ok", "cadena": "viva"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
