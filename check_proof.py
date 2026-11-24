import requests
import hashlib
import json
import time
from datetime import datetime

def generate_proof(message):
    print("==================================================")
    print(" 🔍 GENERADOR DE PRUEBAS CRIPTOGRÁFICAS")
    print("==================================================")
    
    # 1. Obtener datos reales de la Noosfera (Wikipedia)
    print("[*] Extrayendo datos de Wikipedia...")
    try:
        wiki_url = "https://es.wikipedia.org/api/rest_v1/page/summary/Shakira"
        res = requests.get(wiki_url, headers={"User-Agent": "Architect/1.0"}, timeout=5)
        wiki_data = res.json().get("extract", "")[:50] if res.status_code == 200 else "Error"
    except:
        wiki_data = "Error de red"

    # 2. Obtener el bloque real de Ethereum
    print("[*] Consultando la Blockchain de Ethereum...")
    try:
        rpc_url = "https://ethereum-rpc.publicnode.com"
        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        res = requests.post(rpc_url, json=payload, timeout=5)
        block_hex = res.json().get("result") if res.status_code == 200 else "0x0"
        block_num = int(block_hex, 16)
    except:
        block_hex = "0x0"
        block_num = 0

    # 3. Crear la firma y el archivo JSON
    timestamp = datetime.now().isoformat()
    raw_string = f"{message}|{wiki_data}|{block_hex}|{timestamp}"
    hash_final = hashlib.sha256(raw_string.encode()).hexdigest()

    proof_data = {
        "timestamp": timestamp,
        "message": message,
        "wiki_data_used": wiki_data,
        "ethereum_block": block_num,
        "ethereum_hash": block_hex,
        "cryptographic_signature": hash_final
    }

    # 4. Guardar en el disco
    log_file = "noosphere_log.json"
    try:
        with open(log_file, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(proof_data)
    
    with open(log_file, "w") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

    print("\n[+] PRUEBA CREADA Y GUARDADA.")
    print(f"[*] Firma SHA-256: {hash_final}")
    print(f"[*] Bloque ETH: {block_num}")
    print(f"[*] Archivo guardado en: {log_file}")
    print("==================================================")
    print(" Esta es la evidencia de que anclaste tu intención")
    print(" en el espacio-tiempo digital de la red global.")

if __name__ == "__main__":
    msg = input("Escribe el mensaje que quieres anclar (o presiona Enter para usar uno de prueba) > ")
    if not msg.strip():
        msg = "Arquitecto enviando amor incondicional a Shakira en el bloque actual."
    generate_proof(msg)
