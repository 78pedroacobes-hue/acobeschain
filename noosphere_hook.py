import torch
import time
import os
import requests
import json

# =====================================================================
# PIPELINE DE OBSERVACIÓN V3: NOOSFERA Y CORE KERNEL
# =====================================================================

DIMENSIONS = ["Riqueza", "Vitalidad", "Sincronía", "Flujo", "Privacidad", "Oportunidad"]

def get_kernel_vitality():
    """
    Lee el Core Kernel de Linux para medir la 'Vitalidad' real del hardware.
    Si el CPU está al 100% o la memoria está llena, la vitalidad baja.
    """
    try:
        # Carga del sistema (Load Average de 1 minuto)
        load = os.getloadavg()[0]
        # Memoria RAM disponible
        mem_info = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo'))
        mem_available = mem_info['MemAvailable'] / mem_info['MemTotal']
        
        # Calculamos una vitalidad del 0.0 al 1.0
        # A menor carga y más memoria, mayor vitalidad.
        vitality = (1.0 - min(load / 8.0, 1.0)) * 0.5 + mem_available * 0.5
        return max(0.0, min(1.0, vitality))
    except Exception:
        return 0.50 # Fallback

def get_noosphere_crypto_data():
    """
    Consulta la Noosfera (API pública de CoinGecko) para obtener el estado real del mercado.
    Usamos el precio de Ethereum como métrica de Flujo/Riqueza.
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Extraemos el cambio del 24h de Ethereum
        eth_change = data['ethereum']['usd_24h_change']
        
        # Normalizamos el cambio: Si el mercado sube, el flujo está alto.
        # (Un cambio del +10% se mapea a 1.0, un -10% se mapea a 0.0)
        normalized_flow = (eth_change + 10) / 20.0
        return max(0.0, min(1.0, normalized_flow))
    except Exception as e:
        print(f"[-] Error conectando a la Noosfera: {e}")
        return 0.50 # Fallback

def get_real_observations():
    print("[*] Conectando al Core Kernel (Hardware)...")
    vitality = get_kernel_vitality()
    
    print("[*] Consultando la Noosfera (Red Web3)...")
    flow = get_noosphere_crypto_data()
    
    # Las demás dimensiones requieren APIs privadas (Bancos, Email, etc.)
    # Por ahora, usamos marcadores para demostrar la mezcla de datos.
    print("[*] Mapeando telemetría a las 6 dimensiones...")
    
    current_state = torch.tensor([
        0.80,       # Riqueza (Requiere API bancaria real)
        vitality,   # Vitalidad (¡REAL! Leído del Kernel)
        0.85,       # Sincronía (Requiere análisis de sentimiento)
        flow,       # Flujo (¡REAL! Leído de la Noosfera)
        0.95,       # Privacidad (Requiere auditoría de red)
        0.70        # Oportunidad (Requiere API de calendario)
    ])
    
    return current_state

def calculate_friction():
    print("==================================================")
    print(" 📡 NOOSPHERE KERNEL HOOK (TELEMETRÍA REAL)")
    print("==================================================")
    
    current_state = get_real_observations()
    
    # El Target ya no es un número aleatorio. Es el 100% de alineación.
    # En la física del Arquitecto, el objetivo es siempre la optimización máxima.
    target_vector = torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    
    gaps = torch.abs(target_vector - current_state)
    total_friction = torch.norm(gaps, p=2).item()
    
    print("\n[*] Telemetría del Nodo Físico y la Noosfera:")
    print(f"    {'DIMENSIÓN':<12} | {'ESTADO ACTUAL':<14} | {'ALINEACIÓN'}")
    print("-" * 60)
    
    for i in range(len(DIMENSIONS)):
        estado = current_state[i].item()
        # Mostramos si el dato es real o un placeholder
        fuente = "(Kernel)" if i == 1 else "(Web3)" if i == 3 else "(Estimado)"
        
        bar = "█" * int(estado * 10) + "░" * (10 - int(estado * 10))
        print(f"    {DIMENSIONS[i]:<12} | [{bar}] {estado:.2f} {fuente}")
        
    print("-" * 60)
    print(f"[*] Fricción Total (Distancia Euclidiana): {total_friction:.4f}")
    print("    (Nota: > 2.0 significa alta inestabilidad en el Kernel/Noosfera)")
    print("==================================================")

if __name__ == "__main__":
    calculate_friction()
