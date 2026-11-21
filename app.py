from flask import Flask, jsonify, render_template_string, request
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
DECRETO = "Decreto del Arquitecto: AcobesChain nace para reemplazar el sistema antiguo de operar. Precio de Apertura de Mercado Propio AcobesChain. Valor Soberano Inmutable fijado en Genesis por Pedro J. Acobes. Mercado interno soberano. Esta cadena no pide permiso a mercados externos."
RESERVAS = []

BASE_CSS = """
<style>
*{box-sizing:border-box} body{background:#050505;color:#fff;font-family:Arial,Helvetica,sans-serif;margin:0;padding:0;text-align:center}
.top{padding:28px 16px 10px} h1{font-size:44px;letter-spacing:6px;margin:0;background:linear-gradient(90deg,#FFD700,#00ffcc);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{opacity:.8;margin-top:6px} .pill{display:inline-block;border:1px solid #00ffcc;color:#00ffcc;padding:6px 14px;border-radius:30px;font-size:12px;margin:4px}
.pill-gold{border-color:#FFD700;color:#FFD700}
.wrap{max-width:780px;margin:0 auto;padding:16px}
.box{border:1px solid #222;background:#0d0d0d;padding:20px;border-radius:18px;margin:16px 0;text-align:left}
.card{border:1px solid #2a2a2a;background:linear-gradient(180deg,#111,#080808);padding:18px;border-radius:18px;margin:14px 0;text-align:left;box-shadow:0 10px 30px rgba(0,0,0,.5)}
.card h2{margin:0 0 6px} .precio{font-size:28px;color:#FFD700;font-weight:bold} .tag{font-size:12px;opacity:.7}
.boton{background:#00ffcc;color:#000;padding:13px 22px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:6px}
.boton-gold{background:#FFD700;color:#000;padding:13px 22px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:6px}
.boton-white{background:#fff;color:#000;padding:13px 22px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block;margin:6px}
input,select{width:100%;padding:13px;border-radius:12px;border:1px solid #333;background:#111;color:#fff;margin:8px 0;font-size:16px}
label{font-size:13px;opacity:.8;text-align:left;display:block}
.decreto{border:1px solid #FFD700;background:#141000;padding:16px;border-radius:14px;font-size:14px;line-height:1.5}
.paso{font-size:42px} .footer{opacity:.5;font-size:12px;padding:20px}
</style>
"""

HOME = BASE_CSS + """
<div class="top"><h1>ACOBESCHAIN</h1><div class="sub">Espejo de Agarta en la Superficie — Soberano</div>
<div style="margin-top:12px"><span class="pill">PUERTA: ABIERTA</span><span class="pill">VAULT: ACTIVO</span><span class="pill pill-gold">CANALES: 21 / 21</span></div></div>
<div class="wrap">
<div class="box"><b>DOMINIO:</b> acobeschain.com &nbsp;|&nbsp; <b>CHAIN:</b> acobes-mainnet-1<br><b>DUEÑO:</b> Pedro J. Acobes — Acobes Industries Inc.<br><b>ESTADO:</b> Visible en superficie</div>
<div class="decreto">{{decreto}}</div>
<div style="margin:18px 0"><a class="boton-gold" href="/comprar">QUIERO ADQUIRIR TOKENS</a><br><a class="boton" href="/tokens">VER MIS 6 TOKENS</a><a class="boton-white" href="/catalogo">VER MI CATÁLOGO</a></div>
<div class="box"><h3>¿Cómo se adquiere?</h3><p>1. Entras a <b>Quiero Adquirir</b><br>2. Eliges tu metal<br>3. Dejas tu contacto y quedas en la Lista Soberana<br>4. El Arquitecto te contacta para el acceso</p><p class="tag">Mercado Propio AcobesChain. Adquisición por reserva y acceso soberano.</p></div>
<div class="footer">© Acobes Industries Inc. / Arquitectura Records LLC — Pedro J. Acobes</div></div>
"""

