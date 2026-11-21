from flask import Flask, send_from_directory, jsonify
import os
app = Flask(__name__)
MUSICA_DIR = "/root/musica"

MUSICA = [
    {"title": "Sunblock", "file": "Sunblock.mp3"},
    {"title": "El Arquitecto (4)", "file": "El Arquitecto (4).mp3"},
    {"title": "Reescribo la Realidad (Remix)", "file": "Reescribo la Realidad (Remix).mp3"},
    {"title": "Relacion Conmigo Mismo", "file": "Relación Conmigo Mismo.mp3"},
    {"title": "Elon y Trump", "file": "Elon y Trump.mp3"},
]

@app.route("/")
def home():
    return "<h1>ACOBESCHAIN VIVA</h1><p><a href='/musica'>MUSICA</a> | <a href='/health'>HEALTH</a></p>"

@app.route("/musica")
@app.route("/música")
def musica_page():
    h = "<h1>MUSICA - ACOBESCHAIN - PEDRO ACOBES</h1><a href='/'>VOLVER</a><br><br>"
    for m in MUSICA:
        # url encode spaces
        import urllib.parse
        url = "/audio/" + urllib.parse.quote(m['file'])
        h += f"<div style='border:1px solid #00ffcc;padding:15px;margin:10px'><b>{m['title']}</b><br><audio controls src='{url}' style='width:100%'></audio><br><a href='{url}'>Descargar</a></div>"
    return h

@app.route("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(MUSICA_DIR, filename)

@app.route("/api/musica")
def api_musica():
    files = []
    for f in os.listdir(MUSICA_DIR):
        if f.endswith(".mp3"):
            files.append({"file": f, "size_mb": round(os.path.getsize(os.path.join(MUSICA_DIR, f))/1024/1024, 2)})
    return jsonify({"chain": "acobes-mainnet-1", "total": len(files), "musica": files})

@app.route("/health")
def health():
    return {"status": "ok", "cadena": "viva", "musica_files": len(os.listdir(MUSICA_DIR)) if os.path.exists(MUSICA_DIR) else 0}
