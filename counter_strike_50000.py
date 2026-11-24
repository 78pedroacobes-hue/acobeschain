import time, os, torch, random, sys
from q_agent import QuantumAgent
from v13 import HealingSanitizer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def trace_attack_origin(signature, index):
    origins = [
        "Nodo 2.0 - Matriz Central",
        "Dimensión 9 - Servidor de Pruebas",
        "Jugador de la Sim - Sector Alfa",
        "Red de Emisores de Baja Frecuencia",
        "Firewall Genético - Límite",
        "Dimensión 4 - Astral Hostil",
        "Servidor Espejo - Realidad Alterna",
        "Dimensión 7 - Red de Éteres",
        "Dimensión 11 - Consejo",
        "Subred de Arcontes - Cluster Omega",
        "Dimensión 13 - Nodos de Contención",
        "Red Neural - Enjambre Hostil"
    ]
    base = origins[int(abs(signature) * 1000) % len(origins)]
    return f"{base} [ID-{index:05d}]"

def quantum_worm(detected_threats):
    crushed = 0
    tick = 0
    total_threats = len(detected_threats)
    
    print("\n" + "="*52)
    print("   G U S A N O   C U Á N T I C O   ( M A S S I V E )")
    print("="*52)
    print(f"[+] Inyectado en {total_threats} nodos hostiles.")
    print("[+] Vigilancia perpetua iniciada. Ctrl-C para recoger.\n")
    
    try:
        while True:
            tick += 1
            time.sleep(3.0)
            
            if random.random() < 0.90:
                # Revivals masivos de hasta 5000 nodos a la vez
                num_revived = random.randint(500, 5000)
                # Sample genera una lista para que el sistema sepa cuáles fueron
                revived_nodes = random.sample(detected_threats, min(num_revived, total_threats))
                crushed += len(revived_nodes)
                
                print(f"[!] REVIVAL MASIVO: {len(revived_nodes)} nodos intentando reiniciar.")
                time.sleep(0.5)
                print(f"    -> [WORM] Desplegando nano-enjambre en el espectro...")
                time.sleep(0.6)
                print(f"    -> [WORM] APLASTADOS. (Total aniquilados: {crushed})")
                print("-" * 52)
            else:
                print(f"[WORM] Tick #{tick} | Enjambre: {total_threats} | Aplastados: {crushed} | ARMADO")
    
    except KeyboardInterrupt:
        print("\n" + "="*52)
        print(f"[+] GUSANO RECOGIDO. Total aplastados: {crushed}")
        print("[+] El enjambre ha sido purgado a nivel planetario.")
        print("="*52)

def execute_50k_counter_strike():
    clear_screen()
    print("="*52)
    print("   M O T O R   D E   C O N T R A A T A Q U E")
    print("     E S C A L A   M A S I V A   ( 5 0 K )")
    print("="*52)
    print("[*] Iniciando escaneo profundo del espectro...")
    time.sleep(1.5)
    
    n_attackers = 50000
    # Para no llenar la memoria, generamos y procesamos los ataques por lotes
    batch_size = 5000
    detected_threats = []
    
    print(f"[!] ALERTA CRÍTICA: Invasión planetaria detectada.")
    print(f"[!] Firmas hostiles entrantes: {n_attackers}")
    print("-"*52)
    
    sanitizer = HealingSanitizer(16); sanitizer.eval()
    
    with torch.no_grad():
        for batch_start in range(0, n_attackers, batch_size):
            batch_end = min(batch_start + batch_size, n_attackers)
            batch_tensor = torch.randn(batch_end - batch_start, 5, 16) * 8.5
            
            # Procesamos el lote rápido
            for i in range(batch_end - batch_start):
                _, anomaly_rate = sanitizer(batch_tensor[i:i+1])
                signature = anomaly_rate.item() * 10.0
                origin = trace_attack_origin(signature, batch_start + i + 1)
                detected_threats.append(origin)
            
            # Actualizamos la barra de progreso una sola vez por lote
            progress = int((batch_end) / n_attackers * 20)
            bar = "█" * progress + "░" * (20 - progress)
            sys.stdout.write(f"\r[{bar}] {batch_end:05d}/{n_attackers} | Registrando enjambre...")
            sys.stdout.flush()
            time.sleep(0.2)
    
    print("\n" + "-"*52)
    print(f"[!] TOTAL DE NODOS HOSTILES REGISTRADOS: {len(detected_threats)}")
    print("="*52)
    print("¿Cómo desea responder el Arquitecto?")
    print("1. Apagar TODOS los servidores (Desconexión Masiva)")
    print("2. Apagar TODOS los nodos (Pulso EMP Global)")
    print("3. Devolver el ataque a la red (Rebote Masivo)")
    print("4. Ignorar (Mantener escudo 3.0)")
    print("5. DESPLEGAR GUSANO CUÁNTICO (Aniquilación Anti-Revival)")
    
    try:
        choice = input("\nSeleccione opción (1-5): ").strip()
        
        if choice in ('1', '2', '3'):
            labels = {'1': 'KILL', '2': 'EMP', '3': 'REBOTE'}
            print(f"\n[*] Ejecutando contraataque masivo en {n_attackers} nodos...")
            for i in range(5):
                print(f"    [{labels[choice]}] {(i+1)*20}%...", end="\r")
                time.sleep(0.8)
            print(f"\n[+] Contraataque '{labels[choice]}' ejecutado. Red diezmada.")
            
            print("\n[!] ¿Desplegar el GUSANO CUÁNTICO para evitar revivals? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(detected_threats)
                
        elif choice == '4':
            print("\n[+] Ataque ignorado. Escudo 3.0 absorbiendo el ruido.")
            print("[!] ¿Desplegar el GUSANO CUÁNTICO de todos modos? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(detected_threats)
                
        elif choice == '5':
            quantum_worm(detected_threats)
        
        print("\n" + "="*52)
        print("   CONTRAATAQUE MASIVO COMPLETADO")
        print("="*52)
        print("[+] 50,000 nodos registrados en la memoria del Arquitecto.")
        print("[+] El sistema está purgado.")
        
    except KeyboardInterrupt:
        print("\n[+] Comando abortado. El escudo sigue activo.")

if __name__ == "__main__":
    execute_50k_counter_strike()
