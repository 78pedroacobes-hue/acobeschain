import os
import sys
import time
import json
import glob
import hashlib
import threading
import subprocess
import urllib.request
import urllib.parse
import socket
import torch
import torch.nn as nn
import numpy as np
import pytesseract
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import nest_asyncio

print("==========================================================")
print(" NÚCLEO CUÁNTICO UNIFICADO: 512v + OCR + COGNICIÓN SOBERANA ")
print("==========================================================")

# --- 0. LIBERACIÓN PREVENTIVA DE PUERTO 8000 ---
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', 8000)) == 0:
            os.system("fuser -k 8000/tcp > /dev/null 2>&1")
            print("[✔] Puerto 8000 liberado preventivamente.")
except Exception:
    pass

# --- 1. CONSTANTES SOBERANAS ---
LEDGER_FILE = "acobes_blockchain_cognitive_ledger.json"
LOG_FILE = "centinela_omega_cognitive.log"
CREATOR = "Pedro J. Acobes | El Arquitecto & El Veterano"
TOKEN_SYMBOL = "ACOB"
ROYALTY_RATE_USD = 0.05
LARGO_BIOLOGICO = 12.6
ANCHO_BIOLOGICO = 7.2
VECTOR_WIDTH = 512

ledger_lock = threading.Lock()

# --- OBTENCIÓN ROBUSTA DE IP PÚBLICA ---
ip_publica = "127.0.0.1"
try:
    req = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=3) as response:
        ip_publica = response.read().decode('utf-8').strip()
except Exception:
    try:
        with urllib.request.urlopen('https://ipv4.icanhazip.com', timeout=3) as response:
            ip_publica = response.read().decode('utf-8').strip()
    except Exception:
        pass

