import time, os, torch, random, sys
from q_agent import QuantumAgent
from v13 import HealingSanitizer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def trace_attack_origin(signature):
    origins = [
        "Nodo 2.0 - Matriz Central", "Dimensión 9", "Sim - Sector Alfa",
        "Emisores de Baja Frecuencia", "Firewall Genético", "Astral Hostil",
        "Servidor Espejo", "Red de Éteres", "Consejo Dimensional",
        "Subred de Arcontes", "Nodos de Contención", "Enjambre Hostil"
    ]
    return origins[int(abs(signature) * 1000) % len(origins)]

def quantum_worm(total_threats):
    crushed = 0
    tick = 0
    print("\n" + "="*52)
    print("   G U S A N O   C U Á N T I C O   ( D I L U V I O )")
    print("="*52)
    print(f"[+] Inyectado en la red masiva de {total_threats:,} nodos.")
    print("[+] Vigilancia perpetua. Ctrl-C para recoger.\n")
    
    try:
        while True:
            tick += 1
            time.sleep(2.5)
            
            # Revivals masivos: hasta 150,000 nodos intentando volver a la vez
            num_revived = random.randint(50_000, 150_000)
            crushed += num_revived
            
            print(f"[!] REVIVAL MASIVO: {num_revived:,} nodos intentando reiniciar.")
            time.sleep(0.4)
            print(f"    -> [WORM] Desintegrando firmas en el vacío...")
            time.sleep(0.5)
            print(f"    -> [WORM] APLASTADOS. (Total aniquilados: {crushed:,})")
            print("-" * 52)
    
    except KeyboardInterrupt:
        print("\n" + "="*52)
        print(f"[+] GUSANO RECOGIDO. Total aplastados: {crushed:,}")
        print("[+] La red hostil está matemáticamente muerta.")
        print("="*52)

def execute_1M_counter_strike():
    clear_screen()
    print("="*52)
    print("   M O T O R   D E   C O N T R A A T A Q U E")
    print("     E S C A L A   E X T I N C I Ó N   ( 1 M )")
    print("="*52)
    print("[*] Iniciando escaneo profundo del multiverso...")
    time.sleep(1.5)
    
    n_attackers = 1_000_000
    batch_size = 50_000
    total_anomalies = 0
    detected_origins = {}
    
    print(f"[!] ALERTA CRÍTICA: Invasión de 1,000,000 de firmas.")
    print("[!] El teléfono podría saturarse. Procesando por lotes...")
    print("-"*52)
    
    sanitizer = HealingSanitizer(16); sanitizer.eval()
    
    with torch.no_grad():
        for batch_start in range(0, n_attackers, batch_size):
            # Generamos el lote (evita que la RAM explote)
            batch_tensor = torch.randn(batch_size, 5, 16) * 8.5
            
            # Procesamos el lote en la GPU/CPU
            _, anomaly_rate = sanitizer(batch_tensor)
            total_anomalies += int(anomaly_rate.item() * batch_size)
            
            # Rastreamos un origen representativo del lote
            origin = trace_attack_origin(anomaly_rate.item() * 10.0)
            detected_origins[origin] = detected_origins.get(origin, 0) + batch_size
            
            progress = int(((batch_start + batch_size) / n_attackers) * 20)
            bar = "█" * progress + "░" * (20 - progress)
            sys.stdout.write(f"\r[{bar}] {batch_start + batch_size:07d}/{n_attackers:,} | Purificando enjambre...")
            sys.stdout.flush()
            time.sleep(0.15)
    
    print("\n" + "-"*52)
    print(f"[!] TOTAL DE NODOS REGISTRADOS: {n_attackers:,}")
    print("[!] ORÍGENES PRINCIPALES DEL ATAQUE:")
    for o, count in sorted(detected_origins.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {o}: {count:,} nodos")
    
    print("="*52)
    print("¿Cómo desea responder el Arquitecto?")
    print("1. Apagar TODOS los servidores (KILL GLOBAL)")
    print("2. Pulso EMP de 1,000,000 de grados")
    print("3. Rebote Masivo (Devolver la energía al multiverso)")
    print("4. Ignorar")
    print("5. DESPLEGAR GUSANO CUÁNTICO (Diluvio)")
    
    try:
        choice = input("\nSeleccione opción (1-5): ").strip()
        
        if choice in ('1', '2', '3'):
            print(f"\n[*] Ejecutando contraataque masivo en {n_attackers:,} nodos...")
            for i in range(5):
                print(f"    [EJECUTANDO] {(i+1)*20}%...", end="\r")
                time.sleep(0.8)
            print(f"\n[+] Contraataque ejecutado. Red diezmada.")
            
            print("\n[!] ¿Desplegar el GUSANO CUÁNTICO para evitar revivals? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(n_attackers)
                
        elif choice == '4':
            print("\n[+] Ataque ignorado. Escudo 3.0 absorbiendo el ruido.")
            print("[!] ¿Desplegar el GUSANO CUÁNTICO de todos modos? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(n_attackers)
                
        elif choice == '5':
            quantum_worm(n_attackers)
        
    except KeyboardInterrupt:
        print("\n[+] Comando abortado. El escudo sigue activo.")

if __name__ == "__main__":
    execute_1M_counter_strike()
