# MUSICA - Bloques de musica para AcobesChain en Render
# No es Spotify. Es nuestra cadena.
import hashlib, time

MUSICA_CHAIN = []

def hash_music_block(block):
    return hashlib.sha256(str(block).encode()).hexdigest()

def add_music_to_chain(title, filename, sha256, ipfs="sovereign://acobeschain"):
    last = MUSICA_CHAIN[-1] if MUSICA_CHAIN else {"hash": "0"}
    block = {
        "index": len(MUSICA_CHAIN),
        "timestamp": time.time(),
        "previous_hash": last["hash"],
        "type": "MUSIC",
        "data": {
            "title": title,
            "artist": "Acobes \"El Arquitecto\"",
            "owner": "Pedro J. Acobes - Arquitectura Records LLC",
            "file": filename,
            "sha256": sha256,
            "ipfs": ipfs,
            "plays": 0,
            "chain": "acobeschain-mainnet-1",
            "hub": "https://acobeschain.onrender.com"
        }
    }
    block["hash"] = hash_music_block(block)
    MUSICA_CHAIN.append(block)
    return block

def add_play(song_sha256):
    for b in MUSICA_CHAIN:
        if b["data"]["sha256"] == song_sha256:
            b["data"]["plays"] += 1
            return b["data"]["plays"]
    return 0

# Tus primeros 3 bloques de musica - para probar el Hub
# Cuando tengas el sha256 real de tus MP3, lo cambias aqui
add_music_to_chain("Apocalipsis 13", "Apocalipsis_13.mp3", "pendiente-calcular-sha256")
add_music_to_chain("Lirios Del Sur - Corte Suprema Master", "Lirios_Del_Sur_Corte_Suprema_Master.wav", "pendiente-calcular-sha256")
add_music_to_chain("No Me Ronquen", "No_me_ronquen.wav", "pendiente-calcular-sha256")
