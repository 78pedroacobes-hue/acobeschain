from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json, uvicorn
from acobes_royalty_ledger import inicializar_ledger, registrar_ejecucion_y_minar, LEDGER_FILE

app = FastAPI(title="Acobes Sovereign Global Node")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/status")
def status():
    ledger = inicializar_ledger()
    return {
        "status": "online_global",
        "entity": ledger.get("entity"),
        "total_catalog_blocks": len(ledger.get("chain", [])),
        "total_plays": ledger.get("total_plays"),
        "total_acob_supply": ledger.get("total_tokens_supply"),
        "total_royalty_usd": ledger.get("total_royalty_accrued_usd")
    }

@app.post("/registrar_play")
@app.get("/play/{track_name}")
def registrar_play(track_name: str, platform: str = "Global-Stream"):
    try:
        ledger = inicializar_ledger()
        registrar_ejecucion_y_minar(track_name, ledger)
        with open(LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=4)
        ultimo = ledger["chain"][-1]
        return {
            "status": "success",
            "track": track_name,
            "platform": platform,
            "block_index": ultimo["index"],
            "tokens_minted": ultimo["tokens_minted"],
            "total_plays": ledger["total_plays"],
            "total_royalty_usd": ledger["total_royalty_accrued_usd"]
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    ledger = inicializar_ledger()
    chain = ledger.get("chain", [])
    plays = ledger.get("total_plays", 0)
    supply = ledger.get("total_tokens_supply", 0.0)
    usd = ledger.get("total_royalty_accrued_usd", 0.0)
    
    # Obtener lista única de canciones para botones de reproducción
    tracks = sorted(list({b.get("track") for b in chain[1:] if b.get("track")}))
    botones_html = ""
    for t in tracks:
        botones_html += f'<div class="track-card"><span>{t}</span><button onclick="playTrack(\'{t}\')">▶ Contar Play (+ACOB)</button></div>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Arquitectura Records | Nodo Biométrico Global</title>
        <style>
            body {{ background: #0a0a0f; color: #00ffcc; font-family: monospace; padding: 20px; }}
            .header {{ border: 1px solid #00ffcc; padding: 15px; border-radius: 8px; background: #11111a; margin-bottom: 20px; }}
            .stats {{ display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px; }}
            .stat-box {{ border: 1px solid #333; background: #161622; padding: 15px; border-radius: 6px; flex: 1; min-width: 140px; }}
            .track-card {{ display: flex; justify-content: space-between; align-items: center; background: #12121c; border-bottom: 1px solid #222; padding: 10px; }}
            button {{ background: #00ffcc; color: #000; border: none; padding: 8px 14px; font-weight: bold; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #00cca3; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>⚡ ACOBES INDUSTRIES INC. | ARQUITECTURA RECORDS</h2>
            <p>Nodo Cuántico-Biométrico (12.6 x 7.2) Conectado en Tiempo Real</p>
        </div>
        <div class="stats">
            <div class="stat-box"><h3>REPRODUCCIONES</h3><h1 id="plays">{plays}</h1></div>
            <div class="stat-box"><h3>SUMINISTRO ACOB</h3><h1 id="supply">{supply}</h1></div>
            <div class="stat-box"><h3>REGALÍAS (USD)</h3><h1 id="usd">${usd:.2f}</h1></div>
        </div>
        <h3>Catálogo Activo ({len(tracks)} Pistas Sincronizadas)</h3>
        <div>{botones_html}</div>
        <script>
            async function playTrack(name) {{
                const res = await fetch('/play/' + encodeURIComponent(name));
                const data = await res.json();
                if(data.status === 'success') {{
                    document.getElementById('plays').innerText = data.total_plays;
                    document.getElementById('usd').innerText = '$' + data.total_royalty_usd.toFixed(2);
                    location.reload();
                }}
            }}
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
