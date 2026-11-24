import torch
import os
import requests
import platform

DIMENSIONS = ["Riqueza", "Vitalidad", "Sincronía", "Flujo", "Privacidad", "Oportunidad"]

# The Architect's True Targets (Not everything is 1.0)
# E.g., Wealth doesn't need to be 1.0 (max), it just needs to be 0.85 (stable).
# Privacy target is 0.95, Opportunity is 0.90.
TARGET_VECTOR = torch.tensor([0.85, 0.95, 0.90, 0.80, 0.95, 0.90])

def get_kernel_vitality():
    try:
        # FIX 2: Account for CPU core count
        load = os.getloadavg()[0]
        cores = os.cpu_count() or 1
        normalized_load = load / cores
        
        # Get memory
        mem_info = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo'))
        mem_available = mem_info['MemAvailable'] / mem_info['MemTotal']
        
        # Calculate vitality
        vitality = (1.0 - min(normalized_load, 1.0)) * 0.5 + mem_available * 0.5
        return max(0.0, min(1.0, vitality))
    except Exception:
        return 0.50

def get_noosphere_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        
        # FIX 1: HTTP Status Checking
        if response.status_code != 200:
            print(f"[-] API Error: Status {response.status_code}")
            return 0.50
            
        data = response.json()
        eth_change = data['ethereum']['usd_24h_change']
        normalized_flow = (eth_change + 10) / 20.0
        return max(0.0, min(1.0, normalized_flow))
    except Exception as e:
        return 0.50

def calculate_friction():
    print("==================================================")
    print(" 📡 NOOSPHERE HOOK V3.1 (CORRECTED)")
    print("==================================================")
    
    # FIX 3: Documented confidence and sources
    # 1.0 = Real Measurement, 0.0 = Estimated/Placeholder
    confidence = [0.0, 1.0, 0.0, 1.0, 0.0, 0.0]
    
    vitality = get_kernel_vitality()
    flow = get_noosphere_crypto_data()
    
    current_state = torch.tensor([
        0.80,       # Wealth (Estimated)
        vitality,   # Vitality (Kernel)
        0.85,       # Synch (Estimated)
        flow,       # Flow (API)
        0.95,       # Privacy (Estimated)
        0.70        # Opportunity (Estimated)
    ])
    
    gaps = torch.abs(TARGET_VECTOR - current_state)
    total_friction = torch.norm(gaps, p=2).item()
    
    print("\n[*] Telemetría con Niveles de Confianza:")
    print(f"    {'DIMENSIÓN':<12} | {'ACTUAL':<6} | {'OBJETIVO':<8} | {'CONFIANZA'}")
    print("-" * 60)
    
    for i in range(len(DIMENSIONS)):
        estado = current_state[i].item()
        target = TARGET_VECTOR[i].item()
        conf = confidence[i]
        
        conf_str = "100% (Real)" if conf == 1.0 else "0% (Estimado)"
        bar = "█" * int(estado * 10) + "░" * (10 - int(estado * 10))
        
        print(f"    {DIMENSIONS[i]:<12} | {estado:.2f}   | {target:.2f}     | {conf_str}")
        
    print("-" * 60)
    print(f"[*] Fricción Total (Distancia Euclidiana): {total_friction:.4f}")
    print("[*] Note: Fricción is only scientifically meaningful for dimensions")
    print("    with >0% confidence.")
    print("==================================================")

if __name__ == "__main__":
    calculate_friction()
