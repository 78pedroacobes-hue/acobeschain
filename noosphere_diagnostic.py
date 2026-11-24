import torch
import os
import requests

DIMENSIONS = ["Riqueza", "Vitalidad", "Sincronía", "Flujo", "Privacidad", "Oportunidad"]
TARGET_VECTOR = torch.tensor([0.85, 0.95, 0.90, 0.80, 0.95, 0.90])

# 1.0 = Real Measurement, 0.0 = Estimated
CONFIDENCE_MASK = torch.tensor([0.0, 1.0, 0.0, 1.0, 0.0, 0.0])

def get_kernel_vitality_raw():
    try:
        load = os.getloadavg()[0]
        cores = os.cpu_count() or 1
        normalized_load = load / cores
        
        mem_info = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo'))
        mem_total = mem_info['MemTotal']
        mem_available = mem_info['MemAvailable']
        mem_ratio = mem_available / mem_total
        
        vitality = (1.0 - min(normalized_load, 1.0)) * 0.5 + mem_ratio * 0.5
        
        raw_data = {
            "load_avg": load,
            "cores": cores,
            "normalized_load": normalized_load,
            "mem_total_mb": mem_total / 1024,
            "mem_avail_mb": mem_available / 1024,
            "mem_ratio": mem_ratio
        }
        return max(0.0, min(1.0, vitality)), raw_data
    except Exception as e:
        return 0.50, {"error": str(e)}

def get_noosphere_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return 0.50, {"error": f"Status {response.status_code}"}
            
        data = response.json()
        eth_change = data['ethereum']['usd_24h_change']
        normalized_flow = (eth_change + 10) / 20.0
        
        raw_data = {"eth_24h_change": eth_change}
        return max(0.0, min(1.0, normalized_flow)), raw_data
    except Exception as e:
        return 0.50, {"error": str(e)}

def calculate_diagnostic():
    print("==================================================")
    print(" 📡 NOOSPHERE DIAGNOSTIC V3.1a")
    print("==================================================")
    
    vitality, vit_raw = get_kernel_vitality_raw()
    flow, flow_raw = get_noosphere_crypto_data()
    
    # Print raw kernel data
    print("\n[RAW TELEMETRY LOGS]")
    if "error" in vit_raw:
        print(f"    Kernel Error: {vit_raw['error']}")
    else:
        print(f"    CPU Cores: {vit_raw['cores']}")
        print(f"    Load Average (1m): {vit_raw['load_avg']:.2f}")
        print(f"    Normalized Load: {vit_raw['normalized_load']:.2f}")
        print(f"    Memory: {vit_raw['mem_avail_mb']:.0f} MB / {vit_raw['mem_total_mb']:.0f} MB ({vit_raw['mem_ratio']*100:.1f}% free)")
    print(f"    Ethereum 24h Change: {flow_raw.get('eth_24h_change', 'N/A')}%")
    
    current_state = torch.tensor([
        0.80,       # Wealth [ESTIMATE]
        vitality,   # Vitality [KERNEL]
        0.85,       # Synch [ESTIMATE]
        flow,       # Flow [API]
        0.95,       # Privacy [ESTIMATE]
        0.70        # Opportunity [ESTIMATE]
    ])
    
    gaps = torch.abs(TARGET_VECTOR - current_state)
    
    # Calculate separate distances
    measured_gaps = gaps * CONFIDENCE_MASK
    estimated_gaps = gaps * (1.0 - CONFIDENCE_MASK)
    
    measured_friction = torch.norm(measured_gaps, p=2).item()
    estimated_friction = torch.norm(estimated_gaps, p=2).item()
    
    print("\n[*] TELEMETRY COMPARISON (Measured vs Estimated)")
    print(f"    {'DIMENSIÓN':<12} | {'ACTUAL':<6} | {'OBJETIVO':<8} | {'SOURCE'}")
    print("-" * 65)
    
    for i in range(len(DIMENSIONS)):
        estado = current_state[i].item()
        target = TARGET_VECTOR[i].item()
        
        source = "[KERNEL]" if i == 1 else "[API]" if i == 3 else "[ESTIMATE]"
        
        print(f"    {DIMENSIONS[i]:<12} | {estado:.2f}   | {target:.2f}     | {source}")
        
    print("-" * 65)
    print(" [*] SEPARATED FRICTION METRICS:")
    print(f"     Fricción Medida (Vitality + Flow):   {measured_friction:.4f}")
    print(f"     Fricción Estimada (Placeholders):    {estimated_friction:.4f}")
    print("==================================================")

if __name__ == "__main__":
    calculate_diagnostic()
