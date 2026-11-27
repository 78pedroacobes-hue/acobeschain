from flask import Flask, send_from_directory, jsonify
import os, urllib.parse
app = Flask(__name__)
MUSICA_DIR = "/root/musica"

@app.route("/")
def home():
    return """<h1>ACOBESCHAIN VIVA 👑</h1>
    <h2><a href='/radio'>📻 ESCUCHAR ACOBES FM EN VIVO</a></h2>
    <p><a href='/musica'>MUSICA</a> | <a href='/health'>HEALTH</a></p>"""

@app.route("/radio")
def radio():
    files = sorted([f for f in os.listdir(MUSICA_DIR) if f.lower().endswith(".mp3")]) if os.path.exists(MUSICA_DIR) else []
    playlist = [{"title": f, "url": "/audio/" + urllib.parse.quote(f)} for f in files]
    import json
    plist = json.dumps(playlist)
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>ACOBES FM</title></head>
    <body style="background:black;color:#00ffcc;font-family:sans-serif;text-align:center;padding:20px">
    <div style="background:red;color:white;display:inline-block;padding:5px 15px;border-radius:20px">● EN VIVO</div>
    <h1>📻 ACOBES FM</h1>
    <h3>La Emisora del Veterano - Desde Canovanas, PR</h3>
    <p id="now">Dale PLAY, bebe</p>
    <audio id="player" controls autoplay style="width:100%;max-width:500px"></audio><br><br>
    <button onclick="nextSong()" style="font-size:20px;padding:10px 20px;background:#00ffcc;border:none;border-radius:10px">⏭ SIGUIENTE</button>
    <h3>Programacion de Hoy:</h3>
    <div id="lista"></div>
    <script>
    const playlist = {plist};
    let i = 0;
    const player = document.getElementById('player');
    const now = document.getElementById('now');
    const lista = document.getElementById('lista');
    lista.innerHTML = playlist.map((s,idx)=>`<p onclick="playIdx(${{idx}})" style="cursor:pointer">${{idx+1}}. ${{s.title}}</p>`).join('');
    function playIdx(idx){{ i=idx; play(); }}
    function play(){{ if(playlist.length==0){{ now.innerText='No hay musica todavia'; return; }} player.src=playlist[i].url; now.innerText='🔊 SONANDO AHORA: '+playlist[i].title; player.play(); }}
    function nextSong(){{ i=(i+1)%playlist.length; play(); }}
    player.onended = nextSong;
    play();
    </script>
    <p><a href="/musica" style="color:#00ffcc">Ver Musica</a> | <a href="/" style="color:#00ffcc">Volver</a></p>
    <p>Soberanos. Sin Spotify. Sin permiso.</p>
    </body></html>
    """

@app.route("/musica")
def musica_page():
    files = sorted([f for f in os.listdir(MUSICA_DIR) if f.lower().endswith(".mp3")]) if os.path.exists(MUSICA_DIR) else []
    h = "<h1>MUSICA - ACOBESCHAIN</h1><a href='/radio'>📻 IR A LA RADIO</a><br><br>"
    for f in files:
        url = "/audio/" + urllib.parse.quote(f)
        h += f"<div><b>{f}</b><br><audio controls src='{url}'></audio><br><a href='{url}'>Descargar</a></div><br>"
    return h

@app.route("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(MUSICA_DIR, filename, mimetype="audio/mpeg")

@app.route("/api/musica")
def api_musica():
    files = []
    if os.path.exists(MUSICA_DIR):
        for f in sorted(os.listdir(MUSICA_DIR)):
            if f.lower().endswith(".mp3"):
                files.append({{"file": f, "size_mb": round(os.path.getsize(os.path.join(MUSICA_DIR, f))/1024/1024, 2)}})
    return jsonify({{"station": "ACOBES FM", "total": len(files), "musica": files}})

@app.route("/health")
def health():
    return {{"status": "ok", "station": "ACOBES FM VIVA"}}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