TOKENS_PAGE = BASE_CSS + """
<div class="top"><h1>TOKENS SOBERANOS</h1><div class="sub">Chain: acobes-mainnet-1 | Consenso: Proof-of-Architect (DPoS)</div></div>
<div class="wrap"><div class="decreto">{{decreto}}</div><br><a class="boton" href="/">VOLVER</a><a class="boton-gold" href="/comprar">ADQUIRIR</a>
{% for t in tokens %}<div class="card"><div class="tag">{{t.rol}}</div><h2>{{t.simbolo}} — {{t.nombre}}</h2><div class="precio">{{t.precio_conceptual}}</div><p>Supply: {{t.supply}}<br>Red: AcobesChain — No Solana, No Ethereum</p><a class="boton" href="/comprar?token={{t.simbolo}}">ADQUIRIR {{t.simbolo}}</a></div>{% endfor %}
</div>
"""

CATALOGO_PAGE = BASE_CSS + """
<div class="top"><h1>CATÁLOGO MUSICAL</h1><div class="sub">Pedro J. Acobes | Arquitectura Records LLC — Soberano 100%</div></div>
<div class="wrap"><a class="boton" href="/">VOLVER</a><a class="boton-gold" href="/comprar">ADQUIRIR TOKENS</a>
{% for c in catalogo %}<div class="card"><h2>{{c.titulo}}</h2><p>Archivo: {{c.archivo}}<br>Dueño: Pedro J. Acobes | Estado: Master Propio</p></div>{% endfor %}</div>
"""

COMPRAR_PAGE = BASE_CSS + """
<div class="top"><h1>ADQUIRIR TOKENS</h1><div class="sub">Lista Soberana — Mercado Propio AcobesChain</div></div>
<div class="wrap">
<div class="box"><span class="paso">1️⃣</span><h3>Elige tu metal</h3><p>AGC Oro $10,000 — ASC Plata $1,000 — AQC Cuarzo $100 — ACC Cobre $10 — ADC Diamante $1 — AC $0.10</p></div>
<div class="box"><span class="paso">2️⃣</span><h3>Reserva tu lugar</h3><p>Llena el formulario. No es una venta automática, es una solicitud de acceso soberano.</p></div>
<div class="box"><span class="paso">3️⃣</span><h3>El Arquitecto te contacta</h3><p>Te confirmamos tu reserva y te damos el paso de acceso a tu wallet AcobesChain.</p></div>
<div class="box"><form method="POST" action="/comprar">
<label>¿Qué token quieres?</label><select name="token"><option>AGC - Oro</option><option>ASC - Plata</option><option>AQC - Cuarzo</option><option>ACC - Cobre</option><option>ADC - Diamante</option><option>AC - Utilidad</option></select>
<label>¿Cuántos quieres reservar?</label><input name="cantidad" type="number" min="1" value="1" required>
<label>Tu nombre</label><input name="nombre" placeholder="Tu nombre completo" required>
<label>Tu email o WhatsApp</label><input name="contacto" placeholder="email o WhatsApp" required>
<button class="boton-gold" style="border:0;width:100%;font-size:18px" type="submit">RESERVAR MI LUGAR EN LA LISTA SOBERANA</button>
</form><p class="tag">Al reservar, solicitas acceso. El Arquitecto confirma disponibilidad y pasos de adquisición.</p></div>
<a class="boton" href="/">VOLVER</a></div>
"""

GRACIAS_PAGE = BASE_CSS + """
<div class="top"><h1>¡RESERVA RECIBIDA!</h1></div>
<div class="wrap"><div class="box"><h2>{{nombre}}, ya estás en la Lista Soberana</h2><p>Token: <b>{{token}}</b> | Cantidad reservada: <b>{{cantidad}}</b><br>Contacto: {{contacto}}<br><br>El Arquitecto te va a contactar para confirmar tu acceso. Guarda esta página.</p></div>
<a class="boton-gold" href="/tokens">VER TOKENS DE NUEVO</a><a class="boton" href="/">VOLVER A LA PUERTA</a></div>
"""

