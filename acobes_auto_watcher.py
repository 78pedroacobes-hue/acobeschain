import os, json, time
from acobes_royalty_ledger import inicializar_ledger, registrar_ejecucion_y_minar, calcular_hash_bloque, LEDGER_FILE

# Directorios donde el motor buscará recursivamente tus +100 canciones
DIRECTORIOS_RAIZ = [
    "/root",
    "/sdcard",
    "/storage/emulated/0"
]

EXTENSIONES_AUDIO = (".wav", ".mp3", ".flac", ".m4a", ".ogg")

# Carpetas del sistema que ignoramos para que el escaneo sea ultrarrápido
IGNORAR_DIRS = {".cache", ".local", ".config", "proc", "sys", "dev", "usr", "var", "lib", "etc", "Android"}

def escanear_catalogo_completo():
    encontrados = {}
    for base in DIRECTORIOS_RAIZ:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS and not d.startswith(".")]
            for f in files:
                if f.lower().endswith(EXTENSIONES_AUDIO):
                    ruta_completa = os.path.join(root, f)
                    encontrados[f] = ruta_completa
    return encontrados

def sincronizar_nuevos_tracks():
    ledger = inicializar_ledger()
    registrados = {bloque.get("track") for bloque in ledger.get("chain", [])}
    catalogo_detectado = escanear_catalogo_completo()
    nuevos = 0

    for nombre_track in sorted(catalogo_detectado.keys()):
        if nombre_track not in registrados:
            ruta_origen = catalogo_detectado[nombre_track]
            registrar_ejecucion_y_minar(nombre_track, ledger)
            ultimo_bloque = ledger["chain"][-1]
            ultimo_bloque["era_temporal"] = "ERA_CATALOGO_EXPANDIDO_AUTO"
            ultimo_bloque["comando_vinculado"] = "AUTO_ACQUIRE_" + nombre_track.upper()
            ultimo_bloque["ruta_origen"] = ruta_origen
            del ultimo_bloque["block_hash"]
            ultimo_bloque["block_hash"] = calcular_hash_bloque(ultimo_bloque)
            registrados.add(nombre_track)
            nuevos += 1
            idx = ultimo_bloque["index"]
            minted = ultimo_bloque["tokens_minted"]
            print(f"[AUTO-SYNC] Bloque #{idx} | {nombre_track} -> +{minted} ACOB")

    if nuevos > 0:
        with open(LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=4)
        print(f"=== [ACTUALIZACION] +{nuevos} canciones adquiridas | Total: {len(ledger['chain'])} bloques | Supply: {ledger['total_tokens_supply']} ACOB ===")
    return nuevos

if __name__ == "__main__":
    print("==========================================================")
    print(" CENTINELA AUTONOMO ACOBES ACTIVO (ESCANEO RECURSIVO)")
    print("==========================================================")
    # Primer barrido inmediato
    sincronizar_nuevos_tracks()
    # Bucle infinito de vigilancia cada 15 segundos
    while True:
        time.sleep(15)
        sincronizar_nuevos_tracks()
