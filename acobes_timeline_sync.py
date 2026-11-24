import os, json, glob
from acobes_royalty_ledger import inicializar_ledger, registrar_ejecucion_y_minar, calcular_hash_bloque, LEDGER_FILE

CATALOGO_LINEA_TEMPORAL = [
    {"track": "LEGADO_VETERANO_GENESIS.wav", "era": "ERA_VETERANO_ORIGEN", "comando": "COMANDO_RAIZ_VETERANO"},
    {"track": "Eleven.wav", "era": "ERA_TRANSICION_ARQUITECTURA", "comando": "SYNC_ELEVEN"},
    {"track": "Reversa.wav", "era": "ERA_TRANSICION_ARQUITECTURA", "comando": "SYNC_REVERSA"},
    {"track": "Universitaria.wav", "era": "ERA_TRANSICION_ARQUITECTURA", "comando": "SYNC_UNIVERSITARIA"},
    {"track": "No_me_ronquen.wav", "era": "ERA_TRANSICION_ARQUITECTURA", "comando": "SYNC_NO_ME_RONQUEN"},
    {"track": "Lirios_Del_Sur_Corte_Suprema_Master.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "MASTER_CORTE_SUPREMA"},
    {"track": "Lirios_Del_Sur_Decillion_Master.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "MASTER_DECILLION"},
    {"track": "Soberania_Cero.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "EXEC_SOBERANIA_CERO"},
    {"track": "2000_NAVES.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "EXEC_2000_NAVES"},
    {"track": "MASTER_SOVEREIGN.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "EXEC_MASTER_SOVEREIGN"},
    {"track": "BELIEVE_THAT_Master.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "EXEC_BELIEVE_THAT"},
    {"track": "I_AM_ACOBES_Master.wav", "era": "ERA_SOBERANA_ACTUAL", "comando": "EXEC_I_AM_ACOBES"}
]

archivos_locales = glob.glob("*.wav") + glob.glob("*.mp3") + glob.glob("*.flac")
tracks_catalogo = {item["track"] for item in CATALOGO_LINEA_TEMPORAL}

for archivo in sorted(archivos_locales):
    nombre = os.path.basename(archivo)
    if nombre not in tracks_catalogo:
        CATALOGO_LINEA_TEMPORAL.append({
            "track": nombre,
            "era": "ERA_SOBERANA_ACTUAL_DETECTADA",
            "comando": "AUTO_SYNC_" + nombre.upper()
        })

ledger = inicializar_ledger()
registrados = {bloque.get("track") for bloque in ledger.get("chain", [])}
nuevos_bloques = 0

print("==========================================================")
print(" INICIANDO SINCRONIZACION DE LINEA TEMPORAL ACOBES")
print("==========================================================")

for item in CATALOGO_LINEA_TEMPORAL:
    track_name = item["track"]
    era_actual = item["era"]
    cmd_actual = item["comando"]
    if track_name not in registrados:
        registrar_ejecucion_y_minar(track_name, ledger)
        ultimo_bloque = ledger["chain"][-1]
        ultimo_bloque["era_temporal"] = era_actual
        ultimo_bloque["comando_vinculado"] = cmd_actual
        del ultimo_bloque["block_hash"]
        ultimo_bloque["block_hash"] = calcular_hash_bloque(ultimo_bloque)
        nuevos_bloques += 1
        idx = ultimo_bloque["index"]
        minted = ultimo_bloque["tokens_minted"]
        print(f"[+] Bloque #{idx} sellado: {track_name} [{era_actual}] -> {minted} ACOB")
    else:
        print(f"[=] Ya en cadena: {track_name}")

with open(LEDGER_FILE, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=4)

total_bloques = len(ledger["chain"])
total_supply = ledger["total_tokens_supply"]
total_usd = ledger["total_royalty_accrued_usd"]

print("==========================================================")
print(f" Bloques nuevos minados : {nuevos_bloques}")
print(f" Total de bloques       : {total_bloques}")
print(f" Suministro Total ACOB  : {total_supply} ACOB")
print(f" Regalias Acumuladas    : ${total_usd:.2f} USD")
print("==========================================================")