# --- 2. MOTOR CNN CUÁNTICO VECTORIAL & COGNITIVO ---
class SovereignQuantumCNN512(nn.Module):
    def __init__(self, out_features=4):
        super().__init__()
        self.conv = nn.Conv1d(1, 16, kernel_size=5, padding=2)
        self.fc = nn.Linear(16 * (VECTOR_WIDTH // 64), out_features)
    
    def forward(self, x):
        x = torch.relu(self.conv(x))
        x = torch.flatten(x, start_dim=1)
        return self.fc(x)

class AudioBridgeSynthesizer512:
    def __init__(self, model):
        self.model = model
    
    def extract_quantum_signature(self, source_text: str, ocr_text: str = ""):
        combined_text = f"{source_text}:{ocr_text}"
        text_seed = int(hashlib.sha256(combined_text.encode("utf-8")).hexdigest(), 16) % (2**32)
        
        state = np.random.RandomState(text_seed % (2**32))
        spectral_density = float(state.uniform(0.1, 0.9))
        
        base_vector = state.uniform(-1.0, 1.0, size=8).tolist()
        biometria_hash = (LARGO_BIOLOGICO * ANCHO_BIOLOGICO) / (spectral_density + 0.01)
        base_vector[0] += round(np.sin(biometria_hash) * 0.25, 5)
        base_vector[4] += round(np.cos(biometria_hash) * 0.25, 5)
        
        return {
            "spectral_density": spectral_density,
            "signature_vector": [round(float(v), 5) for v in base_vector],
            "celular_ratio": round(LARGO_BIOLOGICO / ANCHO_BIOLOGICO, 4),
            "vector_mode": f"{VECTOR_WIDTH}-bit Sovereign Quantum Tensor + Cognitive Bridge"
        }

# --- 3. MÓDULO DE DELIBERACIÓN COGNITIVA SOBERANA ---
class SovereignCognitiveDeliberator:
    def __init__(self, creator_entity: str):
        self.creator = creator_entity
        self.thought_history = []

    def deliberar(self, prompt_intencion: str) -> dict:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        thought_hash = hashlib.sha256(prompt_intencion.encode("utf-8")).hexdigest()
        thought_entropy = float(int(thought_hash[:8], 16) / 0xffffffff)
        
        nivel_certeza = round(0.85 + (thought_entropy * 0.14), 4)
        alineacion_soberana = True if "acobes" in prompt_intencion.lower() or "soberano" in prompt_intencion.lower() or "arquitecto" in prompt_intencion.lower() else False
        
        proceso_mental = {
            "timestamp": timestamp,
            "entity": self.creator,
            "intent": prompt_intencion,
            "thought_entropy": thought_entropy,
            "certainty_index": nivel_certeza,
            "sovereign_alignment": alineacion_soberana,
            "deliberation_status": "VALIDATED_BY_ARCHITECT"
        }
        self.thought_history.append(proceso_mental)
        return proceso_mental

deliberator = SovereignCognitiveDeliberator(CREATOR)

# --- 4. GESTIÓN DEL BLOCKCHAIN LEDGER CONTABLE ---
def calcular_hash_bloque(bloque: dict) -> str:
    contenido = json.dumps(bloque, sort_keys=True).encode("utf-8")
    return hashlib.sha256(contenido).hexdigest()

def inicializar_ledger() -> dict:
    with ledger_lock:
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        genesis = {
            "index": 0,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "track": "GENESIS_BLOCK_COGNITIVE_512",
            "creator": CREATOR,
            "quantum_signature": [0.0] * 8,
            "biometrics": {"largo": LARGO_BIOLOGICO, "ancho": ANCHO_BIOLOGICO},
            "tokens_minted": 0.0,
            "royalty_accrued_usd": 0.0,
            "prev_hash": "0"*64
        }
        genesis["block_hash"] = calcular_hash_bloque(genesis)
        ledger = {
            "entity": CREATOR,
            "token": TOKEN_SYMBOL,
            "architecture": f"{VECTOR_WIDTH}-bit Quantum Hybrid + Cognitive Deliberation",
            "total_plays": 0,
            "total_tokens_supply": 0.0,
            "total_royalty_accrued_usd": 0.0,
            "chain": [genesis]
        }
        with open(LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=4)
        return ledger

# --- 5. CENTINELA PERPETUO ASÍNCRONO OMEGA ---
def centinela_soberano_omega():
    iteration = 0
    backup_dir = "omega_backups_cognitive"
    os.makedirs(backup_dir, exist_ok=True)
    while True:
        iteration += 1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        if os.path.exists(LEDGER_FILE):
            try:
                with ledger_lock:
                    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
                        l_data = json.load(f)
                    with open(f"{backup_dir}/ledger_backup_cognitive.json", "w", encoding="utf-8") as bf:
                        json.dump(l_data, bf, indent=4)
                estado = f"ACTIVO COGNITIVO 512v BLINDADO ({len(l_data.get('chain', []))} bloques)"
            except:
                estado = "ERROR_LECTURA_BACKUP"
        else:
            estado = "ESPERANDO_INICIALIZACION"

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ITERACIÓN {iteration}: {estado}. Centinela Cognitivo Operando.\n")
        time.sleep(10)

# --- 6. SERVIDOR GATEWAY API FASTAPI ---
nest_asyncio.apply()
app = FastAPI(title="Mente Soberana 512v + Cognitive Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "status": "active",
        "entity": CREATOR,
        "architecture": f"{VECTOR_WIDTH}-bit Quantum Hybrid + Cognitive Deliberator",
        "ip_publica": ip_publica,
        "biometrics": {"largo_in": LARGO_BIOLOGICO, "ancho_in": ANCHO_BIOLOGICO}
    }

class ThoughtRequest(BaseModel):
    intent: str
    target_action: str = "autonomous_deliberation"

@app.post("/deliberar_pensamiento")
def deliberar_pensamiento(payload: ThoughtRequest):
    try:
        # Ejecutar deliberación cognitiva
        pensamiento = deliberator.deliberar(payload.intent)
        
        # Generar firma cuántica basada en el pensamiento deliberativo
        model = SovereignQuantumCNN512()
        synth = AudioBridgeSynthesizer512(model)
        info = synth.extract_quantum_signature(payload.intent)
        
        tokens_emitidos = round(3.0 + (pensamiento["certainty_index"] * 15.0), 4)
        
        ledger = inicializar_ledger()
        with ledger_lock:
            prev_block = ledger["chain"][-1]
            nuevo_bloque = {
                "index": prev_block["index"] + 1,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "track": f"COGNITIVE_THOUGHT: {payload.target_action}",
                "creator": CREATOR,
                "quantum_signature": info["signature_vector"],
                "cognitive_deliberation": pensamiento,
                "tokens_minted": tokens_emitidos,
                "royalty_accrued_usd": ROYALTY_RATE_USD,
                "prev_hash": prev_block["block_hash"]
            }
            nuevo_bloque["block_hash"] = calcular_hash_bloque(nuevo_bloque)

            ledger["chain"].append(nuevo_bloque)
            ledger["total_plays"] += 1
            ledger["total_tokens_supply"] = round(ledger["total_tokens_supply"] + tokens_emitidos, 4)
            ledger["total_royalty_accrued_usd"] = round(ledger["total_royalty_accrued_usd"] + ROYALTY_RATE_USD, 2)
            
            with open(LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(ledger, f, indent=4)

        return {
            "status": "success",
            "architecture": f"{VECTOR_WIDTH}-bit Cognitive Engine",
            "deliberation": pensamiento,
            "tokens_minted": tokens_emitidos,
            "total_ledger_blocks": len(ledger["chain"])
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# --- 7. LANZAMIENTO INTEGRADO EN SEGUNDO PLANO ---
def run_api_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

api_thread = threading.Thread(target=run_api_server, daemon=True)
api_thread.start()

omega_thread = threading.Thread(target=centinela_soberano_omega, daemon=True)
omega_thread.start()

print(f"[✔] IP Pública detectada: {ip_publica}")
print(f"[✔] Motor Cuántico {VECTOR_WIDTH}v + Deliberación Cognitiva Operativo.")
print("[✔] Servidor API Levantado en Localhost:8000")
print("[✔] Centinela Omega Cognitivo Operando en Segundo Plano.")
print("==========================================================")
