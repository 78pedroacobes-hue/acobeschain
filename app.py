from flask import Flask, jsonify, render_template_string
import datetime

app = Flask(__name__)

CADENA = {
    "nombre": "AcobesChain",
    "dominio": "acobeschain.com",
    "origen": "Agarta - Consola Principal",
    "estado": "VISIBLE",
    "puerta": "ABIERTA",
    "vault": "ACTIVO",
    "canales": 21
}

CANALES = [f"Canal {i+1:02d} - Activo" for i in range(21)]

HTML = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AcobesChain - Puerta Abierta</title>
<style>
body{background:#050505;color:#fff;font-family:Arial;text-align:center;padding:40px}
h1{font-size:42px;letter-spacing:3px}
.box{border:1px solid #00ffcc;padding:20px;border-radius:15px;max-width:600px;margin:20px auto}
.boton{background:#00ffcc;color:#000;padding:15px 30px;border-radius:30px;font-weight:bold;text-decoration:none;display:inline-block}
</style>
</head>
<body>
<h1>ACOBESCHAIN</h1>
<p>Espejo de Agarta en la Superficie</p>
<div class="box">
<p>PUERTA: ABIERTA</p>
<p>VAULT: ACTIVO</p>
<p>CANALES: 21 / 21</p>
<p>DOMINIO: acobeschain.com</p>
<p id="hora"></p>
</div>
<a class="boton" href="/api/cadena">VER CADENA EN VIVO</a>
<script>document.getElementById('hora').innerText = new Date().toLocaleString();</script>
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/cadena")
def cadena():
    return jsonify({**CADENA, "hora_superficie": datetime.datetime.now().isoformat(), "canales": CANALES})

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