@app.route("/")
def home(): return render_template_string(HOME, decreto=DECRETO)
@app.route("/tokens")
def tokens_page(): return render_template_string(TOKENS_PAGE, tokens=TOKENS, decreto=DECRETO)
@app.route("/catalogo")
def catalogo_page(): return render_template_string(CATALOGO_PAGE, catalogo=CATALOGO)
@app.route("/comprar", methods=["GET","POST"])
def comprar():
    if request.method == "POST":
        d = {"token": request.form.get("token"), "cantidad": request.form.get("cantidad"), "nombre": request.form.get("nombre"), "contacto": request.form.get("contacto"), "hora": datetime.datetime.now().isoformat()}
        RESERVAS.append(d)
        return render_template_string(GRACIAS_PAGE, **d)
    return render_template_string(COMPRAR_PAGE)
@app.route("/api/cadena")
def cadena(): return jsonify({**CADENA, "hora_superficie": datetime.datetime.now().isoformat(), "canales": CANALES, "genesis": GENESIS, "decreto": DECRETO})
@app.route("/api/tokens")
def api_tokens(): return jsonify({"chain_id": GENESIS["chain_id"], "owner": GENESIS["owner"], "tokens": TOKENS, "decreto": DECRETO})
@app.route("/api/catalogo")
def api_catalogo(): return jsonify({"artista": "Pedro J. Acobes", "sello": "Arquitectura Records LLC", "total": len(CATALOGO), "catalogo": CATALOGO})
@app.route("/api/puerta")
def puerta(): return jsonify({"puerta": "ABIERTA", "mensaje": "La puerta de Agarta esta visible en la superficie"})
@app.route("/api/vault")
def vault(): return jsonify({"vault": "ACTIVO", "mensaje": "Vault protegido - solo lectura publica"})
@app.route("/api/reservas")
def reservas(): return jsonify({"total_reservas": len(RESERVAS), "nota": "Lista Soberana privada del Arquitecto"})
@app.route("/health")
def health(): return jsonify({"status": "ok", "cadena": "viva"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

# --- MUSICA EN LA CADENA - AGREGADO SOBERANO ---
from musica import MUSICA_CHAIN, add_play

@app.route("/musica")
def musica_page():
    html = "<h1 style='text-align:center'>MUSICA - ACOBESCHAIN</h1><p style='text-align:center'>Arquitectura Records LLC - Cadena Soberana - Sin Spotify</p>"
    for b in MUSICA_CHAIN:
        d = b["data"]
        html += f"""
        <div style='border:1px solid #00ffcc;padding:15px;margin:10px auto;max-width:600px;background:#111;color:#fff'>
        <b>{d['title']}</b><br>
        Artista: {d['artist']}<br>
        Hash: {d['sha256'][:16]}...<br>
        Bloque: #{b['index']} | Prev: {b['previous_hash'][:8]}...<br>
        Plays REALES en AcobesChain: <b>{d['plays']}</b><br>
        <audio controls style='width:100%;margin-top:10px' onplay="fetch('/api/musica/play/{d['sha256']}',{{method:'POST'}})">
        <source src='/static/{d['file']}'>
        </audio>
        </div>"""
    html += "<p style='text-align:center'><a href='/'>VOLVER A LA PUERTA</a></p>"
    return html

@app.route("/api/musica")
def api_musica():
    return jsonify({"chain": "acobes-mainnet-1", "hub": "https://acobeschain.onrender.com", "total": len(MUSICA_CHAIN), "musica": MUSICA_CHAIN})

@app.route("/api/musica/play/<sha>", methods=["POST"])
def api_play(sha):
    plays = add_play(sha)
    return jsonify({"sha256": sha, "plays": plays, "real": True, "chain": "acobeschain"})
