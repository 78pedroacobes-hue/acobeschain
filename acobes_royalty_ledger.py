import os, json, time, hashlib
from acobes_engine import SovereignQuantumCNN, AudioBridgeSynthesizer

LEDGER_FILE = "acobes_blockchain_ledger.json"
CREATOR = "Pedro J. Acobes | Acobes Industries Inc. / Bio-Quantum Department"
TOKEN_SYMBOL = "ACOB"
ROYALTY_RATE_USD = 0.05

def calcular_hash_bloque(bloque: dict) -> str:
    contenido = json.dumps(bloque, sort_keys=True).encode("utf-8")
    return hashlib.sha256(contenido).hexdigest()

def inicializar_ledger() -> dict:
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r", encoding="utf-8") as f: return json.load(f)
    genesis = {
        "index": 0, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "track": "GENESIS_BLOCK_BIOMIMETIC", "creator": CREATOR, "quantum_signature": [0.0, 0.0],
        "biometrics": {"largo": 12.6, "ancho": 7.2},
        "tokens_minted": 0.0, "royalty_accrued_usd": 0.0, "prev_hash": "0"*64
    }
    genesis["block_hash"] = calcular_hash_bloque(genesis)
    ledger = {"entity": CREATOR, "token": TOKEN_SYMBOL, "total_plays": 0, "total_tokens_supply": 0.0, "total_royalty_accrued_usd": 0.0, "chain": [genesis]}
    with open(LEDGER_FILE, "w", encoding="utf-8") as f: json.dump(ledger, f, indent=4)
    return ledger

def registrar_ejecucion_y_minar(wav_path: str, ledger: dict):
    model = SovereignQuantumCNN()
    synth = AudioBridgeSynthesizer(model)
    info = synth.extract_quantum_signature(wav_path)
    sig = [round(x, 5) for x in info["signature_vector"]]
    densidad = info["spectral_density"]
    tokens_emitidos = round(1.0 + (densidad * 12.6), 4)
    prev_block = ledger["chain"][-1]
    nuevo_bloque = {
        "index": prev_block["index"] + 1, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "track": wav_path, "creator": CREATOR, "quantum_signature": sig,
        "biometrics_ratio": info["celular_ratio"], "spectral_density": round(densidad, 6),
        "tokens_minted": tokens_emitidos, "royalty_accrued_usd": ROYALTY_RATE_USD, "prev_hash": prev_block["block_hash"]
    }
    nuevo_bloque["block_hash"] = calcular_hash_bloque(nuevo_bloque)
    ledger["chain"].append(nuevo_bloque)
    ledger["total_plays"] += 1
    ledger["total_tokens_supply"] = round(ledger["total_tokens_supply"] + tokens_emitidos, 4)
    ledger["total_royalty_accrued_usd"] = round(ledger["total_royalty_accrued_usd"] + ROYALTY_RATE_USD, 2)
